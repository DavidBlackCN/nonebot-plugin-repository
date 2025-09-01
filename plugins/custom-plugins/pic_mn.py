from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
import httpx

__plugin_meta__ = PluginMetadata(
    name="猫娘图片插件",
    description="获取并发送猫娘图片",
    usage="使用命令 '猫娘' 来获取随机猫娘图片",
    type="application",
    homepage="https://github.com/your-username/your-repo",
    supported_adapters={"onebot.v11"},
)

mn_cmd = on_command("猫娘", priority=10, block=True)

API_URL = "https://api.lxtu.cn/api.php?category=mn"

@mn_cmd.handle()
async def handle_mn():
    try:
        # 获取图片URL
        async with httpx.AsyncClient() as client:
            # 发送请求并跟随重定向，但不获取响应体
            response = await client.head(API_URL, follow_redirects=True)
            
            # 检查响应状态
            if response.status_code != 200:
                await mn_cmd.finish(f"获取图片失败，状态码: {response.status_code}")
            
            # 获取最终的重定向URL
            image_url = str(response.url)
            
            # 发送图片
            await mn_cmd.send(MessageSegment.image(image_url))
            
    except httpx.RequestError as e:
        await mn_cmd.finish(f"请求图片时发生错误: {e}")
    except Exception as e:
        await mn_cmd.finish(f"发生未知错误: {e}")