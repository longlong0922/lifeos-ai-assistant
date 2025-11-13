"""
LifeOS LangGraph Demo
完整展示 3 大核心能力
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.workflow import create_workflow
from modules.memory import MemoryStore, MemoryManager, MemoryType


def demo_scenario_1():
    """
    Demo #1: 信息过载场景
    展示完整的任务分析、优先级排序、行动拆解流程
    """
    print("\n" + "🎬"*40)
    print("Demo #1: 信息过载 → 自动总结与提炼重点")
    print("🎬"*40)
    
    # 创建工作流
    workflow = create_workflow(llm_provider="mock")
    
    # 用户输入
    user_input = """我感觉好崩溃，今天事情太多了：
1. 明天要交的项目报告还没写完
2. 晚上要和客户开会，还没准备材料
3. 有三封邮件要回复
4. 同事让我帮忙看两个文件
5. 还要去超市买菜

我都不知道从哪里开始，脑子一团乱"""
    
    # 运行工作流
    result = workflow.run("demo_user_001", user_input)
    
    # 显示最终输出
    print("\n" + "="*80)
    print("🤖 LifeOS 助理输出（展示 3 大解决痛点）")
    print("="*80)
    print(result["final_message"])
    
    return result


def demo_scenario_2():
    """
    Demo #2: 学习场景
    展示任务拆解能力
    """
    print("\n" + "🎬"*40)
    print("Demo #2: 计划难执行 → 自动拆成下一步行动")
    print("🎬"*40)
    
    workflow = create_workflow(llm_provider="mock")
    
    user_input = """我想开始准备考公，但任务太多了，不知道从哪里开始"""
    
    result = workflow.run("demo_user_002", user_input)
    
    print("\n" + "="*80)
    print("🤖 LifeOS 助理输出")
    print("="*80)
    print(result["final_message"])
    
    # 显示拆解的步骤
    if result.get("action_steps"):
        print("\n📋 详细步骤拆解：")
        for step in result["action_steps"]:
            print(f"\n  步骤 {step['step_number']}（{step['type']} - {step['difficulty']}）")
            print(f"    → {step['description']}")
            print(f"    ⏱ 预计：{step['estimated_minutes']} 分钟")
            print(f"    ✓ 预期成果：{step['expected_outcome']}")
    
    return result


def demo_scenario_3():
    """
    Demo #3: 个性化指导场景
    展示基于用户习惯的个性化调整
    """
    print("\n" + "🎬"*40)
    print("Demo #3: 个性化指导 → 根据用户习惯调整计划")
    print("🎬"*40)
    
    # 先设置用户偏好
    memory_store = MemoryStore("lifeos_data.db")
    memory_manager = MemoryManager(memory_store)
    
    user_id = "demo_user_003"
    
    print("📝 设置用户偏好...")
    memory_manager.remember(
        user_id, "morning_productivity", True,
        MemoryType.PREFERENCE
    )
    memory_manager.remember(
        user_id, "evening_productivity", False,
        MemoryType.PREFERENCE
    )
    memory_manager.remember(
        user_id, "preferred_task_duration", 25,
        MemoryType.PREFERENCE
    )
    memory_manager.remember(
        user_id, "career_goal", "成为产品经理",
        MemoryType.GOAL
    )
    
    print("   ✓ 早上效率高：True")
    print("   ✓ 晚上效率低：True")
    print("   ✓ 偏好25分钟任务块（番茄钟）")
    print("   ✓ 长期目标：成为产品经理\n")
    
    # 创建工作流
    workflow = create_workflow(llm_provider="mock")
    
    user_input = """今天下午要写项目报告
晚上要回复一堆邮件
明天上午要参加产品评审会议"""
    
    result = workflow.run(user_id, user_input)
    
    print("\n" + "="*80)
    print("🤖 LifeOS 助理输出")
    print("="*80)
    print(result["final_message"])
    
    # 显示个性化分析
    if result.get("user_context"):
        print("\n🎯 个性化分析：")
        context = result["user_context"]
        print(f"   • 早上生产力：{context.get('morning_productivity', False)}")
        print(f"   • 晚上生产力：{context.get('evening_productivity', True)}")
        print(f"   • 长期目标：{context.get('long_term_goals', [])}")
        print(f"   • 工作风格：{context.get('work_style', '未知')}")
    
    return result


def demo_workflow_visualization():
    """
    Demo #4: 工作流可视化
    展示完整的处理流程
    """
    print("\n" + "🎬"*40)
    print("Demo #4: 工作流可视化 - 完整处理流程")
    print("🎬"*40)
    
    workflow = create_workflow(llm_provider="mock")
    
    user_input = "今天要做年度总结报告，还要准备下周的培训材料"
    
    result = workflow.run("demo_user_004", user_input)
    
    print("\n" + "="*80)
    print("📊 工作流执行图")
    print("="*80)
    
    print("""
    用户输入
       ↓
    ┌──────────────┐
    │ 1. 意图识别   │ → 判断：任务处理模式
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ 2. 任务提取   │ → 提取：{task_count} 个任务
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ 3. 任务分析   │ → 评估：重要性、紧急性、耗时
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ 4. 优先级排序 │ → 分类：高/中/低优先级
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ 5. 行动拆解   │ → 拆解：{step_count} 个可执行步骤
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ 6. 个性化调整 │ → 调整：基于用户习惯
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ 7. 输出生成   │ → 生成：友好的最终消息
    └──────────────┘
       ↓
    最终输出
    """.format(
        task_count=len(result.get("raw_tasks", [])),
        step_count=len(result.get("action_steps", []))
    ))
    
    print("\n" + "="*80)
    print("🤖 最终输出")
    print("="*80)
    print(result["final_message"])


def run_all_demos():
    """运行所有 Demo"""
    print("\n" + "🚀"*40)
    print("LifeOS LangGraph 完整 Demo")
    print("基于 LangChain + LangGraph 的智能体系统")
    print("🚀"*40)
    
    try:
        # Demo 1: 信息过载
        demo_scenario_1()
        input("\n按回车继续下一个 Demo...")
        
        # Demo 2: 任务拆解
        demo_scenario_2()
        input("\n按回车继续下一个 Demo...")
        
        # Demo 3: 个性化指导
        demo_scenario_3()
        input("\n按回车继续下一个 Demo...")
        
        # Demo 4: 工作流可视化
        demo_workflow_visualization()
        
        print("\n" + "="*80)
        print("✅ 所有 Demo 演示完成！")
        print("="*80)
        
        print("\n🎯 核心能力展示：")
        print("  ✓ 信息过滤能力 - 自动提取和分类任务")
        print("  ✓ 任务拆解能力 - 拆解成 5 分钟可启动步骤")
        print("  ✓ 行动启动能力 - 推荐最轻松的开始点")
        print("  ✓ 个性化指导能力 - 基于用户习惯调整计划")
        print("  ✓ 情绪承接能力 - 温暖鼓励的语气")
        
        print("\n🏗️ 技术栈：")
        print("  • LangChain - Prompt 管理和 LLM 调用")
        print("  • LangGraph - 状态机工作流编排")
        print("  • 5 个专业工具 - 任务分析、优先级评估、时间估算、记忆搜索、行动拆解")
        print("  • 7 个工作流节点 - 完整的处理流程")
        print("  • 多 Prompt 系统 - 7 个专门优化的 Prompt")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo 已中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
