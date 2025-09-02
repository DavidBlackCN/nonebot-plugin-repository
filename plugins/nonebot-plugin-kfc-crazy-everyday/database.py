import sqlite3
import os
from pathlib import Path
from typing import Optional

# 数据库文件路径
DB_PATH = Path(__file__).parent / "kfc_data.db"

def init_db():
    """初始化数据库"""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建群组设置表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_settings (
        group_id INTEGER PRIMARY KEY,
        daily_crazy BOOLEAN NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def get_group_setting(group_id: int) -> Optional[bool]:
    """获取群组设置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT daily_crazy FROM group_settings WHERE group_id = ?",
        (group_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def set_group_setting(group_id: int, daily_crazy: bool):
    """设置群组设置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO group_settings (group_id, daily_crazy) VALUES (?, ?)",
        (group_id, daily_crazy)
    )
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()