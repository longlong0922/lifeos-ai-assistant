"""
路由节点 - 识别用户意图
"""
from typing import Dict, Any
from app.models import GraphState, IntentType


def router_node(state: GraphState) -> Dict[str, Any]:
    """
    路由节点：分析用户消息，判断意图
    """
    if not state.messages:
        state.next_node = "chat"
        return {"next_node": "chat", "intent": IntentType.CHAT}
    
    last_message = state.messages[-1].content.lower()
    
    # 简单的关键词匹配（实际应用中可使用 LLM 分类）
    if any(keyword in last_message for keyword in ["习惯", "打卡", "跑步", "锻炼", "坚持"]):
        state.intent = IntentType.HABIT_TRACKING
        state.next_node = "habit"
        return {"intent": IntentType.HABIT_TRACKING, "next_node": "habit"}
    
    elif any(keyword in last_message for keyword in ["决策", "选择", "要不要", "应该", "还是"]):
        state.intent = IntentType.DECISION_SUPPORT
        state.next_node = "coach"
        return {"intent": IntentType.DECISION_SUPPORT, "next_node": "coach"}
    
    elif any(keyword in last_message for keyword in ["简报", "今天计划", "今日", "安排"]):
        state.intent = IntentType.DAILY_BRIEF
        state.next_node = "plan"
        return {"intent": IntentType.DAILY_BRIEF, "next_node": "plan"}
    
    elif any(keyword in last_message for keyword in ["反思", "回顾", "今天怎么样", "心情"]):
        state.intent = IntentType.REFLECTION
        state.next_node = "reflect"
        return {"intent": IntentType.REFLECTION, "next_node": "reflect"}
    
    elif any(keyword in last_message for keyword in ["目标", "想学", "想做", "计划学", "打算"]):
        state.intent = IntentType.GOAL_BREAKDOWN
        state.next_node = "coach"
        return {"intent": IntentType.GOAL_BREAKDOWN, "next_node": "coach"}
    
    else:
        state.intent = IntentType.CHAT
        state.next_node = "chat"
        return {"intent": IntentType.CHAT, "next_node": "chat"}
