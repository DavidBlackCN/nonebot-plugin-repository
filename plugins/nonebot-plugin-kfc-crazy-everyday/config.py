from pydantic import BaseModel, Extra
from nonebot import get_plugin_config

class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""

    # KFC API地址
    kfc_api_url: str = "https://60s.zeabur.app/v2/kfc"  

    # 请求超时时间（秒）
    kfc_timeout: int = 10  

    # 默认星期几
    kfc_default_day: str = "四"  

    # 是否开启"天天疯狂"模式
    # 开启后任意时间输入"疯狂星期X"均有回复
    # 关闭后仅在星期四输入"疯狂星期四"有回复
    daily_crazy: bool = True  

# 获取配置
plugin_config = get_plugin_config(Config)