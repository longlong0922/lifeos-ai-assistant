"""
LifeOS 快速演示脚本
展示五大核心功能
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Database
from app.llm_provider import MockLLMProvider
from app.graph import LifeOSGraph
from configs.settings import get_settings


def print_section(title: str):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_chat(graph: LifeOSGraph, user_id: int):
    """演示普通聊天"""
    print_section("1. 普通聊天")
    
    result = graph.run(user_id, "你好，我想了解一下你能帮我做什么？")
    print(f"用户: 你好，我想了解一下你能帮我做什么？")
    print(f"AI: {result['response']}\n")


def demo_habit_tracking(graph: LifeOSGraph, user_id: int):
    """演示习惯追踪"""
    print_section("2. 习惯追踪")
    
    result = graph.run(user_id, "我今天完成了跑步，感觉很不错！")
    print(f"用户: 我今天完成了跑步，感觉很不错！")
    print(f"AI: {result['response']}\n")


def demo_daily_brief(graph: LifeOSGraph, user_id: int):
    """演示每日简报"""
    print_section("3. 每日简报")
    
    result = graph.run(user_id, "给我看看今天的简报")
    print(f"用户: 给我看看今天的简报")
    print(f"AI: {result['response']}\n")


def demo_reflection(graph: LifeOSGraph, user_id: int):
    """演示深度反思"""
    print_section("4. 深度反思")
    
    result = graph.run(user_id, "今天感觉有点累，不知道为什么")
    print(f"用户: 今天感觉有点累，不知道为什么")
    print(f"AI: {result['response']}\n")


def demo_decision_support(graph: LifeOSGraph, user_id: int):
    """演示决策支持"""
    print_section("5. 决策支持")
    
    result = graph.run(user_id, "周末要不要去爬山？我有点纠结")
    print(f"用户: 周末要不要去爬山？我有点纠结")
    print(f"AI: {result['response']}\n")


def demo_goal_breakdown(graph: LifeOSGraph, user_id: int):
    """演示目标拆解"""
    print_section("6. 目标拆解")
    
    result = graph.run(user_id, "我想学好 Python 编程")
    print(f"用户: 我想学好 Python 编程")
    print(f"AI: {result['response']}\n")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  LifeOS AI Assistant - 功能演示")
    print("="*60)
    
    # 初始化
    settings = get_settings()
    db = Database(settings.DB_PATH)
    llm = MockLLMProvider()
    graph = LifeOSGraph(db, llm)
    
    # 使用演示用户 ID
    user_id = 1
    
    # 演示各个功能
    demo_chat(graph, user_id)
    demo_habit_tracking(graph, user_id)
    demo_daily_brief(graph, user_id)
    demo_reflection(graph, user_id)
    demo_decision_support(graph, user_id)
    demo_goal_breakdown(graph, user_id)
    
    # 总结
    print_section("演示完成")
    print("✅ LifeOS 的六大核心功能展示完毕！")
    print("\n💡 提示:")
    print("  - 启动服务: python app/main.py")
    print("  - 访问文档: http://localhost:8000/docs")
    print("  - 测试 API: curl http://localhost:8000/api/health")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
