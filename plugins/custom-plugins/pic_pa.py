from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message, permission
from nonebot.params import CommandArg, ArgPlainText
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.exception import FinishedException
import aiohttp

# 注册一个命令处理器，不需要@bot触发
pa = on_command("爬", priority=5, block=True)

@pa.handle()
async def handle_pa(event: GroupMessageEvent, matcher: Matcher, state: T_State):
    # 获取消息中的所有@用户
    at_segments = [seg for seg in event.message if seg.type == "at"]
    
    if not at_segments:
        await pa.finish("⚠️ 请@一个用户喵")
    
    # 获取第一个被@用户的QQ号
    qq = at_segments[0].data["qq"]
    
    if qq == "all":
        await pa.finish("⚠️ 不能@全体成员喵")
    
    # 构建API URL
    api_url = f"https://api.mhimg.cn/api/biaoqingbao_pa?qq={qq}"
    
    try:
        # 异步获取图片
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    # 获取图片数据
                    image_data = await response.read()
                    
                    # 发送图片
                    await pa.send(MessageSegment.image(image_data))
                    # 不再使用 finish，避免抛出 FinishedException
                else:
                    await pa.finish("⚠️获取图片失败，API无响应")
    except FinishedException:
        # 忽略 FinishedException，这是正常的行为
        pass

    except Exception as e:
        await pa.finish(f"⚠️获取图片时出错: {str(e)}")