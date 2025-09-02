import nonebot
from nonebot import require, get_bot, get_driver
from nonebot.plugin import on_command, PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger
import httpx
import asyncio
from datetime import datetime, time
from typing import List, Dict, Any, Set

# 导入配置
from .config import (
    greeting_scheduler_times,
    greeting_blacklist_groups,
    image_api_url,
    request_timeout,
    morning_message,
    evening_message
)

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

# 获取 driver
driver = get_driver()

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="定时问候图片插件",
    description="定时在群内发送早安/晚安消息和图片",
    usage="配置定时时间和不需要发送的群号后自动运行",
    type="application",
    config=None,
)

# 存储命令和状态
greeting_status = on_command("问候状态", aliases={"greeting_status"}, priority=5, block=True)

# 将黑名单转换为集合以便快速查找
blacklist_set = set(greeting_blacklist_groups)

async def fetch_image() -> bytes:
    """从API获取图片"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_api_url, timeout=request_timeout)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"图片API请求失败，状态码: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"获取图片时发生错误: {e}")
        return None

async def send_greeting(group_id: int):
    """发送问候消息和图片到指定群"""
    # 检查是否在黑名单中
    if group_id in blacklist_set:
        logger.info(f"群 {group_id} 在黑名单中，跳过发送")
        return
    
    # 获取当前时间判断是早安还是晚安
    now = datetime.now().time()
    noon = time(12, 0)
    
    # 获取问候消息
    greeting_text = morning_message if now < noon else evening_message
    
    # 获取图片
    image_data = await fetch_image()
    if not image_data:
        logger.error("获取图片失败，跳过发送")
        return
    
    # 构造消息
    message = Message([
        MessageSegment.text(f"{greeting_text}\n"),
        MessageSegment.image(image_data)
    ])
    
    # 发送消息
    try:
        bot = get_bot()
        await bot.send_group_msg(group_id=group_id, message=message)
        logger.info(f"已向群 {group_id} 发送问候消息")
    except Exception as e:
        logger.error(f"向群 {group_id} 发送消息失败: {e}")

async def get_all_groups() -> List[int]:
    """获取机器人加入的所有群组"""
    try:
        bot = get_bot()
        group_list = await bot.get_group_list()
        return [group["group_id"] for group in group_list]
    except Exception as e:
        logger.error(f"获取群组列表失败: {e}")
        return []

async def send_greetings_to_all_groups():
    """向所有群发送问候（除了黑名单中的群）"""
    # 获取所有群组
    all_groups = await get_all_groups()
    if not all_groups:
        logger.error("无法获取群组列表，跳过发送")
        return
    
    # 过滤黑名单群组
    target_groups = [gid for gid in all_groups if gid not in blacklist_set]
    
    if not target_groups:
        logger.warning("没有可发送的群组")
        return
    
    logger.info(f"准备向 {len(target_groups)} 个群发送问候消息")
    
    # 向所有目标群发送消息
    for group_id in target_groups:
        await send_greeting(group_id)
        # 避免发送过快，间隔1秒
        await asyncio.sleep(1)

def setup_scheduler():
    """设置定时任务"""
    if not greeting_scheduler_times:
        logger.warning("未配置定时时间，插件将不会执行")
        return
    
    # 为每个配置的时间创建定时任务
    for time_str in greeting_scheduler_times:
        try:
            # 解析时间字符串
            hour, minute = map(int, time_str.split(':'))
            
            # 添加定时任务
            scheduler.add_job(
                send_greetings_to_all_groups,
                'cron',
                hour=hour,
                minute=minute,
                id=f"greeting_{time_str}",
                replace_existing=True
            )
            logger.info(f"已创建定时任务: {time_str}")
        except ValueError:
            logger.error(f"时间格式错误: {time_str}，请使用HH:MM格式")
        except Exception as e:
            logger.error(f"创建定时任务失败: {e}")

@greeting_status.handle()
async def handle_greeting_status():
    """处理问候状态查询命令"""
    if not greeting_scheduler_times:
        await greeting_status.finish("未配置定时任务")
    
    times = ", ".join(greeting_scheduler_times)
    blacklist = ", ".join(map(str, greeting_blacklist_groups))
    message = f"定时问候任务配置:\n时间: {times}\n黑名单群组: {blacklist}"
    await greeting_status.finish(message)

# 驱动加载时设置定时任务
@driver.on_startup
async def _():
    setup_scheduler()

# 驱动卸载时清理定时任务
@driver.on_shutdown
async def _():
    # 移除所有本插件的定时任务
    for job in scheduler.get_jobs():
        if job.id.startswith("greeting_"):
            scheduler.remove_job(job.id)
    logger.info("已清理所有定时问候任务")