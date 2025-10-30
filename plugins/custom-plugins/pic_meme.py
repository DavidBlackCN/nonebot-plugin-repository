from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import FinishedException
import aiohttp
import json

__plugin_meta__ = PluginMetadata(
    name="梗图插件",
    description="获取并发送梗图",
    usage="使用命令 'meme' 来获取随机梗图",
    type="application",
    homepage="https://github.com/your-username/your-repo",
    supported_adapters=None,
)

meme = on_command("meme", aliases={"梗图"}, priority=10, block=True)

# 替换为你的API URL
API_URL = "https://tea.qingnian8.com/api/geng/random?pageSize=1"

@meme.handle()
async def handle_meme():
    try:
        # 获取API数据
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                if response.status != 200:
                    await meme.finish(f"API请求失败，状态码: {response.status}")
                
                data = await response.json()
                
                # 从返回的JSON中提取图片URL
                # 根据实际API响应结构调整这里的路径
                data_url = data.get("data")
                image_url = data_url[0].get("url") if data_url else None

                if not image_url:
                    await meme.finish("API响应中没有找到图片链接")
                
                # 发送图片
                await meme.finish(MessageSegment.image(image_url))

    except FinishedException:
        # 忽略由finish方法引起的异常
        pass

    except aiohttp.ClientError as e:
        await meme.finish(f"网络请求错误: {e}")
    except json.JSONDecodeError as e:
        await meme.finish(f"API响应解析错误: {e}")
    except Exception as e:
        await meme.finish(f"发生未知错误: {e}")