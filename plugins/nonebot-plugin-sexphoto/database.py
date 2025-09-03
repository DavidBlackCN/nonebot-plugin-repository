import sqlite3
import os
from pathlib import Path
from nonebot import get_driver
from .config import Config

# 获取配置
driver = get_driver()
plugin_config = Config.parse_obj(driver.config.dict())

# 数据库文件路径
DB_PATH = Path(__file__).parent / "group_r18.db"

def init_db():
    """初始化数据库"""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建群组设置表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_settings (
        group_id INTEGER PRIMARY KEY,
        r18_enabled INTEGER DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()

def set_group_r18(group_id: int, enabled: bool):
    """设置群聊R18状态"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 插入或更新记录
    cursor.execute('''
    INSERT OR REPLACE INTO group_settings (group_id, r18_enabled)
    VALUES (?, ?)
    ''', (group_id, 1 if enabled else 0))
    
    conn.commit()
    conn.close()

def get_group_r18(group_id: int) -> bool:
    """获取群聊R18状态，如果没有记录则返回默认值"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询群组设置
    cursor.execute('SELECT r18_enabled FROM group_settings WHERE group_id = ?', (group_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    # 如果数据库有记录则返回，否则返回默认配置
    if result:
        return bool(result[0])
    else:
        return plugin_config.sexphoto_default_group_r18

# 初始化数据库
init_db()