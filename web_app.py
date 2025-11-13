"""
LifeOS AI Assistant - 现代化 Web UI 后端
FastAPI + WebSocket 实时通信
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import os
from pathlib import Path

from agents.workflow_complete import create_complete_workflow
from agents.conversation_manager import ConversationManager

# 创建 FastAPI 应用
app = FastAPI(
    title="LifeOS AI Assistant",
    description="智能生活助理 - 完整版",
    version="2.0.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
workflow = None
conversation_manager = ConversationManager()
active_connections: List[WebSocket] = []


# ============================================================================
# Pydantic 模型
# ============================================================================

class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    success: bool
    session_id: str
    intent: str
    confidence: float
    response: str
    processing_steps: List[str]
    timestamp: str


class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    total_turns: int
    started_at: str
    last_active_at: str
    intent_distribution: Dict[str, int]


# ============================================================================
# 启动事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global workflow
    
    print("🚀 正在启动 LifeOS AI Assistant...")
    
    # 检查静态文件
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        print(f"✅ 找到静态文件: {static_path}")
    else:
        print(f"⚠️ 静态文件不存在: {static_path}")
    
    # 创建工作流（自动从环境变量读取配置）
    try:
        workflow = create_complete_workflow(
            llm_provider=os.getenv("LLM_PROVIDER", "mock"),
            model_name=os.getenv("HUNYUAN_MODEL", "hunyuan-large")
        )
        print("✅ 工作流初始化成功")
    except Exception as e:
        print(f"❌ 工作流初始化失败: {e}")
        workflow = None
    
    print("=" * 60)
    print("✅ LifeOS AI Assistant 已启动")
    print("📍 访问地址: http://localhost:8000")
    print("📡 WebSocket: ws://localhost:8000/ws/{user_id}")
    print("📚 API 文档: http://localhost:8000/docs")
    print("=" * 60)


# ============================================================================
# 静态文件服务
# ============================================================================

# 挂载静态文件目录
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
except Exception as e:
    print(f"⚠️ 静态文件目录挂载失败: {e}")


# ============================================================================
# API 路由
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页"""
    html_file = static_dir / "index.html"
    print(f"📄 请求主页，文件路径: {html_file}")
    print(f"📄 文件是否存在: {html_file.exists()}")
    
    if html_file.exists():
        print(f"✅ 返回 index.html (大小: {html_file.stat().st_size} 字节)")
        return FileResponse(html_file)
    else:
        print(f"⚠️ index.html 不存在，返回占位页面")
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LifeOS AI Assistant</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: white;
                    text-align: center;
                    padding: 20px;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    border-radius: 20px;
                    max-width: 600px;
                }
                h1 { font-size: 2.5em; margin-bottom: 20px; }
                p { font-size: 1.2em; margin: 10px 0; }
                a { color: #ffd700; text-decoration: none; font-weight: bold; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 LifeOS AI Assistant</h1>
                <p>Web UI 正在构建中...</p>
                <p>静态文件路径: <code>static/index.html</code></p>
                <p>请访问 <a href="/docs">/docs</a> 查看 API 文档</p>
                <p>或访问 <a href="/health">/health</a> 检查服务状态</p>
            </div>
        </body>
        </html>
        """)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口 - 同步版本
    """
    try:
        # 执行工作流
        result = workflow.run(
            user_input=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        return ChatResponse(
            success=True,
            session_id=result.get("session_id", ""),
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            response=result.get("final_output", ""),
            processing_steps=result.get("processing_steps", []),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """获取用户所有会话"""
    # TODO: 实现会话列表查询
    return {"user_id": user_id, "sessions": []}


@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str, last_n: int = 10):
    """获取会话历史"""
    history = conversation_manager.get_conversation_history(session_id, last_n)
    return {"session_id": session_id, "history": history}


@app.get("/api/session/{session_id}/stats", response_model=SessionInfo)
async def get_session_stats(session_id: str):
    """获取会话统计"""
    stats = conversation_manager.get_session_stats(session_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return SessionInfo(
        session_id=session_id,
        user_id=stats.get("user_id", ""),
        total_turns=stats.get("total_turns", 0),
        started_at=stats.get("started_at", ""),
        last_active_at=stats.get("last_active_at", ""),
        intent_distribution=stats.get("intent_distribution", {})
    )


# ============================================================================
# WebSocket 实时通信
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket 连接 - 实时对话
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    # 创建会话
    session_id = conversation_manager.create_session(user_id)
    
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "连接成功！我是 LifeOS 智能助理 😊"
    })
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            # 发送"正在思考"状态
            await websocket.send_json({
                "type": "thinking",
                "message": "🤔 正在思考..."
            })
            
            # 执行工作流（异步）
            result = await asyncio.to_thread(
                workflow.run,
                user_input=user_message,
                user_id=user_id,
                session_id=session_id
            )
            
            # 发送结果
            await websocket.send_json({
                "type": "response",
                "intent": result.get("intent", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "response": result.get("final_output", ""),
                "processing_steps": result.get("processing_steps", []),
                "timestamp": datetime.now().isoformat()
            })
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"🔌 用户 {user_id} 断开连接")
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"发生错误: {str(e)}"
        })
        active_connections.remove(websocket)


# ============================================================================
# 健康检查
# ============================================================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "workflow_initialized": workflow is not None,
        "active_connections": len(active_connections)
    }


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
