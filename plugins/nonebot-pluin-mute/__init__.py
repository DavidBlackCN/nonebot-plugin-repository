from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .config import MuteConfig
import re
import random
from typing import Tuple, Optional

__plugin_meta__ = PluginMetadata(
    name="禁言（口球）管理插件",
    description="通过命令管理群成员禁言，支持多种时间单位和自禁言功能",
    usage="mute @某人 [时长+单位] [理由] 或 unmute @某人 或 muteme\n单位: s(秒), m(分钟), h(小时), d(天)，默认为分钟",
    config=MuteConfig,
    extra={"version": "1.2.0"},  # 更新版本号
)

# 加载配置
config = MuteConfig()

# 创建命令处理器
if config.require_at_bot:
    rule = to_me()
else:
    rule = None

# 注册禁言命令处理器
mute_aliases = set(config.mute_command[1:]) if len(config.mute_command) > 1 else set()
mute_matcher = on_command(
    config.mute_command[0], 
    aliases=mute_aliases,
    rule=rule,
    priority=10, 
    block=True
)

# 注册解除禁言命令处理器
unmute_aliases = set(config.unmute_command[1:]) if len(config.unmute_command) > 1 else set()
unmute_matcher = on_command(
    config.unmute_command[0], 
    aliases=unmute_aliases,
    rule=rule,
    priority=10, 
    block=True
)

# 注册自禁言命令处理器
muteme_aliases = set(config.muteme_command[1:]) if len(config.muteme_command) > 1 else set()
muteme_matcher = on_command(
    config.muteme_command[0], 
    aliases=muteme_aliases,
    rule=rule,
    priority=10, 
    block=True
)

async def check_permission(bot: Bot, event: GroupMessageEvent) -> bool:
    """检查用户权限"""
    user_id = event.user_id
    
    # 超级用户始终有权限
    if await SUPERUSER(bot, event):
        return True
    
    # 白名单用户有权限
    if user_id in config.whitelist_users:
        return True
    
    # 群管理员有权限（如果配置允许）
    if config.allow_group_admins:
        group_id = event.group_id
        member_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        if member_info.get("role") in ["admin", "owner"]:
            return True
    
    return False

def parse_duration(duration_str: str) -> int:
    """解析时长字符串，返回秒数"""
    # 匹配数字和单位
    pattern = r'^(\d+)([smhd]?)$'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        raise ValueError("⚠️ 无效的时长格式喵")
    
    num, unit = match.groups()
    num = int(num)
    
    # 如果没有指定单位，使用默认单位
    if not unit:
        unit = config.default_time_unit
    
    # 根据单位转换为秒
    if unit == 's':  # 秒
        return num
    elif unit == 'm':  # 分钟
        return num * 60
    elif unit == 'h':  # 小时
        return num * 3600
    elif unit == 'd':  # 天
        return num * 86400
    else:
        raise ValueError("⚠️ 不支持的时间单位喵")

def format_duration(seconds: int) -> str:
    """将秒数格式化为易读的字符串"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        return f"{seconds // 60}分钟"
    elif seconds < 86400:
        return f"{seconds // 3600}小时"
    else:
        return f"{seconds // 86400}天"

def parse_mute_command(message: Message) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """解析禁言命令，提取目标用户、时长(秒)和理由"""
    target_user = None
    duration_seconds = None
    reason = None
    
    # 提取@的用户
    for segment in message:
        if segment.type == "at":
            target_user = int(segment.data.get("qq", 0))
            break
    
    # 如果没有@用户，直接返回
    if not target_user:
        return None, None, None
    
    # 提取文本内容
    text = message.extract_plain_text().strip()
    
    # 如果没有文本内容，直接返回
    if not text:
        return target_user, None, None
    
    # 使用正则表达式匹配时长和理由
    # 匹配模式: 时长(数字+单位) 和 理由
    pattern = r'(\d+[smhd]?)(?:\s+(.+))?$'
    match = re.search(pattern, text)
    
    if match:
        duration_str, reason_str = match.groups()
        
        # 解析时长
        if duration_str:
            try:
                duration_seconds = parse_duration(duration_str)
            except ValueError as e:
                logger.warning(f"⚠️ 解析时长失败: {e}")
                # 时长解析失败，不设置时长
        
        # 处理理由
        if reason_str:
            reason = reason_str.strip()
    
    return target_user, duration_seconds, reason

def parse_unmute_command(message: Message) -> Optional[int]:
    """解析解除禁言命令，提取目标用户"""
    target_user = None
    
    # 提取@的用户
    for segment in message:
        if segment.type == "at":
            target_user = int(segment.data.get("qq", 0))
            break
    
    return target_user

async def mute_user(bot: Bot, group_id: int, user_id: int, duration_seconds: int, reason: Optional[str] = None) -> bool:
    """执行禁言操作"""
    try:
        # 检查最大禁言时长
        max_duration = config.max_mute_duration * 60  # 转换为秒
        if max_duration > 0 and duration_seconds > max_duration:
            duration_seconds = max_duration
        
        # 执行禁言
        await bot.set_group_ban(
            group_id=group_id,
            user_id=user_id,
            duration=duration_seconds,
        )
        
        # 记录日志
        duration_formatted = format_duration(duration_seconds)
        log_msg = f"😋 已为用户 {user_id} 塞上口球w，时长 {duration_formatted}"
        if reason:
            log_msg += f"，理由：{reason}"
        logger.info(log_msg)
        
        return True
    except Exception as e:
        logger.error(f"⚠️ 塞口球操作失败: {e}")
        return False

async def unmute_user(bot: Bot, group_id: int, user_id: int) -> bool:
    """执行解除禁言操作"""
    try:
        await bot.set_group_ban(
            group_id=group_id,
            user_id=user_id,
            duration=0,  # 0表示解除禁言
        )
        
        logger.info(f"✅ 用户 {user_id} 已被取下口球喵")
        return True
    except Exception as e:
        logger.error(f"⚠️ 取下口球操作失败喵: {e}")
        return False

def generate_random_duration() -> int:
    """生成随机禁言时长（秒）"""
    return random.randint(config.muteme_min_duration, config.muteme_max_duration)

@mute_matcher.handle()
async def handle_mute(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    """处理禁言命令"""
    # 检查权限
    if not await check_permission(bot, event):
        await mute_matcher.finish("⚠️ 您没有权限执行此操作喵")
    
    # 解析消息
    target_user, duration_seconds, reason = parse_mute_command(msg)
    
    # 检查目标用户
    if not target_user:
        await mute_matcher.finish("⚠️ 请@要塞口球的用户喵")
    
    # 设置默认时长
    if not duration_seconds:
        duration_seconds = config.default_mute_duration * 60  # 转换为秒
        logger.info(f"使用默认口球时长: {duration_seconds}秒")
    
    # 执行禁言
    success = await mute_user(bot, event.group_id, target_user, duration_seconds, reason)
    
    if success:
        duration_formatted = format_duration(duration_seconds)
        reply = f"😋 已为用户 {target_user} 塞上口球w，时长 {duration_formatted}"
        if reason and config.enable_reason:
            reply += f"，理由：{reason}"
        await mute_matcher.finish(reply)
    else:
        await mute_matcher.finish("⚠️ 禁言操作失败，请检查Bot权限喵")

@unmute_matcher.handle()
async def handle_unmute(bot: Bot, event: GroupMessageEvent, msg: Message = CommandArg()):
    """处理解除禁言命令"""
    # 检查权限
    if not await check_permission(bot, event):
        await unmute_matcher.finish("⚠️ 您没有权限执行此操作喵")
    
    # 解析消息
    target_user = parse_unmute_command(msg)
    
    # 检查目标用户
    if not target_user:
        await unmute_matcher.finish("⚠️ 请@要取下口球的用户喵")
    
    # 执行解除禁言
    success = await unmute_user(bot, event.group_id, target_user)
    
    if success:
        await unmute_matcher.finish(f"✅ 用户 {target_user} 已被取下口球喵")
    else:
        await unmute_matcher.finish("⚠️ 取下口球操作失败，请检查Bot权限喵")

@muteme_matcher.handle()
async def handle_muteme(bot: Bot, event: GroupMessageEvent):
    """处理自禁言命令"""
    # 检查是否启用muteme功能
    if not config.enable_muteme:
        await muteme_matcher.finish("自禁言功能已禁用")
    
    # 生成随机禁言时长
    duration_seconds = generate_random_duration()
    
    # 执行自禁言
    success = await mute_user(bot, event.group_id, event.user_id, duration_seconds, "自禁言")
    
    if success:
        duration_formatted = format_duration(duration_seconds)
        reply = config.muteme_success_message.format(duration=duration_formatted)
        await muteme_matcher.finish(reply)
    else:
        await muteme_matcher.finish(config.muteme_fail_message)