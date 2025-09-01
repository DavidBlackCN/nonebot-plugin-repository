from nonebot import on_command
import httpx


movie = on_command(
    '电影票房',
    block=True,
    priority=11
)


@movie.handle()
async def main():
    msg = await get_data()
    await movie.finish(msg)


async def get_data():
    url = 'https://api.suyanw.cn/api/piaofang.php'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        data = resp.text
    return data