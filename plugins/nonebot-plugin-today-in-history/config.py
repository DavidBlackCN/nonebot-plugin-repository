from pydantic_settings import BaseSettings
from typing import List, Optional

class Config(BaseSettings):
    # 命令触发关键词
    history_command: str = "历史上的今天"
    history_aliases: List[str] = ["历史", "today", "history"]
    
    # API配置
    api_url: str = "https://60s.zeabur.app/v2/today_in_history"
    api_timeout: int = 10
    
    # 定时任务配置
    scheduled_hour: int = 12
    scheduled_minute: int = 0
    
    # 其他配置
    send_delay: float = 1.0  # 群发消息之间的延迟（秒）
    max_events: int = 10  # 最大显示事件数量
    
    class Config:
        extra = "ignore"

# 创建配置实例
config = Config()