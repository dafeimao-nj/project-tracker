"""
项目跟进系统 - 数据模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


# 枚举类型
class ItemType(str, Enum):
    风控模型的搭建 = "风控模型的搭建"
    智能客服 = "智能客服"
    智能巡检 = "智能巡检"


class Status(str, Enum):
    未启动 = "未启动"
    进行中 = "进行中"
    遇阻 = "遇阻"
    待验收 = "待验收"
    已完成 = "已完成"
    已取消 = "已取消"


class Priority(str, Enum):
    低 = "低"
    中 = "中"
    高 = "高"
    紧急 = "紧急"


# 负责人列表
OWNERS = ["黄京", "夏韵", "孙培", "赵园园"]


# 数据模型
class WorkItem(BaseModel):
    """工作事项"""
    id: Optional[int] = None
    name: str  # 事项名称
    type: ItemType  # 事项类型
    owner: str  # 负责人
    status: Status = Status.未启动  # 状态
    priority: Priority = Priority.中  # 优先级
    create_time: datetime  # 创建时间
    expected_time: Optional[datetime] = None  # 预计完成时间
    actual_time: Optional[datetime] = None  # 实际完成时间
    progress: int = 0  # 进度百分比 (0-100)
    latest_update: str = ""  # 最新进展


class FollowUpRecord(BaseModel):
    """跟进记录"""
    id: Optional[int] = None
    item_id: int  # 关联的工作事项 ID
    time: datetime  # 跟进时间
    person: str  # 跟进人
    content: str  # 跟进内容


class WorkItemCreate(BaseModel):
    """创建工作事项请求"""
    name: str
    type: ItemType
    owner: str
    priority: Priority = Priority.中
    expected_time: Optional[datetime] = None


class WorkItemUpdate(BaseModel):
    """更新工作事项请求"""
    name: Optional[str] = None
    type: Optional[ItemType] = None
    owner: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    expected_time: Optional[datetime] = None
    actual_time: Optional[datetime] = None
    progress: Optional[int] = None
    latest_update: Optional[str] = None


class FollowUpCreate(BaseModel):
    """创建跟进记录请求"""
    item_id: int
    person: str
    content: str


# 统计数据
class Statistics(BaseModel):
    """统计数据"""
    total: int  # 总事项数
    not_started: int  # 未启动
    in_progress: int  # 进行中
    blocked: int  # 遇阻
    pending_review: int  # 待验收
    completed: int  # 已完成
    cancelled: int  # 已取消
    completion_rate: float  # 完成率
    overdue: int  # 超期数量
