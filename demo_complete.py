"""
LifeOS 完整智能体 Demo
震撼展示：真实 LLM + 多轮对话 + 完整功能
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from agents.workflow_complete import create_complete_workflow
from agents.conversation_manager import ConversationManager


def print_section(title: str, emoji: str = "🎬"):
    """打印章节标题"""
    print(f"\n{'='*80}")
    print(f"{emoji} {title}")
    print(f"{'='*80}\n")


def print_result(result: dict):
    """美化打印结果"""
    print("\n" + "─" * 80)
    print("🤖 LifeOS 助理回复")
    print("─" * 80)
    print(result.get("final_output", "无输出"))
    print("─" * 80)
    
    # 显示处理步骤
    steps = result.get("processing_steps", [])
    if steps:
        print("\n📋 处理步骤：")
        for step in steps:
            print(f"   • {step}")
    
    # 显示元数据
    print(f"\n📊 元数据:")
    print(f"   • 意图: {result.get('intent', 'unknown')}")
    print(f"   • 置信度: {result.get('confidence', 0):.2f}")
    print(f"   • 会话ID: {result.get('session_id', 'N/A')}")
    print()


def demo_1_multi_turn_conversation():
    """Demo 1: 多轮对话展示"""
    print_section("Demo 1: 多轮对话 - 展示上下文记忆", "🎭")
    
    print("""
    这个 Demo 展示：
    ✅ 多轮对话能力
    ✅ 上下文理解（代词指代、意图延续）
    ✅ 数据库持久化保存
    ✅ 真实 LLM 意图识别
    """)
    
    # 创建工作流（使用真实 LLM）
    workflow = create_complete_workflow(
        llm_provider=os.getenv("LLM_PROVIDER", "mock"),
        model_name=os.getenv("HUNYUAN_MODEL", "hunyuan-large")
    )
    
    # 创建会话
    conv_manager = ConversationManager()
    session_id = conv_manager.create_session("demo_user_001")
    
    print(f"🆔 会话ID: {session_id}\n")
    
    # 第1轮：用户表达任务困扰
    print("👤 用户（第1轮）：")
    user_msg_1 = "我感觉好累啊，今天要做的事情太多了：写报告、开会、回复邮件..."
    print(f"   {user_msg_1}\n")
    
    result_1 = workflow.run(user_msg_1, user_id="demo_user_001", session_id=session_id)
    print_result(result_1)
    
    input("\n按回车继续下一轮对话...")
    
    # 第2轮：用户继续追问（测试上下文理解）
    print("\n👤 用户（第2轮）：")
    user_msg_2 = "那我应该先做哪个？"  # 测试代词指代
    print(f"   {user_msg_2}\n")
    
    result_2 = workflow.run(user_msg_2, user_id="demo_user_001", session_id=session_id)
    print_result(result_2)
    
    input("\n按回车继续下一轮对话...")
    
    # 第3轮：切换意图到习惯管理
    print("\n👤 用户（第3轮）：")
    user_msg_3 = "对了，我想养成每天早起的习惯，有什么建议吗？"
    print(f"   {user_msg_3}\n")
    
    result_3 = workflow.run(user_msg_3, user_id="demo_user_001", session_id=session_id)
    print_result(result_3)
    
    # 显示会话统计
    stats = conv_manager.get_session_stats(session_id)
    print(f"\n📊 会话统计:")
    print(f"   • 总轮次: {stats.get('total_turns', 0)}")
    print(f"   • 意图分布: {stats.get('intent_distribution', {})}")


def demo_2_all_intents():
    """Demo 2: 六种意图全覆盖"""
    print_section("Demo 2: 六大核心功能展示", "🎯")
    
    print("""
    展示 6 种核心意图的识别和处理：
    1️⃣  任务管理 (task_management)
    2️⃣  情绪支持 (emotion_support)
    3️⃣  习惯追踪 (habit_tracking)
    4️⃣  目标设定 (goal_setting)
    5️⃣  反思总结 (reflection)
    6️⃣  闲聊对话 (casual_chat)
    """)
    
    workflow = create_complete_workflow(
        llm_provider=os.getenv("LLM_PROVIDER", "mock")
    )
    
    test_cases = [
        ("任务管理", "帮我整理一下今天的待办：复习英语、健身、准备明天的会议"),
        ("情绪支持", "好焦虑啊，感觉什么都做不好..."),
        ("习惯追踪", "我想每天坚持跑步30分钟"),
        ("目标设定", "我今年的目标是考上研究生"),
        ("反思总结", "帮我总结一下这周我做了什么"),
        ("闲聊对话", "你好，你有什么功能？")
    ]
    
    for intent_name, user_input in test_cases:
        print(f"\n🔹 测试 [{intent_name}]")
        print(f"👤 用户: {user_input}\n")
        
        result = workflow.run(user_input, user_id="demo_user_002")
        
        print(f"✓ 识别意图: {result.get('intent', 'unknown')}")
        print(f"🤖 回复:")
        print(f"   {result.get('final_output', '').split(chr(10))[0][:80]}...")
        
        input("\n按回车继续下一个测试...")


def demo_3_habit_tracking_workflow():
    """Demo 3: 习惯追踪完整流程"""
    print_section("Demo 3: 习惯追踪完整流程", "🎯")
    
    print("""
    展示完整的习惯管理功能：
    ✅ 创建习惯计划
    ✅ 打卡记录
    ✅ 数据统计
    ✅ 激励反馈
    """)
    
    workflow = create_complete_workflow()
    
    from agents.tools_complete import HabitTrackingTool
    habit_tool = HabitTrackingTool()
    
    user_id = "demo_user_003"
    
    # 步骤1：用户表达想养成习惯
    print("\n【步骤 1】用户表达意图")
    print("👤: 我想养成每天早上跑步的习惯\n")
    
    result = workflow.run("我想养成每天早上跑步的习惯", user_id=user_id)
    print(f"🤖: {result.get('final_output', '')[:150]}...\n")
    
    input("按回车继续...")
    
    # 步骤2：创建习惯
    print("\n【步骤 2】创建习惯")
    habit_result = habit_tool._run(
        user_id=user_id,
        habit_name="早晨跑步",
        action="create",
        target_frequency="每天"
    )
    print(f"✅ {habit_result}\n")
    
    input("按回车继续...")
    
    # 步骤3：模拟打卡
    print("\n【步骤 3】今天打卡")
    checkin_result = habit_tool._run(
        user_id=user_id,
        habit_name="早晨跑步",
        action="checkin"
    )
    print(f"✅ {checkin_result}\n")
    
    input("按回车继续...")
    
    # 步骤4：查看统计
    print("\n【步骤 4】查看统计")
    stats_result = habit_tool._run(
        user_id=user_id,
        habit_name="早晨跑步",
        action="stats"
    )
    print(f"📊 统计数据:")
    print(stats_result)


def demo_4_goal_breakdown():
    """Demo 4: 目标拆解展示"""
    print_section("Demo 4: 目标智能拆解", "🌟")
    
    print("""
    展示目标规划能力：
    ✅ 大目标拆解为里程碑
    ✅ 里程碑拆解为行动步骤
    ✅ 生成"第一步"行动建议
    """)
    
    workflow = create_complete_workflow(
        llm_provider=os.getenv("LLM_PROVIDER", "mock")
    )
    
    print("\n👤 用户: 我想在半年内学会机器学习并找到相关工作\n")
    
    result = workflow.run(
        "我想在半年内学会机器学习并找到相关工作",
        user_id="demo_user_004"
    )
    
    print_result(result)
    
    # 使用目标工具
    from agents.tools_complete import GoalManagementTool
    goal_tool = GoalManagementTool()
    
    print("\n📍 自动拆解建议:")
    breakdown = goal_tool._run(
        user_id="demo_user_004",
        goal_title="学会机器学习并找到工作",
        action="breakdown"
    )
    print(breakdown)


def demo_5_data_visualization():
    """Demo 5: 数据统计和洞察"""
    print_section("Demo 5: 数据驱动的个人成长", "📊")
    
    print("""
    展示数据统计能力：
    ✅ 习惯坚持率统计
    ✅ 目标进度追踪
    ✅ 整体表现洞察
    ✅ 个性化建议
    """)
    
    from agents.tools_complete import DataStatsTool, HabitTrackingTool
    
    stats_tool = DataStatsTool()
    habit_tool = HabitTrackingTool()
    
    user_id = "demo_user_005"
    
    # 创建一些示例数据
    print("📝 准备示例数据...\n")
    for habit in ["早起", "跑步", "读书"]:
        habit_tool._run(user_id, habit, "create", "每天")
        habit_tool._run(user_id, habit, "checkin")
    
    print("✅ 示例数据准备完成\n")
    
    # 查看统计
    print("📊 习惯统计（最近一周）:")
    habit_stats = stats_tool._run(user_id, "habits", "week")
    print(habit_stats)
    
    print("\n📊 整体表现:")
    overall_stats = stats_tool._run(user_id, "overall", "month")
    print(overall_stats)


def main():
    """主函数"""
    print("""
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║           🚀 LifeOS 完整智能体系统 - 震撼 Demo                  ║
    ║                                                                  ║
    ║  技术栈：                                                        ║
    ║  • LangGraph - 状态机工作流                                      ║
    ║  • LangChain - Prompt 工程和工具管理                            ║
    ║  • 腾讯混元 - 真实 LLM 驱动                                      ║
    ║  • SQLite - 多轮对话和数据持久化                                 ║
    ║                                                                  ║
    ║  核心能力：                                                      ║
    ║  ✅ 6 种意图识别（真实 LLM，非关键词）                          ║
    ║  ✅ 多轮对话记忆（数据库持久化）                                 ║
    ║  ✅ 完整工具集（习惯/目标/反思/统计）                            ║
    ║  ✅ 个性化建议（基于历史数据）                                   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    """)
    
    print("请选择要运行的 Demo:")
    print("1. 多轮对话展示（上下文记忆 + 意图切换）")
    print("2. 六大功能全覆盖（所有意图类型）")
    print("3. 习惯追踪完整流程（创建→打卡→统计）")
    print("4. 目标智能拆解（大目标→里程碑→行动）")
    print("5. 数据统计和洞察（可视化分析）")
    print("0. 运行所有 Demo")
    print()
    
    choice = input("请输入选择 (0-5): ").strip()
    
    demos = {
        "1": demo_1_multi_turn_conversation,
        "2": demo_2_all_intents,
        "3": demo_3_habit_tracking_workflow,
        "4": demo_4_goal_breakdown,
        "5": demo_5_data_visualization
    }
    
    if choice == "0":
        for demo_func in demos.values():
            demo_func()
            input("\n\n按回车继续下一个 Demo...")
    elif choice in demos:
        demos[choice]()
    else:
        print("❌ 无效选择")
        return
    
    print("""
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║                      🎉 Demo 演示完成！                          ║
    ║                                                                  ║
    ║  项目亮点总结：                                                  ║
    ║  • 真实 LLM 意图识别（非简单关键词匹配）                        ║
    ║  • 多轮对话数据库持久化                                          ║
    ║  • 6 大核心功能完整覆盖                                          ║
    ║  • LangGraph 专业工作流编排                                      ║
    ║  • 工具集扩展性强（易于添加新功能）                              ║
    ║                                                                  ║
    ║  这才是"真正强大"的 LifeOS 智能助理！                           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 感谢体验 LifeOS！")
    except Exception as e:
        print(f"\n\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
