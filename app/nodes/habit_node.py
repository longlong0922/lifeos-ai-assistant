"""
习惯追踪节点
"""
from typing import Dict
from datetime import datetime
from app.models import GraphState, ChatMessage, HabitStatus
from app.database import Database
from app.llm_provider import BaseLLMProvider, LIFE_OS_SYSTEM_PROMPT, HABIT_COACHING_PROMPT


def habit_node(state: GraphState, db: Database, llm: BaseLLMProvider) -> Dict:
    """
    习惯追踪节点：分析用户的习惯记录，提供个性化指导
    """
    user_id = state.user_id
    user_message = state.messages[-1].content
    
    # 获取用户的习惯数据
    habits = db.get_user_habits(user_id)
    
    if not habits:
        response = "我注意到你还没有设置任何习惯。要不要从一个小目标开始？比如每天 10 分钟的某个活动？"
        state.messages.append(ChatMessage(role="assistant", content=response))
        return {"messages": state.messages, "next_node": None}
    
    # 获取最近的习惯记录
    habit_records = []
    for habit in habits:
        records = db.get_habit_records(habit['id'], limit=7)
        habit_records.extend(records)
    
    # 分析模式
    if habit_records:
        completed_count = len([r for r in habit_records if r['status'] == HabitStatus.COMPLETED.value])
        total_count = len(habit_records)
        success_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        # 找出成功的时间段模式（简化版）
        contexts = [r['context'] for r in habit_records if r['context'] and r['status'] == HabitStatus.COMPLETED.value]
    else:
        success_rate = 0
        contexts = []
    
    # 构建 prompt
    # 安全地格式化习惯数据，避免特殊字符
    habit_names = ', '.join([h['name'] for h in habits])
    success_contexts = ', '.join(contexts[:3]) if contexts else '暂无'
    
    habit_data_summary = f"""
习惯列表: {habit_names}
最近 7 天记录: {len(habit_records)} 条
完成率: {success_rate:.1f}%
成功情境: {success_contexts}
    """.strip()
    
    prompt = HABIT_COACHING_PROMPT.format(
        habit_data=habit_data_summary,
        user_message=user_message
    )
    
    # 调用 LLM
    messages = [
        {"role": "system", "content": LIFE_OS_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    response = llm.chat(messages, temperature=0.7)
    
    # 保存对话
    state.messages.append(ChatMessage(role="assistant", content=response))
    
    # 如果用户提到完成或未完成，记录到数据库
    if any(keyword in user_message for keyword in ["完成了", "做了", "跑了", "打卡"]):
        # 假设是第一个习惯
        db.add_habit_record(
            habit_id=habits[0]['id'],
            user_id=user_id,
            date=datetime.now(),
            status=HabitStatus.COMPLETED.value,
            context=user_message
        )
    elif any(keyword in user_message for keyword in ["没做", "放弃", "忘了", "没时间"]):
        db.add_habit_record(
            habit_id=habits[0]['id'],
            user_id=user_id,
            date=datetime.now(),
            status=HabitStatus.MISSED.value,
            context=user_message
        )
    
    return {"messages": state.messages, "next_node": None}
