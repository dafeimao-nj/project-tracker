"""
项目跟进系统 - API 服务
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from models import (
    WorkItem, WorkItemCreate, WorkItemUpdate,
    FollowUpRecord, FollowUpCreate, Statistics,
    ItemType, Status, Priority, OWNERS
)
import database

# 初始化数据库
database.init_db()

# 创建 FastAPI 应用
app = FastAPI(title="项目跟进系统 API", version="1.0.0")

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 工作事项 API ==========

@app.get("/api/items", response_model=list[WorkItem])
async def get_items():
    """获取所有工作事项"""
    items = database.get_all_items()
    return [
        WorkItem(
            id=item["id"],
            name=item["name"],
            type=item["type"],
            owner=item["owner"],
            status=item["status"],
            priority=item["priority"],
            create_time=datetime.fromisoformat(item["create_time"]),
            expected_time=datetime.fromisoformat(item["expected_time"]) if item["expected_time"] else None,
            actual_time=datetime.fromisoformat(item["actual_time"]) if item["actual_time"] else None,
            progress=item["progress"],
            latest_update=item["latest_update"]
        )
        for item in items
    ]


@app.get("/api/items/{item_id}", response_model=WorkItem)
async def get_item(item_id: int):
    """获取单个工作事项"""
    item = database.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="工作事项不存在")
    
    return WorkItem(
        id=item["id"],
        name=item["name"],
        type=item["type"],
        owner=item["owner"],
        status=item["status"],
        priority=item["priority"],
        create_time=datetime.fromisoformat(item["create_time"]),
        expected_time=datetime.fromisoformat(item["expected_time"]) if item["expected_time"] else None,
        actual_time=datetime.fromisoformat(item["actual_time"]) if item["actual_time"] else None,
        progress=item["progress"],
        latest_update=item["latest_update"]
    )


@app.post("/api/items", response_model=WorkItem)
async def create_item(item: WorkItemCreate):
    """创建工作事项"""
    # 验证负责人
    if item.owner not in OWNERS:
        raise HTTPException(status_code=400, detail=f"负责人必须是: {', '.join(OWNERS)}")
    
    item_id = database.create_item(
        name=item.name,
        type=item.type.value,
        owner=item.owner,
        priority=item.priority.value,
        expected_time=item.expected_time.isoformat() if item.expected_time else None
    )
    
    return await get_item(item_id)


@app.put("/api/items/{item_id}", response_model=WorkItem)
async def update_item(item_id: int, item: WorkItemUpdate):
    """更新工作事项"""
    # 检查事项是否存在
    existing = database.get_item(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="工作事项不存在")
    
    # 构建更新数据
    update_data = {}
    if item.name is not None:
        update_data["name"] = item.name
    if item.type is not None:
        update_data["type"] = item.type.value
    if item.owner is not None:
        if item.owner not in OWNERS:
            raise HTTPException(status_code=400, detail=f"负责人必须是: {', '.join(OWNERS)}")
        update_data["owner"] = item.owner
    if item.status is not None:
        update_data["status"] = item.status.value
    if item.priority is not None:
        update_data["priority"] = item.priority.value
    if item.expected_time is not None:
        update_data["expected_time"] = item.expected_time.isoformat()
    if item.actual_time is not None:
        update_data["actual_time"] = item.actual_time.isoformat()
    if item.progress is not None:
        update_data["progress"] = item.progress
    if item.latest_update is not None:
        update_data["latest_update"] = item.latest_update
    
    database.update_item(item_id, **update_data)
    return await get_item(item_id)


@app.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    """删除工作事项"""
    if not database.delete_item(item_id):
        raise HTTPException(status_code=404, detail="工作事项不存在")
    return {"message": "删除成功"}


# ========== 跟进记录 API ==========

@app.get("/api/items/{item_id}/follow-ups", response_model=list[FollowUpRecord])
async def get_follow_ups(item_id: int):
    """获取工作事项的所有跟进记录"""
    records = database.get_follow_ups(item_id)
    return [
        FollowUpRecord(
            id=record["id"],
            item_id=record["item_id"],
            time=datetime.fromisoformat(record["time"]),
            person=record["person"],
            content=record["content"]
        )
        for record in records
    ]


@app.post("/api/follow-ups", response_model=FollowUpRecord)
async def create_follow_up(follow_up: FollowUpCreate):
    """创建跟进记录"""
    # 检查事项是否存在
    item = database.get_item(follow_up.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="工作事项不存在")
    
    record_id = database.create_follow_up(
        item_id=follow_up.item_id,
        person=follow_up.person,
        content=follow_up.content
    )
    
    # 更新事项的最新进展
    database.update_item(
        follow_up.item_id,
        latest_update=follow_up.content
    )
    
    records = database.get_follow_ups(follow_up.item_id)
    record = next(r for r in records if r["id"] == record_id)
    
    return FollowUpRecord(
        id=record["id"],
        item_id=record["item_id"],
        time=datetime.fromisoformat(record["time"]),
        person=record["person"],
        content=record["content"]
    )


# ========== 统计 API ==========

@app.get("/api/statistics", response_model=Statistics)
async def get_statistics():
    """获取统计数据"""
    stats = database.get_statistics()
    return Statistics(**stats)


# ========== 元数据 API ==========

@app.get("/api/meta/types")
async def get_types():
    """获取事项类型列表"""
    return [t.value for t in ItemType]


@app.get("/api/meta/statuses")
async def get_statuses():
    """获取状态列表"""
    return [s.value for s in Status]


@app.get("/api/meta/priorities")
async def get_priorities():
    """获取优先级列表"""
    return [p.value for p in Priority]


@app.get("/api/meta/owners")
async def get_owners():
    """获取负责人列表"""
    return OWNERS


# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
