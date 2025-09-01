from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import FinishedException
import aiohttp
import json

__plugin_meta__ = PluginMetadata(
    name="jk图片插件",
    description="获取并发送jk图片",
    usage="使用命令 'jk' 来获取随机jk图片",
    type="application",
    homepage="https://github.com/your-username/your-repo",
    supported_adapters=None,
)

jk = on_command("jk", aliases={"JK"}, priority=10, block=True)

# 替换为你的API URL
API_URL = "https://v2.xxapi.cn/api/jk?return=json"

@jk.handle()
async def handle_jk():
    try:
        # 获取API数据
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                if response.status != 200:
                    await jk.finish(f"API请求失败，状态码: {response.status}")
                
                data = await response.json()
                
                # 从返回的JSON中提取图片URL
                # 根据实际API响应结构调整这里的路径
                image_url = data.get("data")
                
                if not image_url:
                    await jk.finish("API响应中没有找到图片链接")
                
                # 发送图片
                await jk.finish(MessageSegment.image(image_url))

    except FinishedException:
        # 忽略由finish方法引起的异常
        pass

    except aiohttp.ClientError as e:
        await jk.finish(f"网络请求错误: {e}")
    except json.JSONDecodeError as e:
        await jk.finish(f"API响应解析错误: {e}")
    except Exception as e:
        await jk.finish(f"发生未知错误: {e}")