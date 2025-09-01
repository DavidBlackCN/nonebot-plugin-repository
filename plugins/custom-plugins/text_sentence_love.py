from nonebot import on_command
import httpx
import json


twqh = on_command(
    '土味情话',
    block=True,
    priority=11
)


@twqh.handle()
async def main():
    msg = await get_data()
    await twqh.finish(msg)


async def get_data():
    url = 'https://api.suxun.site/api/qinghua'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        data = resp.text
    return data