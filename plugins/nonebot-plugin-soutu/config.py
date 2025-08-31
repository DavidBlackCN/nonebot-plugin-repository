from pydantic import BaseModel
from typing import List

class Config(BaseModel):
    # 触发命令
    img_commands: List[str] = ["搜图", "图图"]
    
    # API基础URL
    img_api_base: str = "https://api.suxun.site/api/imgv2"
    
    # 支持的图片分类 #可以再加一个r18选项
    valid_categories: List[str] = [
        "mp", "pc", "1080p", "silver", "furry", 
        "starry", "setu", "ws", "pixiv"
    ]
    
    # 需要撤回的图片分类
    recall_categories: List[str] = ["setu", "pixiv"]
    
    # 撤回时间（秒）
    recall_delay: int = 60
    
    # 是否启用撤回功能
    enable_recall: bool = True

# 创建配置实例
config = Config()