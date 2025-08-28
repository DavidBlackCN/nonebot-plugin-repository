from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot.exception import FinishedException
import httpx
from urllib.parse import quote

__plugin_meta__ = PluginMetadata(
    name="发病语录",
    description="获取随机的发病语录",
    usage="/发病 [内容]",
    type="application",
    homepage="https://github.com/vikiboss/60s",
)

fabing = on_command("发病", priority=10, block=True)

@fabing.handle()
async def handle_fabing(args: Message = CommandArg()):
    # 获取用户输入的参数
    user_input = args.extract_plain_text().strip()
    
    # 构建API请求URL
    api_url = "https://60s.zeabur.app/v2/fabing"
    if user_input:
        # 对用户输入进行URL编码，避免特殊字符问题
        api_url += f"?name={quote(user_input)}"
    
    try:
        # 发送HTTP请求获取数据
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
        
        # 检查API返回状态
        if data.get("code") == 200:
            saying = data["data"]["saying"]
            # 直接使用finish发送结果
            await fabing.finish(saying)
        else:
            await fabing.finish("获取发病语录失败，请稍后再试")
            
    except httpx.RequestError as e:
        logger.error(f"请求API失败: {e}")
        await fabing.finish("网络请求失败，请检查网络连接")
    except httpx.HTTPStatusError as e:
        logger.error(f"API返回错误状态码: {e.response.status_code}")
        await fabing.finish("API服务异常，请稍后再试")
    except FinishedException:
        # 不处理FinishedException，让它正常传播
        raise
    except Exception as e:
        logger.error(f"处理发病语录时发生未知错误: {e}")
        # 添加更详细的错误信息到日志
        logger.error(f"API返回数据: {data if 'data' in locals() else '无数据'}")
        await fabing.finish("获取发病语录时发生未知错误")