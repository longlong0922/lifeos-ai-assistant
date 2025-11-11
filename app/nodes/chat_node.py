"""
普通聊天节点
"""
from typing import Dict
from app.models import GraphState, ChatMessage
from app.llm_provider import BaseLLMProvider, LIFE_OS_SYSTEM_PROMPT


def chat_node(state: GraphState, llm: BaseLLMProvider) -> Dict:
    """
    普通聊天节点：处理一般性对话
    """
    user_message = state.messages[-1].content
    
    # 构建对话历史
    messages = [{"role": "system", "content": LIFE_OS_SYSTEM_PROMPT}]
    
    # 添加最近的对话历史（最多 10 条）
    for msg in state.messages[-10:]:
        messages.append({
            "role": "user" if msg.role == "user" else "assistant",
            "content": msg.content
        })
    
    # 调用 LLM
    response = llm.chat(messages, temperature=0.8, max_tokens=800)
    
    # 添加快捷建议
    suggestions = [
        "🎯 查看今日简报",
        "📊 记录习惯",
        "💭 深度反思",
        "🔮 做个决策"
    ]
    
    state.messages.append(ChatMessage(
        role="assistant",
        content=response,
        metadata={"suggestions": suggestions}
    ))
    
    return {"messages": state.messages, "next_node": None}
