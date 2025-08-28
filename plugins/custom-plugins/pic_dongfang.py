import nonebot
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from httpx import AsyncClient, HTTPError, TimeoutException
from urllib.parse import urlparse

__plugin_meta__ = PluginMetadata(
    name="东方随机图片",
    description="获取东方Project的随机图片",
    usage="东方 - 随机获取一张东方Project图片",
    type="application",
    homepage="https://github.com/your-repo/touhou-images-plugin",
    supported_adapters={"onebot.v11", "onebot.v12", "telegram", "discord"},
)

touhou = on_command("东方", aliases={"东方图", "touhou"}, priority=10, block=True)

@touhou.handle()
async def handle_touhou():
    
    try:
        # 使用异步HTTP客户端获取图片
        async with AsyncClient(timeout=10.0, follow_redirects=False) as client:
            # API URL
            api_url = "https://img.paulzzh.com/touhou/random"
            
            # 发送请求但不跟随重定向
            response = await client.get(api_url)
            
            # 检查是否是重定向响应
            if response.status_code == 302 and 'location' in response.headers:
                # 获取重定向的图片URL
                image_url = response.headers['location']
                
                # 确保URL是完整的（有时可能是相对路径）
                if not image_url.startswith('http'):
                    parsed_api = urlparse(api_url)
                    image_url = f"{parsed_api.scheme}://{parsed_api.netloc}{image_url}"
                
                # 使用平台特定的消息段发送图片
                try:
                    from nonebot.adapters.onebot.v11 import MessageSegment as OB11MessageSegment
                    await touhou.send(OB11MessageSegment.image(image_url))
                    return
                except ImportError:
                    pass
                    
                try:
                    from nonebot.adapters.onebot.v12 import MessageSegment as OB12MessageSegment
                    await touhou.send(OB12MessageSegment.image(image_url))
                    return
                except ImportError:
                    pass
                    
                try:
                    from nonebot.adapters.telegram import MessageSegment as TGMessageSegment
                    await touhou.send(TGMessageSegment.photo(image_url))
                    return
                except ImportError:
                    pass
                    
                try:
                    from nonebot.adapters.discord import MessageSegment as DSMessageSegment
                    await touhou.send(DSMessageSegment.file(image_url))
                    return
                except ImportError:
                    pass
                    
                # 如果不支持任何已知适配器，发送原始URL
                await touhou.send(f"图片获取成功: {image_url}")
            else:
                await touhou.finish("获取图片失败，API响应异常")
            
    except TimeoutException:
        await touhou.finish("获取图片超时，请稍后再试")
    except HTTPError as e:
        await touhou.finish(f"网络请求错误: {str(e)}")
    except Exception as e:
        await touhou.finish(f"获取图片时出现错误: {str(e)}")