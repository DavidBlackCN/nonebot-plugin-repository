from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import FinishedException
import aiohttp
import base64

__plugin_meta__ = PluginMetadata(
    name="猫猫图片插件",
    description="获取并发送猫猫图片",
    usage="使用命令 '猫猫' 来获取随机猫猫图片",
    type="application",
    homepage="https://github.com/your-username/your-repo",
    supported_adapters={"onebot.v11"},
)

miao_cmd = on_command("猫猫", priority=10, block=True)

API_URL = "http://edgecats.net/"

@miao_cmd.handle()
async def handle_miao():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                if response.status == 200:
                    # 获取响应的内容类型
                    content_type = response.headers.get('Content-Type', '')
                    
                    # 检查是否是图片
                    if 'image' in content_type:
                        # 直接读取二进制图片数据
                        image_data = await response.read()
                        
                        # 将图片数据转换为 base64 编码
                        base64_data = base64.b64encode(image_data).decode('utf-8')
                        
                        # 发送 base64 编码的图片
                        await miao_cmd.send(MessageSegment.image(f"base64://{base64_data}"))
                    else:
                        # 尝试获取文本响应（可能是URL）
                        text_response = await response.text()
                        
                        # 发送图片
                        await miao_cmd.send(MessageSegment.image(text_response))
                else:
                    await miao_cmd.send("获取猫猫图片失败，请稍后再试")

    except FinishedException:
        pass # 这是正常的结束异常，不需要处理
    except Exception as e:
        await miao_cmd.send(f"获取猫猫图片时发生错误: {str(e)}")