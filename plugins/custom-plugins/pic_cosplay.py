from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
import httpx


cosplay = on_command(
    'cosplay',
    block=True,
    priority=11
)


@cosplay.handle()
async def main():
    msg = await get_data()
    await cosplay.finish(MessageSegment.image(msg))


async def get_data():
    url = 'https://api.lolimi.cn/API/cosplay/api.php?type=image'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        data = resp.text.strip()
    return data