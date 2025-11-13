"""
LangGraph 状态定义
定义整个工作流的状态结构
"""

from typing import TypedDict, List, Dict, Optional, Annotated, Any
from datetime import datetime
import operator


class TaskItem(TypedDict, total=False):
    """单个任务项"""
    title: str  # 添加 title 字段
    description: str
    category: str
    importance: int  # 1-10
    urgency: int     # 1-10
    estimated_minutes: int
    can_defer: bool
    reason: str


class ActionStep(TypedDict):
    """行动步骤"""
    step_number: int
    description: str
    estimated_minutes: int
    difficulty: str  # easy/medium/hard
    expected_outcome: str
    type: str  # immediate/prep/calendar


class PersonalizationContext(TypedDict):
    """个性化上下文"""
    morning_productivity: bool
    evening_productivity: bool
    preferred_task_duration: int  # minutes
    long_term_goals: List[str]
    work_style: str
    energy_pattern: str


class AgentState(TypedDict, total=False):
    """
    LangGraph 工作流状态
    使用 Annotated 支持状态累积更新
    total=False 使所有字段变为可选
    """
    # 输入
    user_id: str
    user_input: str
    timestamp: str
    
    # 意图识别
    intent: str  # emotion/task/decision/mixed/unknown
    intent_confidence: float
    confidence: float  # 兼容字段
    
    # 任务分析
    raw_tasks: Annotated[List[str], operator.add]  # 提取的原始任务列表
    analyzed_tasks: Annotated[List[TaskItem], operator.add]  # 分析后的任务
    
    # 优先级排序
    high_priority: List[TaskItem]
    medium_priority: List[TaskItem]
    low_priority: List[TaskItem]
    deferrable: List[str]
    
    # 行动拆解
    recommended_task: Optional[TaskItem]
    action_steps: List[ActionStep]
    quick_start_action: Optional[ActionStep]
    
    # 个性化
    user_context: Optional[PersonalizationContext]
    personalized_adjustments: List[str]
    
    # 输出
    summary: str
    final_message: str
    final_output: str  # 最终输出（主要使用）
    next_action: str
    
    # 多轮对话
    session_id: str
    conversation_history: List[Dict]
    
    # 元数据
    processing_steps: Annotated[List[str], operator.add]  # 记录处理步骤
    errors: Annotated[List[str], operator.add]  # 错误记录
    
    # 控制流
    should_continue: bool
    needs_clarification: bool
