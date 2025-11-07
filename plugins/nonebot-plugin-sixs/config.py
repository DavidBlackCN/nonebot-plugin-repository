from pydantic_settings import BaseSettings
from typing import List, Optional

class Config(BaseSettings):
    # 命令触发关键词
    sixty_seconds_command: str = "60秒"
    sixty_seconds_aliases: List[str] = ["60s", "六十秒"]
    
    # API配置
    api_url: str = "http://api.suxun.site/api/sixs?type=json"
    # 可选备用API地址
    # https://jx.iqfk.top/api/new
    # https://60s.zeabur.app/v2/60s
    # https://api.southerly.top/api/60s?format=image
    api_timeout: int = 10
    
    # 定时任务配置
    scheduled_hour: int = 10
    scheduled_minute: int = 0
    
    # 其他配置
    send_delay: float = 1.0  # 群发消息之间的延迟（秒）
    
    class Config:
        extra = "ignore"

# 创建配置实例
config = Config()