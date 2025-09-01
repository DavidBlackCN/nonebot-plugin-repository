from nonebot import on_command
import httpx


tgrj = on_command(
    '舔狗日记',
    block=True,
    priority=11
)


@tgrj.handle ()
async def main():
    msg = await get_data()
    await tgrj.finish(msg)


async def get_data():
    url = 'https://api.suyanw.cn/api/tiangou.php'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        data = resp.text
    return data