"""
LifeOS 交互式聊天界面
直接在命令行中和 AI 对话
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider
from app.database import Database
from app.graph import LifeOSGraph

def main():
    """交互式聊天主函数"""
    print("=" * 60)
    print("💬 LifeOS AI Assistant - 交互式聊天")
    print("=" * 60)
    
    # 初始化
    settings = get_settings()
    print(f"\n🤖 正在连接 {settings.LLM_PROVIDER}...")
    
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
    
    print("✅ 连接成功！\n")
    print("💡 使用提示:")
    print("   - 输入消息和 AI 对话")
    print("   - 输入 'quit' 或 'exit' 退出")
    print("   - 输入 'clear' 清空对话历史")
    print("   - 输入 'stats' 查看统计信息")
    print("\n" + "=" * 60)
    
    user_id = 1  # 默认用户 ID
    session_id = None
    
    print("\n🎯 你可以尝试:")
    print("   • '我今天完成了跑步！'")
    print("   • '帮我分析一下最近的习惯'")
    print("   • '今天要不要去健身房？'")
    print("   • '我想学 Python，怎么开始？'")
    print()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n😊 你: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！希望 LifeOS 帮到了你！")
                break
            
            elif user_input.lower() in ['clear', '清空']:
                session_id = None
                print("\n✅ 对话历史已清空")
                continue
            
            elif user_input.lower() in ['stats', '统计']:
                habits = db.get_user_habits(user_id)
                goals = db.get_user_goals(user_id)
                reflections = db.get_recent_reflections(user_id, limit=10)
                
                print(f"\n📊 你的统计:")
                print(f"   习惯: {len(habits)} 个")
                print(f"   目标: {len(goals)} 个")
                print(f"   反思: {len(reflections)} 条")
                continue
            
            # 调用 AI
            print("\n🤔 AI 正在思考...")
            
            result = graph.run(
                user_id=user_id,
                message=user_input,
                session_id=session_id
            )
            
            # 显示响应
            print(f"\n🤖 LifeOS: {result['response']}")
            
            # 显示意图
            if result.get('intent'):
                intent_emoji = {
                    'habit_tracking': '🏃',
                    'decision_support': '🔮',
                    'daily_brief': '📋',
                    'reflection': '💭',
                    'goal_breakdown': '🎯',
                    'chat': '💬'
                }
                intent = result['intent']
                emoji = intent_emoji.get(intent.value if hasattr(intent, 'value') else str(intent), '💬')
                print(f"\n{emoji} 识别意图: {intent}")
            
            # 显示建议
            if result.get('suggestions'):
                print("\n💡 你可以继续:")
                for suggestion in result['suggestions']:
                    print(f"   • {suggestion}")
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        
        except Exception as e:
            print(f"\n❌ 出错了: {e}")
            print("请重试或输入 'quit' 退出")

if __name__ == "__main__":
    main()
