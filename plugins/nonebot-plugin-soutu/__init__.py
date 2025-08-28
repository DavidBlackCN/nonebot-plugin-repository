from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment, Bot
from nonebot.exception import ActionFailed, FinishedException
import httpx
import asyncio
import json

# 导入配置
from .config import config

# 插件元信息
__plugin_meta__ = PluginMetadata(
    name="图片搜索",
    description="从指定API获取图片，特定类别图片会自动撤回",
    usage=f"发送'{config.img_commands[0]} [类别]'获取图片，类别可选：{'、'.join(config.valid_categories)}",
    type="application",
    homepage="https://github.com/your-repo/your-plugin",
    supported_adapters={"onebot.v11"},
)

# 将列表转换为集合
command_aliases = set(config.img_commands[1:]) if len(config.img_commands) > 1 else set()

# 注册命令处理器
img_cmd = on_command(
    config.img_commands[0], 
    aliases=command_aliases,
    priority=10, 
    block=True
)

async def recall_message(bot: Bot, message_id: int, delay: int = config.recall_delay):
    """延迟撤回消息的函数"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_msg(message_id=message_id)
    except ActionFailed:
        # 如果撤回失败（如消息已被删除或权限不足），忽略错误
        pass

@img_cmd.handle()
async def handle_img_command(bot: Bot, args: Message = CommandArg()):
    try:
        # 获取用户输入的参数
        category = args.extract_plain_text().strip().lower()
        
        # 如果没有提供参数，默认使用"all"
        if not category:
            category = "all"
        
        # 检查分类是否有效（注意：all不再在有效分类列表中，但允许使用）
        if category != "all" and category not in config.valid_categories:
            # 使用finish而不是send后return，避免异常传播
            await img_cmd.finish(f"无效的分类，支持的分类有：{'、'.join(config.valid_categories)}")
            return  # 这里return是为了代码清晰，实际上finish已经会抛出异常终止执行
        
        # 构建API URL
        if category == "all":
            api_url = config.img_api_base
        else:
            api_url = f"{config.img_api_base}?type=json&sort={category}"
        
        # 使用异步HTTP客户端请求API，设置跟随重定向
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(api_url, timeout=30.0)
            
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            
            # 如果响应是JSON格式
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    # 检查API返回的状态码和数据
                    if data.get("code") == "200" and "url" in data:
                        img_url = data["url"]
                        # 发送图片
                        message = await img_cmd.send(MessageSegment.image(img_url))
                        
                        # 如果启用了撤回功能且当前分类需要撤回
                        if (config.enable_recall and 
                            category in config.recall_categories):
                            # 获取消息ID
                            message_id = message["message_id"]
                            # 创建后台任务，延迟后撤回消息
                            asyncio.create_task(recall_message(bot, message_id, config.recall_delay))
                            # 发送提示消息
                            await img_cmd.send(f"这是一张{category}，将在{config.recall_delay}秒后撤回喵~")
                    else:
                        error_msg = data.get("msg", "未知错误")
                        await img_cmd.finish(f"API返回错误: {error_msg}")
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试将响应文本作为图片URL
                    img_url = response.text.strip()
                    # 发送图片
                    message = await img_cmd.send(MessageSegment.image(img_url))
                    
                    # 如果启用了撤回功能且当前分类需要撤回
                    if (config.enable_recall and 
                        category in config.recall_categories):
                        # 获取消息ID
                        message_id = message["message_id"]
                        # 创建后台任务，延迟后撤回消息
                        asyncio.create_task(recall_message(bot, message_id, config.recall_delay))
                        # 发送提示消息
                        await img_cmd.send(f"这是一张{category}，将在{config.recall_delay}秒后撤回喵~")
            else:
                # 如果响应不是JSON，可能是直接重定向到图片
                # 获取最终的重定向URL
                final_url = str(response.url)
                # 发送图片
                message = await img_cmd.send(MessageSegment.image(final_url))
                
                # 如果启用了撤回功能且当前分类需要撤回
                if (config.enable_recall and 
                    category in config.recall_categories):
                    # 获取消息ID
                    message_id = message["message_id"]
                    # 创建后台任务，延迟后撤回消息
                    asyncio.create_task(recall_message(bot, message_id, config.recall_delay))
                    # 发送提示消息
                    await img_cmd.send(f"这是一张{category}，将在{config.recall_delay}秒后撤回喵~")
                
    except FinishedException:
        # 忽略FinishedException，这是正常的命令结束
        pass
    except httpx.RequestError as e:
        await img_cmd.finish(f"网络请求失败: {str(e)}")
    except httpx.HTTPStatusError as e:
        # 如果是302重定向，尝试获取重定向URL
        if e.response.status_code == 302:
            redirect_url = e.response.headers.get('location')
            if redirect_url:
                # 发送重定向URL的图片
                message = await img_cmd.send(MessageSegment.image(redirect_url))
                
                # 如果启用了撤回功能且当前分类需要撤回
                if (config.enable_recall and 
                    category in config.recall_categories):
                    # 获取消息ID
                    message_id = message["message_id"]
                    # 创建后台任务，延迟后撤回消息
                    asyncio.create_task(recall_message(bot, message_id, config.recall_delay))
                    # 发送提示消息
                    await img_cmd.send(f"这是一张{category}，将在{config.recall_delay}秒后撤回喵~")
            else:
                await img_cmd.finish(f"API返回302重定向，但未提供重定向URL")
        else:
            await img_cmd.finish(f"API服务异常: {e.response.status_code} {e.response.reason_phrase}")
    except Exception as e:
        await img_cmd.finish(f"获取图片时发生错误: {str(e)}")