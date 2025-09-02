from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import GroupMessageEvent
import aiohttp
import re
import datetime
import asyncio

# 导入配置类和配置实例
from .config import Config, plugin_config
from .database import get_group_setting, set_group_setting  # 导入数据库函数

__plugin_meta__ = PluginMetadata(
    name="疯狂星期X",
    description="获取KFC疯狂星期X文案",
    usage="疯狂星期[一二三四五六日]",
    type="application",
    homepage="https://github.com/your-repo/kfc-week-plugin",
    supported_adapters=None,
    config=Config,
)

kfc = on_command("疯狂星期", priority=10, block=True)
daily_crazy_toggle = on_command("天天疯狂", priority=10, block=True)

def is_thursday():
    """检查今天是否是星期四"""
    return datetime.datetime.now().weekday() == 3  # 0是周一，3是周四

def get_chinese_weekday():
    """获取当前星期的中文表示"""
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    return weekdays[datetime.datetime.now().weekday()]

def get_group_daily_crazy(group_id):
    """获取群组的天天疯狂模式设置"""
    # 从数据库获取群组设置，如果没有则使用全局设置
    group_setting = get_group_setting(group_id)
    return group_setting if group_setting is not None else plugin_config.daily_crazy

@daily_crazy_toggle.handle()
async def handle_daily_crazy_toggle(event: GroupMessageEvent):
    """处理天天疯狂模式切换"""
    group_id = event.group_id
    current_setting = get_group_daily_crazy(group_id)
    
    # 切换设置并保存到数据库
    new_setting = not current_setting
    set_group_setting(group_id, new_setting)
    
    status = "开启" if new_setting else "关闭"
    await daily_crazy_toggle.finish(f"已{status}本群的天天疯狂模式")

@kfc.handle()
async def handle_kfc(event: GroupMessageEvent, args: Message = CommandArg()):
    # 获取群组ID
    group_id = event.group_id
    
    # 提取用户输入的星期信息
    user_input = args.extract_plain_text().strip()
    
    # 检查是否开启了"天天疯狂"模式（优先使用群组设置）
    daily_crazy = get_group_daily_crazy(group_id)
    
    if not daily_crazy:
        # 如果未开启"天天疯狂"模式
        if not is_thursday():
            await kfc.finish("达咩！天天疯狂未开启！")
        
        # 检查用户输入的是否是"疯狂星期四"
        if not re.search(r'[四4]', user_input):
            await kfc.finish("达咩！天天疯狂未开启！")
    
    # 匹配星期几（支持中文数字和阿拉伯数字）
    day_match = re.search(r'[一二三四五六日1234567]', user_input)
    if not day_match:
        # 如果没有指定星期几，使用配置中的默认值
        target_day = plugin_config.kfc_default_day
    else:
        target_day = day_match.group()
    
    # 将阿拉伯数字转换为中文
    num_to_chinese = {
        '1': '一', '2': '二', '3': '三', 
        '4': '四', '5': '五', '6': '六', '7': '日'
    }
    if target_day in num_to_chinese:
        target_day = num_to_chinese[target_day]
    
    # 构建用户实际输入的星期命令
    user_command = f"疯狂星期{target_day}"
    
    try:
        # 从API获取KFC文案
        async with aiohttp.ClientSession() as session:
            async with session.get(
                plugin_config.kfc_api_url, 
                timeout=plugin_config.kfc_timeout
            ) as response:
                if response.status != 200:
                    await kfc.finish("获取KFC文案失败，请稍后再试")
                
                data = await response.json()
                
                # 正确解析API响应结构
                if 'data' in data and isinstance(data['data'], dict):
                    # 从data字段中获取kfc字段
                    content = data['data'].get('kfc', '')
                    if not content:
                        # 如果kfc字段不存在或为空，尝试content字段
                        content = data['data'].get('content', '')
                else:
                    # 如果API响应结构不符合预期，尝试直接获取kfc或content字段
                    content = data.get('kfc', data.get('content', ''))
                
                if not content:
                    logger.error(f"API返回数据中未找到'kfc'或'content'字段。完整响应: {data}")
                    await kfc.finish("获取到的文案格式有误，请稍后再试或联系管理员。")
                
                # 如果文案中包含"疯狂星期四"，则替换为用户输入的星期
                if "疯狂星期四" in content:
                    modified_content = content.replace("疯狂星期四", user_command)
                    await kfc.finish(modified_content)
                else:
                    # 如果不包含则直接发送原内容
                    await kfc.finish(content)
                    
    except aiohttp.ClientError as e:
        logger.error(f"网络请求错误: {e}")
        await kfc.finish("网络请求失败，请检查网络连接")
    except asyncio.TimeoutError:
        logger.error("请求超时")
        await kfc.finish("请求超时，请稍后再试")
    except FinishedException:
        # 当消息已经成功发送时，忽略FinishedException
        pass
    except Exception as e:
        logger.error(f"处理KFC文案时发生错误: {e}")
        await kfc.finish("处理文案时发生错误，请稍后再试")