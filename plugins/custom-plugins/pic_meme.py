from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
import httpx
from typing import Optional

__plugin_meta__ = PluginMetadata(
    name="梗图生成器",
    description="从指定API获取随机梗图",
    usage="/meme [模板名称] - 获取随机梗图或指定模板梗图",
    type="application",
    homepage="https://github.com/your_username/your_repo",
    supported_adapters=None,
)

meme = on_command("meme", aliases={"梗图", "生成梗图"}, priority=10, block=True)

@meme.handle()
async def handle_meme(args: Message = CommandArg()):
    # 获取用户输入的命令参数
    template = args.extract_plain_text().strip()
    
    # 构建请求URL
    url = "https://zeapi.ink/v1/sjmeme.php?format=json"
    if template:
        url += f"&template={template}"
    
    try:
        # 发送HTTP请求获取梗图数据
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # 检查响应数据
        if data.get("code") == 200 and "url" in data:
            image_url = data["url"]
            await meme.finish(f"[CQ:image,file={image_url}]")
        else:
            error_msg = data.get("msg", "未知错误")
            await meme.finish(f"获取梗图失败: {error_msg}")
            
    except httpx.RequestError as e:
        logger.error(f"请求梗图API失败: {e}")
        await meme.finish("网络请求失败，请稍后再试")
    except httpx.HTTPStatusError as e:
        logger.error(f"API返回错误状态码: {e.response.status_code}")
        await meme.finish("服务暂时不可用，请稍后再试")
    except Exception as e:
        logger.error(f"处理梗图请求时发生未知错误: {e}")
        await meme.finish("获取梗图时发生未知错误")