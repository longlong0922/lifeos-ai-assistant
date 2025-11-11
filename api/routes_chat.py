"""
聊天相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
from app.models import ChatRequest, ChatResponse
from app.database import Database
from app.graph import LifeOSGraph
from app.llm_provider import get_llm_provider
from configs.settings import get_settings

router = APIRouter(prefix="/api", tags=["chat"])

# 全局实例（实际应用中应该使用依赖注入）
settings = get_settings()
db = Database(settings.DB_PATH)

# 构建 LLM 提供者参数
llm_kwargs = {
    "api_key": settings.OPENAI_API_KEY,
    "model": settings.OPENAI_MODEL
}

# 如果配置了 base_url，添加到参数中
if settings.OPENAI_BASE_URL:
    llm_kwargs["base_url"] = settings.OPENAI_BASE_URL

# 如果是混元，使用不同的参数
if settings.LLM_PROVIDER == "hunyuan":
    llm_kwargs = {
        "secret_id": settings.TENCENT_SECRET_ID,
        "secret_key": settings.TENCENT_SECRET_KEY,
        "model": settings.HUNYUAN_MODEL
    }

llm = get_llm_provider(
    provider_type=settings.LLM_PROVIDER,
    **llm_kwargs
)
graph = LifeOSGraph(db, llm)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口
    
    接收用户消息，返回 AI 响应
    """
    try:
        result = graph.run(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=result['response'],
            intent=result.get('intent'),
            suggestions=result.get('suggestions'),
            metadata=result.get('metadata')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION
    }


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: int):
    """
    获取用户统计信息
    """
    try:
        # 获取习惯统计
        habits = db.get_user_habits(user_id)
        habit_count = len(habits)
        
        # 获取总记录数
        total_records = 0
        for habit in habits:
            records = db.get_habit_records(habit['id'], limit=30)
            total_records += len(records)
        
        # 获取反思记录
        reflections = db.get_recent_reflections(user_id, limit=10)
        reflection_count = len(reflections)
        
        # 获取目标
        goals = db.get_user_goals(user_id)
        goal_count = len(goals)
        
        return {
            "user_id": user_id,
            "habits": {
                "total": habit_count,
                "records": total_records
            },
            "reflections": reflection_count,
            "goals": goal_count,
            "last_activity": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, session_id: Optional[str] = None, limit: int = 20):
    """
    获取聊天历史
    """
    try:
        history = db.get_chat_history(user_id, session_id, limit)
        return {
            "user_id": user_id,
            "session_id": session_id,
            "messages": history
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{user_id}")
async def clear_chat_history(user_id: int, session_id: Optional[str] = None):
    """
    清除聊天历史
    """
    # TODO: 实现清除历史的功能
    return {
        "message": "Chat history cleared",
        "user_id": user_id,
        "session_id": session_id
    }
