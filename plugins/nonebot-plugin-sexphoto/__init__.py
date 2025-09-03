from nonebot import on_command, get_driver
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    MessageSegment, 
    Bot, 
    ActionFailed, 
    GroupMessageEvent, 
    PrivateMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER
)
import httpx
import asyncio
from typing import Optional, List, Dict, Union
import re
import time
import logging
from .config import Config
from .database import set_group_r18, get_group_r18

# 获取配置
driver = get_driver()
plugin_config = Config.parse_obj(driver.config.dict())

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 冷却时间记录器：user_id: last_success_time
cd_dict: Dict[str, float] = {}

# 撤回任务记录器：message_id: recall_task
recall_tasks: Dict[int, asyncio.Task] = {}

# 图片发送锁，限制并发发送数量
send_lock = asyncio.Semaphore(3)

# 创建全局HTTP客户端连接池
client = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    timeout=httpx.Timeout(15.0, connect=5.0),
    follow_redirects=True
)

# 插件元信息
__plugin_meta__ = PluginMetadata(
    name="色图插件",
    description="从SexPhotoAPI获取色图的插件，支持群聊R18开关",
    usage=f"{plugin_config.sexphoto_command} [数量] [r18] [关键词] [标签]\n"
          f"{plugin_config.sexphoto_enable_command} - 开启群聊R18功能\n"
          f"{plugin_config.sexphoto_disable_command} - 关闭群聊R18功能",
    type="application",
    homepage="https://github.com/your-repo/your-plugin",
    supported_adapters={"onebot.v11"},
    config=Config,  # 声明插件配置模型
)

# 创建命令
sexphoto = on_command(plugin_config.sexphoto_command, priority=10, block=True)
enable_r18 = on_command(plugin_config.sexphoto_enable_command, priority=10, block=True)
disable_r18 = on_command(plugin_config.sexphoto_disable_command, priority=10, block=True)

async def fetch_sexphoto(num: int = 1, r18: bool = False, keyword: Optional[str] = None, tags: Optional[List[str]] = None) -> List[dict]:
    """从API获取色图数据，带重试机制"""
    base_url = plugin_config.sexphoto_api_url
    params = {"num": num}
    
    if r18 and plugin_config.sexphoto_enable_r18:
        params["r18"] = "true"
    if keyword:
        params["keyword"] = keyword
    if tags:
        params["tag"] = tags
    
    # 重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and data.get("data"):
                return data["data"]
            else:
                logger.warning(f"API返回数据无效，尝试 {attempt+1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # 等待1秒后重试
        except httpx.HTTPError as e:
            logger.error(f"API请求失败 (HTTP错误): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"API请求失败 (异常): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
    
    return []  # 所有重试失败后返回空列表

async def send_image(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], img_url: str) -> int:
    """发送单张图片，带重试机制，返回消息ID（失败返回-1）"""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # 使用锁限制并发发送
            async with send_lock:
                if isinstance(event, GroupMessageEvent):
                    result = await bot.send_group_msg(
                        group_id=event.group_id, 
                        message=MessageSegment.image(img_url)
                    )
                    return result["message_id"]
                else:
                    result = await bot.send_private_msg(
                        user_id=event.user_id, 
                        message=MessageSegment.image(img_url)
                    )
                    return result["message_id"]
        except ActionFailed as e:
            logger.warning(f"图片发送失败 (ActionFailed): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # 短暂等待后重试
        except Exception as e:
            logger.error(f"图片发送失败 (异常): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    
    return -1  # 所有重试失败后返回-1

async def recall_image(bot: Bot, message_id: int, delay: int):
    """延迟撤回图片"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_msg(message_id=message_id)
    except ActionFailed as e:
        logger.warning(f"撤回消息失败 (ActionFailed): {e}")
    except Exception as e:
        logger.error(f"撤回消息失败 (异常): {e}")
    finally:
        # 移除完成的任务
        if message_id in recall_tasks:
            del recall_tasks[message_id]

def has_permission(user_id: int) -> bool:
    """检查用户是否有权限启用/禁用R18"""
    # 白名单用户直接允许
    if user_id in plugin_config.sexphoto_whitelist:
        return True
    
    # 群聊中管理员权限检查在命令处理中完成
    return False

@enable_r18.handle()
async def handle_enable_r18(bot: Bot, event: GroupMessageEvent):
    """处理开启R18命令"""
    user_id = event.user_id
    group_id = event.group_id
    
    # 检查用户权限（管理员、群主或白名单）
    if not (await GROUP_ADMIN(bot, event) or 
            await GROUP_OWNER(bot, event) or 
            has_permission(user_id)):
        await enable_r18.finish("只有管理员或群主才能开启R18功能喵")
    
    # 更新群聊状态
    set_group_r18(group_id, True)
    
    # 发送提示消息
    await enable_r18.finish("本群R18功能已开启喵！")

@disable_r18.handle()
async def handle_disable_r18(bot: Bot, event: GroupMessageEvent):
    """处理关闭R18命令"""
    user_id = event.user_id
    group_id = event.group_id
    
    # 检查用户权限（管理员、群主或白名单）
    if not (await GROUP_ADMIN(bot, event) or 
            await GROUP_OWNER(bot, event) or 
            has_permission(user_id)):
        await disable_r18.finish("只有管理员或群主才能关闭R18功能喵")
    
    # 更新群聊状态
    set_group_r18(group_id, False)
    
    # 发送提示消息
    await disable_r18.finish("本群R18功能已关闭喵！")

@sexphoto.handle()
async def handle_sexphoto(
    bot: Bot, 
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    args: Message = CommandArg()
):
    user_id = str(event.user_id)
    current_time = time.time()
    
    # 检查CD
    if user_id in cd_dict:
        last_time = cd_dict[user_id]
        if current_time - last_time < plugin_config.sexphoto_cd:
            remaining = int(plugin_config.sexphoto_cd - (current_time - last_time))
            await sexphoto.finish(f"达咩！您冲的太快啦！冷却时间还有{remaining}秒")
    
    arg_str = args.extract_plain_text().strip()
    
    num = 1
    r18 = False
    keyword = None
    tags = None
    
    # 第一步：检查是否包含r18标记（不区分大小写）
    r18_pattern = re.compile(r'\b(r18)\b', re.IGNORECASE)
    r18_match = r18_pattern.search(arg_str)
    if r18_match:
        r18 = True
        # 移除r18标记
        arg_str = r18_pattern.sub('', arg_str, count=1).strip()
    
    # 第二步：检查数量
    num_match = re.search(r'\b(\d+)\b', arg_str)
    if num_match:
        requested_num = int(num_match.group(1))
        num = min(requested_num, plugin_config.sexphoto_max_num)
        # 移除数量标记
        arg_str = arg_str.replace(num_match.group(1), '', 1).strip()
    
    # 检查R18状态和限制
    original_requested_num = None
    
    # 在群聊中检查R18是否开启
    if r18 and isinstance(event, GroupMessageEvent):
        group_r18_enabled = get_group_r18(event.group_id)
        if not group_r18_enabled:
            await sexphoto.finish("本群尚未开启R18功能！请管理员或白名单用户发送「开启r18」开启喵")
        
        # 如果启用R18且请求数量超过R18限制
        if num > plugin_config.sexphoto_r18_max_num:
            original_requested_num = num
            num = plugin_config.sexphoto_r18_max_num
    
    # 剩余部分作为关键词和标签
    parts = [part.strip() for part in arg_str.split() if part.strip()]
    if parts:
        keyword = parts[0]
        if len(parts) > 1:
            tags = parts[1:]
    
    # 如果有R18限制，在获取数据前发送提示
    if original_requested_num is not None:
        await sexphoto.send(f"⚠️ R18模式限制：一次最多发送 {plugin_config.sexphoto_r18_max_num} 张图片，您请求了 {original_requested_num} 张，注意身体喵！")
    
    # 获取图片数据
    try:
        data = await fetch_sexphoto(num, r18, keyword, tags)
    except Exception as e:
        logger.error(f"获取图片数据失败: {e}")
        await sexphoto.finish("图片获取失败，请稍后再试喵")
    
    if not data:
        await sexphoto.finish("没有找到符合条件的图片喵，请尝试其他关键词或标签~")
    
    # 获取撤回时间配置
    recall_delay = plugin_config.sexphoto_r18_recall_time if r18 else plugin_config.sexphoto_normal_recall_time
    
    # 单张图片处理
    if len(data) == 1:
        item = data[0]
        img_url = item.get("url")
        if img_url:
            message_id = await send_image(bot, event, img_url)
            if message_id != -1:
                # 成功发送后更新CD时间
                cd_dict[user_id] = current_time
                
                # 启动撤回任务（仅当撤回时间大于0时）
                if recall_delay > 0:
                    recall_task = asyncio.create_task(
                        recall_image(bot, message_id, recall_delay)
                    )
                    recall_tasks[message_id] = recall_task
            else:
                await sexphoto.finish("图片发送失败喵，可能是网络问题或图片地址无效~")
        else:
            await sexphoto.finish("图片数据无效，未找到有效URL")
        return
    
    # 多张图片处理
    success_count = 0
    failed_count = 0
    
    # 并行发送图片（使用异步锁控制并发）
    send_tasks = []
    for item in data:
        img_url = item.get("url")
        if img_url:
            send_tasks.append(send_image(bot, event, img_url))
        else:
            failed_count += 1
    
    # 并行执行所有发送任务
    results = await asyncio.gather(*send_tasks, return_exceptions=True)
    
    # 统计结果并启动撤回任务
    for result in results:
        if isinstance(result, Exception) or result == -1:
            failed_count += 1
        else:
            success_count += 1
            # 启动撤回任务（仅当撤回时间大于0时）
            if recall_delay > 0:
                recall_task = asyncio.create_task(
                    recall_image(bot, result, recall_delay)
                )
                recall_tasks[result] = recall_task
    
    # 添加统计信息
    if success_count > 0:
        message_parts = [f"成功发送 {success_count} 张图片喵~"]
        if failed_count > 0:
            message_parts.append(f"有 {failed_count} 张图片消失了喵~")
        
        # 发送统计信息
        stat_msg = "".join(message_parts)
        await sexphoto.send(stat_msg)
    
        # 只要有成功发送的图片就更新CD
        cd_dict[user_id] = current_time
    else:
        await sexphoto.finish("所有图片发送失败，请检查网络或图片地址喵")

# 添加关闭客户端连接和取消撤回任务的处理
@driver.on_shutdown
async def shutdown_client():
    # 取消所有未完成的撤回任务
    for task in recall_tasks.values():
        task.cancel()
    # 关闭HTTP客户端
    await client.aclose()