"""
数据模型定义 - 使用 Pydantic 和 Dataclass
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class HabitStatus(str, Enum):
    """习惯状态"""
    COMPLETED = "completed"
    MISSED = "missed"
    PARTIAL = "partial"


class IntentType(str, Enum):
    """用户意图类型"""
    CHAT = "chat"  # 普通聊天
    HABIT_TRACKING = "habit_tracking"  # 习惯追踪
    DECISION_SUPPORT = "decision_support"  # 决策支持
    DAILY_BRIEF = "daily_brief"  # 每日简报
    REFLECTION = "reflection"  # 深度反思
    GOAL_BREAKDOWN = "goal_breakdown"  # 目标拆解


class User(BaseModel):
    """用户模型"""
    id: int
    username: str
    created_at: datetime = Field(default_factory=datetime.now)
    timezone: str = "Asia/Shanghai"
    preferences: Dict[str, Any] = Field(default_factory=dict)


class Habit(BaseModel):
    """习惯模型"""
    id: Optional[int] = None
    user_id: int
    name: str
    description: Optional[str] = None
    target_frequency: str = "daily"  # daily, weekly, custom
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class HabitRecord(BaseModel):
    """习惯记录"""
    id: Optional[int] = None
    habit_id: int
    user_id: int
    date: datetime
    status: HabitStatus
    context: Optional[str] = None  # 用户记录的上下文（为什么成功/失败）
    ai_feedback: Optional[str] = None  # AI 的反馈
    created_at: datetime = Field(default_factory=datetime.now)


class Reflection(BaseModel):
    """反思记录"""
    id: Optional[int] = None
    user_id: int
    date: datetime
    conversation: List[Dict[str, str]]  # [{"role": "ai", "content": "..."}, ...]
    insights: Optional[str] = None  # AI 生成的洞察
    patterns: Optional[List[str]] = None  # 识别的模式
    created_at: datetime = Field(default_factory=datetime.now)


class Decision(BaseModel):
    """决策记录"""
    id: Optional[int] = None
    user_id: int
    question: str
    factors: List[Dict[str, Any]]  # 决策因素
    recommendation: Optional[str] = None
    user_choice: Optional[str] = None
    outcome: Optional[str] = None  # 事后反馈
    created_at: datetime = Field(default_factory=datetime.now)


class Goal(BaseModel):
    """目标模型"""
    id: Optional[int] = None
    user_id: int
    title: str
    description: str
    deadline: Optional[datetime] = None
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    daily_tasks: List[str] = Field(default_factory=list)
    progress: float = 0.0
    status: str = "active"  # active, completed, abandoned
    created_at: datetime = Field(default_factory=datetime.now)


class DailyBrief(BaseModel):
    """每日简报"""
    id: Optional[int] = None
    user_id: int
    date: datetime
    energy_prediction: float  # 0-100
    key_focuses: List[Dict[str, str]]  # [{"time": "9-11", "task": "...", "reason": "..."}]
    risk_alerts: List[str]
    encouragement: str
    created_at: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class GraphState(BaseModel):
    """LangGraph 状态"""
    user_id: int
    messages: List[ChatMessage]
    intent: Optional[IntentType] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    next_node: Optional[str] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: int
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    intent: Optional[str] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
