from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import FinishedException
import aiohttp
import base64

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="pic_cosplay",
    description="获取并发送cosplay",
    usage="cosplay - 随机获取一张cosplay",
    type="application",
    homepage="https://github.com/your_username/your_repo",
    supported_adapters={"~onebot.v11"},
)

cosplay_cmd = on_command("cosplay", priority=5, block=True)

API_URL = "https://api.lolimi.cn/API/cosplay/api.php?type=image"

@cosplay_cmd.handle()
async def handle_cosplay():
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
                        await cosplay_cmd.send(MessageSegment.image(f"base64://{base64_data}"))
                    else:
                        # 尝试获取文本响应（可能是URL）
                        text_response = await response.text()
                        
                        # 发送图片
                        await cosplay_cmd.send(MessageSegment.image(text_response))
                else:
                    await cosplay_cmd.send("获取cosplay图片失败，请稍后再试")

    except FinishedException:
        # 这是正常的结束异常，不需要处理
        pass
    
    except Exception as e:
        await cosplay_cmd.send(f"获取cosplay图片时发生错误: {str(e)}")