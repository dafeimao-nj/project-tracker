"""
项目跟进系统 - 数据库
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager
import os

# 数据库路径
DB_PATH = os.path.expanduser("~/.qclaw/workspace/项目跟进系统/data/workitems.db")


@contextmanager
def get_db():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """初始化数据库"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 工作事项表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                owner TEXT NOT NULL,
                status TEXT DEFAULT '未启动',
                priority TEXT DEFAULT '中',
                create_time TEXT NOT NULL,
                expected_time TEXT,
                actual_time TEXT,
                progress INTEGER DEFAULT 0,
                latest_update TEXT DEFAULT ''
            )
        """)
        
        # 跟进记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follow_ups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                time TEXT NOT NULL,
                person TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES work_items(id)
            )
        """)
        
        conn.commit()


# ========== 工作事项 CRUD ==========

def create_item(name: str, type: str, owner: str, priority: str = "中", 
                expected_time: Optional[str] = None) -> int:
    """创建工作事项"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO work_items (name, type, owner, priority, create_time, expected_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, type, owner, priority, datetime.now().isoformat(), expected_time))
        conn.commit()
        return cursor.lastrowid


def get_item(item_id: int) -> Optional[dict]:
    """获取单个工作事项"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM work_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_items() -> List[dict]:
    """获取所有工作事项"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM work_items ORDER BY create_time DESC")
        return [dict(row) for row in cursor.fetchall()]


def update_item(item_id: int, **kwargs) -> bool:
    """更新工作事项"""
    if not kwargs:
        return False
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = ?")
            if isinstance(value, datetime):
                values.append(value.isoformat())
            else:
                values.append(value)
    
    if not fields:
        return False
    
    values.append(item_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE work_items SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0


def delete_item(item_id: int) -> bool:
    """删除工作事项"""
    with get_db() as conn:
        cursor = conn.cursor()
        # 先删除关联的跟进记录
        cursor.execute("DELETE FROM follow_ups WHERE item_id = ?", (item_id,))
        # 再删除事项
        cursor.execute("DELETE FROM work_items WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0


# ========== 跟进记录 CRUD ==========

def create_follow_up(item_id: int, person: str, content: str) -> int:
    """创建跟进记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO follow_ups (item_id, time, person, content)
            VALUES (?, ?, ?, ?)
        """, (item_id, datetime.now().isoformat(), person, content))
        conn.commit()
        return cursor.lastrowid


def get_follow_ups(item_id: int) -> List[dict]:
    """获取工作事项的所有跟进记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM follow_ups 
            WHERE item_id = ? 
            ORDER BY time DESC
        """, (item_id,))
        return [dict(row) for row in cursor.fetchall()]


# ========== 统计 ==========

def get_statistics() -> dict:
    """获取统计数据"""
    items = get_all_items()
    total = len(items)
    
    status_count = {
        "未启动": 0,
        "进行中": 0,
        "遇阻": 0,
        "待验收": 0,
        "已完成": 0,
        "已取消": 0
    }
    
    overdue_count = 0
    now = datetime.now()
    
    for item in items:
        status_count[item["status"]] = status_count.get(item["status"], 0) + 1
        
        # 检查是否超期
        if item["expected_time"] and item["status"] not in ["已完成", "已取消"]:
            expected = datetime.fromisoformat(item["expected_time"])
            if expected < now:
                overdue_count += 1
    
    completed = status_count["已完成"]
    cancelled = status_count["已取消"]
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "not_started": status_count["未启动"],
        "in_progress": status_count["进行中"],
        "blocked": status_count["遇阻"],
        "pending_review": status_count["待验收"],
        "completed": completed,
        "cancelled": cancelled,
        "completion_rate": round(completion_rate, 1),
        "overdue": overdue_count
    }


# ========== 初始化 ==========

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成！")
