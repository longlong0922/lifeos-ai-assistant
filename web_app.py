"""
LifeOS AI Assistant - 现代化 Web UI 后端（改进版）
FastAPI + WebSocket 实时通信
支持所有 6 种意图 + 多轮对话 + 完整 Prompt 集成
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
import traceback

from agents.workflow_complete import create_complete_workflow
from agents.conversation_manager import ConversationManager

# 创建 FastAPI 应用
app = FastAPI(
    title="LifeOS AI Assistant",
    description="智能生活助理 - 完整版（支持 6 种意图 + 7 个专业 Prompt）",
    version="2.1.0"
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
conversation_manager = None
active_connections: Dict[str, WebSocket] = {}  # 改为字典，用 user_id 作为 key


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
    context_continuation: bool  # 新增：是否为上下文延续
    response: str
    processing_steps: List[str]
    analyzed_tasks: Optional[List[Dict[str, Any]]] = []  # 新增：提取的任务
    priority_analysis: Optional[Dict[str, Any]] = {}  # 新增：优先级分析
    timestamp: str


class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    total_turns: int
    started_at: str
    last_active_at: str
    intent_distribution: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    version: str
    workflow_status: str
    llm_provider: str
    active_connections: int
    supported_intents: List[str]
    prompts_loaded: List[str]


# ============================================================================
# 启动事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global workflow, conversation_manager
    
    print("="*70)
    print("🚀 正在启动 LifeOS AI Assistant...")
    print("="*70)
    
    # 检查静态文件
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        print(f"✅ 找到前端文件: {static_path}")
    else:
        print(f"⚠️  前端文件不存在: {static_path}")
        print(f"💡 提示: 创建 static/index.html 以启用 Web UI")
    
    # 初始化对话管理器
    try:
        db_path = os.getenv("DB_PATH", "lifeos_data.db")
        # 如果是相对路径，确保使用项目根目录
        if not os.path.isabs(db_path):
            db_path = Path(__file__).parent / db_path
        
        conversation_manager = ConversationManager(str(db_path))
        print(f"✅ 对话管理器初始化成功")
        print(f"   📁 数据库: {db_path}")
    except Exception as e:
        print(f"❌ 对话管理器初始化失败: {e}")
        print(f"⚠️  继续启动，但对话记忆功能将不可用")
        conversation_manager = None
    
    # 创建工作流（从环境变量读取配置）
    llm_provider = os.getenv("LLM_PROVIDER", "mock")
    model_name = os.getenv("MODEL_NAME", "hunyuan-large")
    
    print(f"\n🔧 配置信息:")
    print(f"   • LLM 提供商: {llm_provider}")
    print(f"   • 模型名称: {model_name}")
    if conversation_manager:
        print(f"   • 数据库: {db_path}")
    
    try:
        workflow = create_complete_workflow(
            llm_provider=llm_provider,
            model_name=model_name,
            db_path=str(db_path) if conversation_manager else "lifeos_data.db"
        )
        print(f"✅ 工作流初始化成功")
        
        # 显示支持的功能
        print(f"\n📚 支持的功能:")
        print(f"   ✓ 意图识别 (6 种)")
        print(f"   ✓ 任务管理 (智能提取+优先级分析)")
        print(f"   ✓ 情绪支持 (温暖回应)")
        print(f"   ✓ 习惯追踪 (计划设计)")
        print(f"   ✓ 目标规划 (多轮对话+路径拆解)")
        print(f"   ✓ 反思总结 (4D 模型)")
        print(f"   ✓ 闲聊对话 (自然交流)")
        print(f"   ✓ 个性化增强 (用户画像)")
        
    except Exception as e:
        print(f"❌ 工作流初始化失败: {e}")
        traceback.print_exc()
        workflow = None
    
    print("\n" + "="*70)
    print("✅ LifeOS AI Assistant 启动完成")
    print("="*70)
    print("📍 主页地址: http://localhost:8000")
    print("📡 WebSocket: ws://localhost:8000/ws/{user_id}")
    print("📚 API 文档: http://localhost:8000/docs")
    print("🏥 健康检查: http://localhost:8000/health")
    print("="*70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    print("\n🛑 正在关闭 LifeOS AI Assistant...")
    
    # 关闭所有 WebSocket 连接
    for user_id, ws in list(active_connections.items()):
        try:
            await ws.close()
            print(f"   ✓ 关闭用户 {user_id} 的连接")
        except:
            pass
    
    print("✅ 清理完成，再见！\n")


# ============================================================================
# 静态文件服务
# ============================================================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """返回网站图标"""
    favicon_path = Path(__file__).parent / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    from fastapi import Response
    return Response(status_code=204)


# 挂载静态文件目录
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
except Exception as e:
    print(f"⚠️  静态文件目录挂载失败: {e}")


# ============================================================================
# 页面路由
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页"""
    html_file = static_dir / "index.html"
    
    if html_file.exists():
        return FileResponse(html_file)
    else:
        # 返回一个临时的 Web UI（用于测试）
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LifeOS AI Assistant</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }
                .container {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 800px;
                    width: 100%;
                }
                h1 {
                    color: #667eea;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-align: center;
                }
                .subtitle {
                    color: #666;
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .feature {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }
                .feature-icon { font-size: 2em; margin-bottom: 10px; }
                .feature-title { font-weight: bold; margin-bottom: 5px; }
                .feature-desc { font-size: 0.9em; opacity: 0.9; }
                .links {
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-top: 30px;
                }
                .btn {
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    transition: all 0.3s;
                }
                .btn:hover {
                    background: #764ba2;
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .status {
                    background: #e8f5e9;
                    color: #2e7d32;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                    text-align: center;
                    font-weight: bold;
                }
                code {
                    background: #f5f5f5;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    color: #d63384;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 LifeOS AI Assistant</h1>
                <p class="subtitle">智能生活助理 - 你的个人 AI 伙伴</p>
                
                <div class="status">
                    ✅ 服务运行中 | API 版本 v2.1.0
                </div>
                
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">📋</div>
                        <div class="feature-title">任务管理</div>
                        <div class="feature-desc">智能提取、优先级排序</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">💚</div>
                        <div class="feature-title">情绪支持</div>
                        <div class="feature-desc">温暖倾听、贴心陪伴</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎯</div>
                        <div class="feature-title">习惯追踪</div>
                        <div class="feature-desc">打卡记录、数据分析</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🌟</div>
                        <div class="feature-title">目标规划</div>
                        <div class="feature-desc">拆解目标、路径设计</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">📝</div>
                        <div class="feature-title">反思总结</div>
                        <div class="feature-desc">定期回顾、持续改进</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">💬</div>
                        <div class="feature-title">自然对话</div>
                        <div class="feature-desc">多轮交流、上下文理解</div>
                    </div>
                </div>
                
                <div class="links">
                    <a href="/docs" class="btn">📚 API 文档</a>
                    <a href="/health" class="btn">🏥 健康检查</a>
                </div>
                
                <div style="margin-top: 30px; text-align: center; color: #666; font-size: 0.9em;">
                    <p>💡 提示: 创建 <code>static/index.html</code> 以启用完整 Web UI</p>
                    <p>🔗 WebSocket 地址: <code>ws://localhost:8000/ws/{user_id}</code></p>
                </div>
            </div>
        </body>
        </html>
        """)


# ============================================================================
# REST API 路由
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口 - 同步版本（HTTP POST）
    支持所有 6 种意图 + 完整功能
    """
    if not workflow:
        raise HTTPException(
            status_code=503,
            detail="工作流未初始化，请检查服务配置"
        )
    
    try:
        print(f"\n📨 收到聊天请求:")
        print(f"   • 用户: {request.user_id}")
        print(f"   • 会话: {request.session_id or '新会话'}")
        print(f"   • 消息: {request.message[:50]}...")
        
        # 执行工作流
        result = workflow.run(
            user_input=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        response = ChatResponse(
            success=True,
            session_id=result.get("session_id", ""),
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            context_continuation=result.get("context_continuation", False),
            response=result.get("final_output", ""),
            processing_steps=result.get("processing_steps", []),
            analyzed_tasks=result.get("analyzed_tasks", []),
            priority_analysis=result.get("priority_analysis", {}),
            timestamp=datetime.now().isoformat()
        )
        
        print(f"✅ 处理完成:")
        print(f"   • 意图: {response.intent} (置信度: {response.confidence:.2f})")
        print(f"   • 步骤: {len(response.processing_steps)} 步")
        print(f"   • 任务: {len(response.analyzed_tasks)} 个")
        
        return response
    
    except Exception as e:
        print(f"❌ 聊天处理失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """获取用户所有会话列表"""
    try:
        # TODO: 从数据库查询用户的所有会话
        # 当前返回模拟数据
        return {
            "user_id": user_id,
            "sessions": [],
            "total": 0,
            "message": "会话列表功能开发中"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str, last_n: int = 10):
    """获取会话历史记录"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="对话管理器未初始化")
    
    try:
        history = conversation_manager.get_conversation_history(
            session_id,
            last_n_turns=last_n
        )
        
        return {
            "session_id": session_id,
            "history": history,
            "total_turns": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/stats", response_model=SessionInfo)
async def get_session_stats(session_id: str):
    """获取会话统计信息"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="对话管理器未初始化")
    
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话（清空历史）"""
    # TODO: 实现会话删除功能
    return {
        "success": True,
        "message": f"会话 {session_id} 已删除",
        "note": "此功能开发中"
    }


# ============================================================================
# WebSocket 实时通信
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket 连接 - 实时对话
    支持完整的意图识别和多轮对话
    """
    await websocket.accept()
    active_connections[user_id] = websocket
    
    print(f"\n🔌 新连接: 用户 {user_id}")
    
    # 创建会话
    session_id = None
    if conversation_manager:
        session_id = conversation_manager.create_session(user_id)
        print(f"   ✓ 创建会话: {session_id}")
    
    # 发送欢迎消息
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "连接成功！我是 LifeOS 智能助理 😊\n\n我可以帮你：\n• 📋 管理任务和待办\n• 💚 提供情绪支持\n• 🎯 追踪习惯打卡\n• 🌟 规划目标路径\n• 📝 反思总结经验\n\n有什么可以帮你的吗？",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip()
            
            if not user_message:
                continue
            
            print(f"\n💬 [{user_id}] {user_message[:50]}...")
            
            # 发送"正在思考"状态
            await websocket.send_json({
                "type": "thinking",
                "message": "🤔 正在思考...",
                "timestamp": datetime.now().isoformat()
            })
            
            try:
                # 执行工作流（异步）
                result = await asyncio.to_thread(
                    workflow.run,
                    user_input=user_message,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # 更新 session_id（如果是首次）
                if not session_id:
                    session_id = result.get("session_id")
                
                intent = result.get("intent", "unknown")
                confidence = result.get("confidence", 0.0)
                
                print(f"✅ [{user_id}] 意图: {intent} ({confidence:.2f})")
                
                # 发送结果
                await websocket.send_json({
                    "type": "response",
                    "intent": intent,
                    "confidence": confidence,
                    "context_continuation": result.get("context_continuation", False),
                    "response": result.get("final_output", ""),
                    "processing_steps": result.get("processing_steps", []),
                    "analyzed_tasks": result.get("analyzed_tasks", []),
                    "priority_analysis": result.get("priority_analysis", {}),
                    "timestamp": datetime.now().isoformat()
                })
            
            except Exception as e:
                print(f"❌ [{user_id}] 处理失败: {e}")
                traceback.print_exc()
                
                await websocket.send_json({
                    "type": "error",
                    "message": f"抱歉，处理时出现问题：{str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        if user_id in active_connections:
            del active_connections[user_id]
        print(f"🔌 用户 {user_id} 断开连接")
    
    except Exception as e:
        print(f"❌ WebSocket 错误 [{user_id}]: {e}")
        traceback.print_exc()
        
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"连接出现问题: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass
        
        if user_id in active_connections:
            del active_connections[user_id]


# ============================================================================
# 健康检查与系统信息
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查 - 返回系统状态"""
    workflow_status = "initialized" if workflow else "not_initialized"
    llm_provider = os.getenv("LLM_PROVIDER", "mock")
    
    supported_intents = [
        "task_management",
        "emotion_support",
        "habit_tracking",
        "goal_setting",
        "reflection",
        "casual_chat"
    ]
    
    prompts_loaded = [
        "complete_intent_recognition_prompt",
        "enhanced_task_extraction_prompt",
        "personalization_prompt",
        "emotion_support_prompt",
        "habit_management_prompt",
        "goal_planning_prompt",
        "reflection_prompt"
    ]
    
    return HealthResponse(
        status="healthy" if workflow else "degraded",
        version="2.1.0",
        workflow_status=workflow_status,
        llm_provider=llm_provider,
        active_connections=len(active_connections),
        supported_intents=supported_intents,
        prompts_loaded=prompts_loaded
    )


@app.get("/api/intents")
async def get_supported_intents():
    """获取支持的意图列表"""
    return {
        "intents": [
            {
                "id": "task_management",
                "name": "任务管理",
                "description": "整理待办、智能排序、优先级分析",
                "icon": "📋",
                "examples": ["我今天要写报告、开会", "帮我整理任务"]
            },
            {
                "id": "emotion_support",
                "name": "情绪支持",
                "description": "倾听理解、温暖陪伴、情绪疏导",
                "icon": "💚",
                "examples": ["好累啊", "压力好大", "很焦虑"]
            },
            {
                "id": "habit_tracking",
                "name": "习惯追踪",
                "description": "习惯养成、打卡记录、数据统计",
                "icon": "🎯",
                "examples": ["我想养成跑步习惯", "帮我设计打卡计划"]
            },
            {
                "id": "goal_setting",
                "name": "目标规划",
                "description": "拆解目标、学习路径、多轮对话",
                "icon": "🌟",
                "examples": ["我想学 Python", "今年想考研"]
            },
            {
                "id": "reflection",
                "name": "反思总结",
                "description": "定期回顾、4D 模型、持续改进",
                "icon": "📝",
                "examples": ["总结这周", "反思学习状态"]
            },
            {
                "id": "casual_chat",
                "name": "闲聊对话",
                "description": "日常问候、功能咨询、自然交流",
                "icon": "💬",
                "examples": ["你好", "你有什么功能", "谢谢"]
            }
        ]
    }


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 LifeOS AI Assistant - Web Server")
    print("="*70)
    print("\n启动参数:")
    print(f"  • Host: 0.0.0.0")
    print(f"  • Port: 8000")
    print(f"  • Reload: True")
    print(f"  • LLM Provider: {os.getenv('LLM_PROVIDER', 'mock')}")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )