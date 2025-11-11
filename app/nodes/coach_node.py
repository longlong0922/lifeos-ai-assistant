"""
教练节点 - 决策支持和目标拆解
"""
from typing import Dict
from datetime import datetime, timedelta
from app.models import GraphState, ChatMessage
from app.database import Database
from app.llm_provider import BaseLLMProvider, LIFE_OS_SYSTEM_PROMPT, DECISION_SUPPORT_PROMPT, GOAL_BREAKDOWN_PROMPT


def coach_node(state: GraphState, db: Database, llm: BaseLLMProvider) -> Dict:
    """
    教练节点：处理决策支持和目标拆解
    """
    user_id = state.user_id
    user_message = state.messages[-1].content
    
    # 判断是决策还是目标拆解
    is_goal = any(keyword in user_message for keyword in ["想学", "想做", "目标", "计划学"])
    
    if is_goal:
        return _handle_goal_breakdown(state, user_id, user_message, db, llm)
    else:
        return _handle_decision_support(state, user_id, user_message, db, llm)


def _handle_decision_support(state: GraphState, user_id: int, user_message: str, 
                              db: Database, llm: BaseLLMProvider) -> Dict:
    """处理决策支持"""
    
    # 获取历史决策（暂时简化，实际应该从数据库获取）
    decision_history = "暂无历史决策记录"
    
    # 从反思记录中获取用户的状态信息
    recent_reflections = db.get_recent_reflections(user_id, limit=3)
    if recent_reflections:
        recent_states = []
        for ref in recent_reflections:
            user_msgs = [msg['content'] for msg in ref['conversation'] if msg['role'] == 'user']
            recent_states.extend(user_msgs[:2])
        
        decision_history = f"最近的状态：\n" + "\n".join(recent_states[:3])
    
    # 构建 prompt
    prompt = DECISION_SUPPORT_PROMPT.format(
        decision_history=decision_history,
        question=user_message
    )
    
    # 调用 LLM
    messages = [
        {"role": "system", "content": LIFE_OS_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    response = llm.chat(messages, temperature=0.7, max_tokens=1000)
    
    # 保存决策记录
    factors = [
        {"factor": "历史模式", "weight": "基于过去经验"},
        {"factor": "当前状态", "weight": "当前情绪和压力水平"}
    ]
    
    db.save_decision(
        user_id=user_id,
        question=user_message,
        factors=factors,
        recommendation=response[:200]  # 保存部分响应
    )
    
    state.messages.append(ChatMessage(role="assistant", content=response))
    return {"messages": state.messages, "next_node": None}


def _handle_goal_breakdown(state: GraphState, user_id: int, user_message: str,
                           db: Database, llm: BaseLLMProvider) -> Dict:
    """处理目标拆解"""
    
    # 检查用户是否已有活跃目标
    active_goals = db.get_user_goals(user_id, status="active")
    
    # 构建 prompt
    prompt = GOAL_BREAKDOWN_PROMPT.format(
        goal=user_message
    )
    
    # 调用 LLM
    messages = [
        {"role": "system", "content": LIFE_OS_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    response = llm.chat(messages, temperature=0.7, max_tokens=1500)
    
    # 创建目标（简化版）
    goal_title = user_message[:50]  # 取前 50 字符作为标题
    
    # 生成 21 天计划的里程碑
    milestones = [
        {"week": 1, "focus": "建立习惯", "description": "不求完美，求每天做"},
        {"week": 2, "focus": "输出练习", "description": "开始有成果产出"},
        {"week": 3, "focus": "巩固提升", "description": "形成自然习惯"}
    ]
    
    daily_tasks = ["每天投入 30 分钟", "记录进展", "反思调整"]
    
    deadline = datetime.now() + timedelta(days=21)
    
    goal_id = db.create_goal(
        user_id=user_id,
        title=goal_title,
        description=user_message,
        deadline=deadline,
        milestones=milestones,
        daily_tasks=daily_tasks
    )
    
    state.messages.append(ChatMessage(
        role="assistant", 
        content=response,
        metadata={"goal_id": goal_id}
    ))
    
    return {"messages": state.messages, "next_node": None}
