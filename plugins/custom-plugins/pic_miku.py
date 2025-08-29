from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
import httpx

__plugin_meta__ = PluginMetadata(
    name="Miku图片插件",
    description="获取并发送Miku图片",
    usage="使用命令 'miku' 来获取随机Miku图片",
    type="application",
    homepage="https://github.com/your-username/your-repo",
    supported_adapters={"onebot.v11"},
)

miku_cmd = on_command("miku", priority=10, block=True)

@miku_cmd.handle()
async def handle_miku():
    
    try:
        # 获取图片URL
        async with httpx.AsyncClient() as client:
            # 发送请求并跟随重定向，但不获取响应体
            response = await client.head("https://apii.ctose.cn/api/cy/api/", follow_redirects=True)
            
            # 检查响应状态
            if response.status_code != 200:
                await miku_cmd.finish(f"获取图片失败，状态码: {response.status_code}")
            
            # 获取最终的重定向URL
            image_url = str(response.url)
            
            # 发送图片
            await miku_cmd.send(MessageSegment.image(image_url))
            
    except httpx.RequestError as e:
        await miku_cmd.finish(f"请求图片时发生错误: {e}")
    except Exception as e:
        await miku_cmd.finish(f"发生未知错误: {e}")