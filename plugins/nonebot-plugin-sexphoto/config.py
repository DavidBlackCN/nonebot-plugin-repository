from pydantic import BaseModel, Extra
from typing import List

class Config(BaseModel, extra=Extra.ignore):
    # 触发命令关键词
    sexphoto_command: List[str] = ["色图", "涩图", "涩涩", "色色"]
    
    # API地址
    sexphoto_api_url: str = "https://sex.nyan.run/api/v2/"
    
    # CD时长（秒）
    sexphoto_cd: int = 5
    
    # 全局最大获取数量限制
    sexphoto_max_num: int = 10
    
    # R18最大获取数量限制
    sexphoto_r18_max_num: int = 3
    
    # 是否启用R18功能
    sexphoto_enable_r18: bool = True
    
    # 是否默认开启群聊R18
    sexphoto_default_group_r18: bool = False
    
    # 白名单用户列表（可以不受限制启用R18）
    sexphoto_whitelist: List[int] = []
    
    # 普通图片撤回时间（秒），0表示不撤回
    sexphoto_normal_recall_time: int = 40
    
    # R18图片撤回时间（秒），0表示不撤回
    sexphoto_r18_recall_time: int = 20
    
    # 合并转发时显示的发送者名称
    sexphoto_sender_name: str = "色图插件"
    
    # 开启r18的命令关键词
    sexphoto_enable_command: List[str] = ["开启r18", "开启R18"]
    
    # 关闭r18的命令关键词
    sexphoto_disable_command: List[str] = ["关闭r18", "关闭R18"]