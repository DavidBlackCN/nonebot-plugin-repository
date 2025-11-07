from nonebot import on_command, get_bot, require
from nonebot.adapters import Message
from nonebot.params import CommandArg, Event
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent
import httpx
import json
from datetime import datetime
import asyncio

# 导入配置
from .config import config

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

__plugin_meta__ = PluginMetadata(
    name="60秒新闻",
    description="获取每日60秒新闻图片，支持定时发送",
    usage=f"输入'{config.sixty_seconds_command}'获取当日新闻图片",
    type="application",
    homepage="https://github.com/your-repo/your-plugin",
    supported_adapters={"onebot.v11"},
)

# 使用配置中的命令和别名
sixty_seconds = on_command(
    config.sixty_seconds_command, 
    aliases=set(config.sixty_seconds_aliases),  
    priority=10, 
    block=True
)

# 存储所有已知的群组ID
known_groups = set()

async def get_news_image():
    """从API获取新闻图片URL"""
    try:
        # 发送HTTP请求获取数据
        async with httpx.AsyncClient() as client:
            response = await client.get(config.api_url, timeout=config.api_timeout)
            response.raise_for_status()
            data = response.json()
        
        # 检查API响应状态
        if data.get("code") != 200:
            return None, f"获取新闻失败: {data.get('message', '未知错误')}"
        
        # 从字段中获取图片URL
        if data.get("image"):
            return data["image"], None
        else:
            return None, "API返回数据中没有找到图片链接"
        
    except httpx.TimeoutException:
        return None, "请求超时，请稍后再试"
    except httpx.RequestError as e:
        return None, f"网络请求错误: {e}"
    except json.JSONDecodeError:
        return None, "解析API响应失败"
    except Exception as e:
        return None, f"获取新闻时发生错误: {e}"

@sixty_seconds.handle()
async def handle_sixty_seconds(event: Event, args: Message = CommandArg()):
    """处理60秒命令"""
    # 获取图片URL
    image_url, error = await get_news_image()
    
    if error:
        await sixty_seconds.finish(error)
    
    # 发送图片
    await sixty_seconds.send(MessageSegment.image(image_url))
    
    # 记录群组ID（如果是群消息）
    if isinstance(event, GroupMessageEvent):
        known_groups.add(event.group_id)
        print(f"记录群组ID: {event.group_id}")

@scheduler.scheduled_job("cron", hour=config.scheduled_hour, minute=config.scheduled_minute, id="morning_news")
async def scheduled_morning_news():
    """定时发送新闻到所有群组"""
    # 获取当日新闻图片
    image_url, error = await get_news_image()
    
    if error:
        print(f"定时发送新闻失败: {error}")
        return
    
    # 获取bot实例
    try:
        bot = get_bot()
    except Exception as e:
        print(f"获取bot实例失败: {e}")
        return
    
    # 如果没有已知群组，尝试获取所有群组
    if not known_groups:
        try:
            groups = await bot.get_group_list()
            for group in groups:
                known_groups.add(group["group_id"])
            print(f"从bot获取到 {len(known_groups)} 个群组")
        except Exception as e:
            print(f"获取群组列表失败: {e}")
            return
    
    # 向所有群组发送新闻
    success_count = 0
    for group_id in known_groups:
        try:
            await bot.send_group_msg(
                group_id=group_id,
                message=MessageSegment.text("早上好！今日60秒新闻：\n") + MessageSegment.image(image_url)
            )
            success_count += 1
            # 避免发送过快被限制
            await asyncio.sleep(config.send_delay)
        except Exception as e:
            print(f"向群组 {group_id} 发送新闻失败: {e}")
            # 如果发送失败，可能是机器人不在该群，从列表中移除
            known_groups.discard(group_id)
    
    print(f"定时新闻发送完成，成功发送到 {success_count} 个群组")

# 当机器人加入新群时，记录群ID
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent

@on_command("", rule=lambda: True).handle()
async def handle_group_increase(event: GroupIncreaseNoticeEvent):
    """处理机器人加入群组事件"""
    if event.user_id == event.self_id:
        known_groups.add(event.group_id)
        print(f"已加入新群组: {event.group_id}，已添加到发送列表")

# 当机器人被踢出群时，移除群ID
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent

@on_command("", rule=lambda: True).handle()
async def handle_group_decrease(event: GroupDecreaseNoticeEvent):
    """处理机器人退出群组事件"""
    if event.user_id == event.self_id:
        known_groups.discard(event.group_id)
        print(f"已退出群组: {event.group_id}，已从发送列表移除")