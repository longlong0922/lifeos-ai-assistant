"""
深度反思对话节点
"""
from typing import Dict
from datetime import datetime
from app.models import GraphState, ChatMessage
from app.database import Database
from app.llm_provider import BaseLLMProvider, LIFE_OS_SYSTEM_PROMPT, REFLECTION_PROMPT


def reflect_node(state: GraphState, db: Database, llm: BaseLLMProvider) -> Dict:
    """
    反思节点：进行苏格拉底式对话，帮助用户深度思考
    """
    user_id = state.user_id
    user_message = state.messages[-1].content
    
    # 获取最近的反思记录
    recent_reflections = db.get_recent_reflections(user_id, limit=5)
    
    # 分析模式：找出重复出现的关键词/主题
    patterns = []
    if recent_reflections:
        all_conversations = []
        for ref in recent_reflections:
            all_conversations.extend([msg['content'] for msg in ref['conversation'] if msg['role'] == 'user'])
        
        # 简单的模式识别（实际应用中可以使用 NLP）
        keywords_count = {}
        emotion_keywords = ['累', '烦', '焦虑', '压力', '无力', '等待', '扯皮', '开心', '满足']
        
        for conv in all_conversations:
            for keyword in emotion_keywords:
                if keyword in conv:
                    keywords_count[keyword] = keywords_count.get(keyword, 0) + 1
        
        # 找出重复 3 次以上的关键词
        patterns = [f"你最近 {count} 次提到'{keyword}'" 
                   for keyword, count in keywords_count.items() if count >= 3]
    
    # 构建对话历史（最近 5 轮）
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in state.messages[-10:]  # 最近 10 条消息
    ]
    
    # 构建 prompt
    reflection_summary = "\n".join([
        f"- {ref['date']}: {ref['insights'] or '进行了对话'}"
        for ref in recent_reflections[:3]
    ]) or "这是你的第一次深度反思"
    
    patterns_text = "\n".join(patterns) if patterns else "暂未发现明显模式"
    
    prompt = REFLECTION_PROMPT.format(
        recent_reflections=reflection_summary,
        patterns=patterns_text,
        conversation=str(conversation_history[-4:])  # 最近 2 轮对话
    )
    
    # 调用 LLM
    messages = [
        {"role": "system", "content": LIFE_OS_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    response = llm.chat(messages, temperature=0.7, max_tokens=800)
    
    # 如果发现重复模式，生成洞察
    insights = None
    if patterns:
        insights = f"模式识别：{'; '.join(patterns)}。这可能值得深入思考。"
    
    # 保存反思记录（每次对话）
    conversation_to_save = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response}
    ]
    
    db.save_reflection(
        user_id=user_id,
        date=datetime.now(),
        conversation=conversation_to_save,
        insights=insights,
        patterns=patterns
    )
    
    state.messages.append(ChatMessage(role="assistant", content=response))
    
    return {"messages": state.messages, "next_node": None}
