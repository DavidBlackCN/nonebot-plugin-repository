from pydantic import BaseModel, Field
from typing import List, Optional

class MuteConfig(BaseModel):
    # 命令关键词配置
    mute_command: List[str] = ["mute", "禁言", "口球"]
    unmute_command: List[str] = ["unmute", "解禁"]
    muteme_command: List[str] = ["muteme", "禁我"]
    
    # 默认禁言时长（分钟）
    default_mute_duration: int = 10
    
    # 默认时间单位（当未指定单位时使用）
    default_time_unit: str = "m"  # s:秒, m:分钟, h:小时, d:天
    
    # 白名单用户ID列表
    whitelist_users: List[int] = Field(default_factory=list)
    
    # 是否允许群管理员使用命令
    allow_group_admins: bool = True
    
    # 最大禁言时长（分钟，0表示无限制）
    max_mute_duration: int = 43200  # 30天
    
    # 是否需要在群聊中@机器人
    require_at_bot: bool = False
    
    # 是否启用理由记录
    enable_reason: bool = True
    
    # muteme 随机禁言配置
    # 随机禁言的最小和最大时长（秒）
    muteme_min_duration: int = 60  # 1分钟
    muteme_max_duration: int = 600  # 10分钟
    
    # 是否允许muteme命令
    enable_muteme: bool = True
    
    # muteme 回复消息模板
    muteme_success_message: str = "🥰 那就满足你叭w，药效{duration}哦~"
    muteme_fail_message: str = "⚠️ 自禁言失败，请检查Bot权限喵"