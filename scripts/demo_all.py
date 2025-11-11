"""
LifeOS 功能演示 - 展示所有核心功能
"""
import sys
from pathlib import Path
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider
from app.database import Database
from app.graph import LifeOSGraph

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def demo_chat(graph, user_id):
    """演示1: 普通聊天"""
    print_section("💬 演示 1: 普通聊天")
    
    message = "你好！介绍一下你能帮我做什么？"
    print(f"用户: {message}")
    print("\nAI 思考中...")
    
    result = graph.run(user_id=user_id, message=message)
    print(f"\nLifeOS: {result['response']}\n")
    time.sleep(1)

def demo_habit_tracking(graph, user_id):
    """演示2: 习惯追踪"""
    print_section("🏃 演示 2: 习惯追踪与教练")
    
    messages = [
        "我今天完成了跑步，跑了5公里！",
        "今天太累了，没去跑步..."
    ]
    
    for message in messages:
        print(f"用户: {message}")
        print("AI 思考中...")
        
        result = graph.run(user_id=user_id, message=message)
        print(f"\nLifeOS: {result['response']}\n")
        time.sleep(2)

def demo_decision_support(graph, user_id):
    """演示3: 决策支持"""
    print_section("🔮 演示 3: 决策支持")
    
    message = "今天晚上要不要去健身房？我有点累但也想锻炼。"
    print(f"用户: {message}")
    print("AI 思考中...")
    
    result = graph.run(user_id=user_id, message=message)
    print(f"\nLifeOS: {result['response']}\n")
    time.sleep(1)

def demo_goal_breakdown(graph, user_id):
    """演示4: 目标拆解"""
    print_section("🎯 演示 4: 目标拆解")
    
    message = "我想学习 Python 编程，但不知道从哪里开始。"
    print(f"用户: {message}")
    print("AI 思考中...")
    
    result = graph.run(user_id=user_id, message=message)
    print(f"\nLifeOS: {result['response']}\n")
    time.sleep(1)

def demo_reflection(graph, user_id):
    """演示5: 深度反思"""
    print_section("💭 演示 5: 深度反思")
    
    message = "今天感觉挺好的，工作很顺利，晚上还锻炼了。"
    print(f"用户: {message}")
    print("AI 思考中...")
    
    result = graph.run(user_id=user_id, message=message)
    print(f"\nLifeOS: {result['response']}\n")
    time.sleep(1)

def show_stats(db, user_id):
    """显示统计信息"""
    print_section("📊 用户统计")
    
    habits = db.get_user_habits(user_id)
    goals = db.get_user_goals(user_id)
    reflections = db.get_recent_reflections(user_id, limit=10)
    
    print(f"习惯数量: {len(habits)}")
    if habits:
        print("\n习惯列表:")
        for habit in habits[:5]:
            print(f"  • {habit['name']}")
    
    print(f"\n目标数量: {len(goals)}")
    if goals:
        print("\n目标列表:")
        for goal in goals[:5]:
            print(f"  • {goal['title']}")
    
    print(f"\n反思记录: {len(reflections)} 条")

def main():
    """主演示函数"""
    print("\n" + "=" * 60)
    print("🌟  LifeOS AI Assistant - 功能演示")
    print("=" * 60)
    
    # 初始化
    settings = get_settings()
    print(f"\n🤖 使用 {settings.LLM_PROVIDER} ({settings.HUNYUAN_MODEL if settings.LLM_PROVIDER == 'hunyuan' else settings.OPENAI_MODEL})")
    
    # 构建 LLM 参数
    llm_kwargs = {}
    if settings.LLM_PROVIDER == "hunyuan":
        llm_kwargs = {
            "secret_id": settings.TENCENT_SECRET_ID,
            "secret_key": settings.TENCENT_SECRET_KEY,
            "model": settings.HUNYUAN_MODEL
        }
    elif settings.LLM_PROVIDER == "openai":
        llm_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL
        }
        if settings.OPENAI_BASE_URL:
            llm_kwargs["base_url"] = settings.OPENAI_BASE_URL
    
    llm = get_llm_provider(provider_type=settings.LLM_PROVIDER, **llm_kwargs)
    db = Database(settings.DB_PATH)
    graph = LifeOSGraph(db, llm)
    
    print("✅ 初始化完成！\n")
    
    user_id = 1
    
    print("🎬 演示将展示 LifeOS 的 5 大核心功能：")
    print("   1. 💬 智能对话")
    print("   2. 🏃 习惯追踪与教练")
    print("   3. 🔮 决策支持")
    print("   4. 🎯 目标拆解")
    print("   5. 💭 深度反思")
    
    input("\n按回车键开始演示...")
    
    try:
        # 运行所有演示
        demo_chat(graph, user_id)
        demo_habit_tracking(graph, user_id)
        demo_decision_support(graph, user_id)
        demo_goal_breakdown(graph, user_id)
        demo_reflection(graph, user_id)
        
        # 显示统计
        show_stats(db, user_id)
        
        print("\n" + "=" * 60)
        print("✅ 演示完成！")
        print("=" * 60)
        
        print("\n🚀 现在你可以:")
        print("   • 运行 'python scripts/chat.py' 开始交互式对话")
        print("   • 运行 'python run.py' 启动 Web 服务")
        print("   • 访问 http://localhost:8000/docs 查看 API 文档")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  演示已停止")
    except Exception as e:
        print(f"\n❌ 出错了: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
