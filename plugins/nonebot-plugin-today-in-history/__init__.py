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
    name="历史上的今天",
    description="获取历史上的今天事件，支持定时发送",
    usage=f"输入'{config.history_command}'获取历史上的今天事件",
    type="application",
    homepage="https://github.com/your-repo/your-plugin",
    supported_adapters={"onebot.v11"},
)

# 使用配置中的命令和别名
history_today = on_command(
    config.history_command, 
    aliases=set(config.history_aliases),  
    priority=10, 
    block=True
)

# 存储所有已知的群组ID
known_groups = set()

async def get_history_events():
    """从API获取历史上的今天事件"""
    try:
        # 发送HTTP请求获取数据
        async with httpx.AsyncClient() as client:
            response = await client.get(config.api_url, timeout=config.api_timeout)
            response.raise_for_status()
            data = response.json()
        
        # 检查API响应状态
        if data.get("code") != 200:
            return None, f"获取历史事件失败: {data.get('message', '未知错误')}"
        
        # 从data字段中获取历史事件
        if data.get("data"):
            return data["data"], None
        else:
            return None, "API返回数据中没有找到历史事件"
        
    except httpx.TimeoutException:
        return None, "请求超时，请稍后再试"
    except httpx.RequestError as e:
        return None, f"网络请求错误: {e}"
    except json.JSONDecodeError:
        return None, "解析API响应失败"
    except Exception as e:
        return None, f"获取历史事件时发生错误: {e}"

def format_history_message(history_data):
    """格式化历史事件消息"""
    date_str = history_data.get("date", "未知日期")
    items = history_data.get("items", [])
    
    message = f"📜 历史上的今天 ({date_str})\n\n"
    
    # 限制显示的事件数量，避免消息过长
    max_events = min(len(items), config.max_events)
    
    for i, item in enumerate(items[:max_events]):
        event_type = "🎂" if item.get("event_type") == "birth" else "⚰️" if item.get("event_type") == "death" else "📅"
        title = item.get("title", "未知事件")
        year = item.get("year", "未知年份")
        
        message += f"{event_type} {year}年: {title}\n"
    
    if len(items) > max_events:
        message += f"\n...还有 {len(items) - max_events} 个事件未显示"
    
    message += f"\n数据来源: {config.api_url}"
    
    return message

@history_today.handle()
async def handle_history_today(event: Event, args: Message = CommandArg()):
    """处理历史上的今天命令"""
    # 获取历史事件数据
    history_data, error = await get_history_events()
    
    if error:
        await history_today.finish(error)
    
    # 格式化并发送消息
    formatted_message = format_history_message(history_data)
    await history_today.send(formatted_message)
    
    # 记录群组ID（如果是群消息）
    if isinstance(event, GroupMessageEvent):
        known_groups.add(event.group_id)
        print(f"记录群组ID: {event.group_id}")

@scheduler.scheduled_job("cron", hour=config.scheduled_hour, minute=config.scheduled_minute, id="morning_history")
async def scheduled_morning_history():
    """定时发送历史事件到所有群组"""
    # 获取当日历史事件
    history_data, error = await get_history_events()
    
    if error:
        print(f"定时发送历史事件失败: {error}")
        return
    
    # 获取bot实例
    try:
        bot = get_bot()
    except Exception as e:
        print(f"获取bot实例失败: {e}")
        return
    
    # 格式化消息
    formatted_message = format_history_message(history_data)
    greeting = f"早上好！今日历史事件回顾：\n\n{formatted_message}"
    
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
    
    # 向所有群组发送历史事件
    success_count = 0
    for group_id in known_groups:
        try:
            await bot.send_group_msg(
                group_id=group_id,
                message=greeting
            )
            success_count += 1
            # 避免发送过快被限制
            await asyncio.sleep(config.send_delay)
        except Exception as e:
            print(f"向群组 {group_id} 发送历史事件失败: {e}")
            # 如果发送失败，可能是机器人不在该群，从列表中移除
            known_groups.discard(group_id)
    
    print(f"定时历史事件发送完成，成功发送到 {success_count} 个群组")

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