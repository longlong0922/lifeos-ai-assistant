"""
LangGraph 流程定义
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.models import GraphState, ChatMessage
from app.database import Database
from app.llm_provider import BaseLLMProvider
from app.nodes.router_node import router_node
from app.nodes.habit_node import habit_node
from app.nodes.plan_node import plan_node
from app.nodes.reflect_node import reflect_node
from app.nodes.coach_node import coach_node
from app.nodes.chat_node import chat_node


class LifeOSGraph:
    """LifeOS 状态图"""
    
    def __init__(self, db: Database, llm: BaseLLMProvider):
        self.db = db
        self.llm = llm
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建状态图"""
        
        # 创建图
        workflow = StateGraph(GraphState)
        
        # 添加节点
        workflow.add_node("router", lambda state: router_node(state))
        workflow.add_node("habit", lambda state: habit_node(state, self.db, self.llm))
        workflow.add_node("plan", lambda state: plan_node(state, self.db, self.llm))
        workflow.add_node("reflect", lambda state: reflect_node(state, self.db, self.llm))
        workflow.add_node("coach", lambda state: coach_node(state, self.db, self.llm))
        workflow.add_node("chat", lambda state: chat_node(state, self.llm))
        
        # 设置入口点
        workflow.set_entry_point("router")
        
        # 添加条件边：router 根据意图分发到不同节点
        workflow.add_conditional_edges(
            "router",
            lambda state: state.get("next_node") if isinstance(state, dict) else getattr(state, "next_node", "chat"),
            {
                "habit": "habit",
                "plan": "plan",
                "reflect": "reflect",
                "coach": "coach",
                "chat": "chat"
            }
        )
        
        # 所有功能节点完成后都结束
        workflow.add_edge("habit", END)
        workflow.add_edge("plan", END)
        workflow.add_edge("reflect", END)
        workflow.add_edge("coach", END)
        workflow.add_edge("chat", END)
        
        return workflow.compile()
    
    def run(self, user_id: int, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        运行图，处理用户消息
        
        Args:
            user_id: 用户 ID
            message: 用户消息
            session_id: 会话 ID（可选）
        
        Returns:
            响应字典
        """
        # 获取历史对话
        history = self.db.get_chat_history(user_id, session_id, limit=10)
        
        # 构建初始状态
        messages = [
            ChatMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=msg['timestamp']
            )
            for msg in history
        ]
        
        # 添加新消息
        new_message = ChatMessage(role="user", content=message)
        messages.append(new_message)
        
        # 保存用户消息
        self.db.save_chat_message(
            user_id=user_id,
            role="user",
            content=message,
            session_id=session_id
        )
        
        # 创建状态
        initial_state = GraphState(
            user_id=user_id,
            messages=messages,
            context={"session_id": session_id}
        )
        
        # 运行图
        try:
            result = self.graph.invoke(initial_state)
            
            # result 可能是 dict 或 GraphState 对象
            if isinstance(result, dict):
                messages = result.get('messages', [])
                intent = result.get('intent')
            else:
                messages = result.messages if hasattr(result, 'messages') else []
                intent = result.intent if hasattr(result, 'intent') else None
            
            # 获取 AI 响应（最后一条 assistant 消息）
            ai_messages = [msg for msg in messages if msg.role == "assistant"]
            if ai_messages:
                ai_response = ai_messages[-1]
                
                # 保存 AI 消息
                self.db.save_chat_message(
                    user_id=user_id,
                    role="assistant",
                    content=ai_response.content,
                    session_id=session_id,
                    metadata=ai_response.metadata
                )
                
                return {
                    "response": ai_response.content,
                    "intent": intent,
                    "suggestions": ai_response.metadata.get('suggestions') if ai_response.metadata else None,
                    "metadata": ai_response.metadata
                }
            else:
                return {
                    "response": "抱歉，我现在有点困惑。能再说一次吗？",
                    "intent": None,
                    "suggestions": None
                }
        
        except Exception as e:
            print(f"Graph execution error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": "抱歉，处理你的消息时出现了问题。请稍后再试。",
                "intent": None,
                "suggestions": None,
                "error": str(e)
            }
