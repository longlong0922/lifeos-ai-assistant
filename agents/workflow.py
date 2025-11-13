"""
LangGraph 工作流 - 完整的智能体执行流程
使用状态图管理整个对话流
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .state import AgentState
from .prompts import (
    intent_recognition_prompt,
    task_extraction_prompt,
    task_analysis_prompt,
    priority_sorting_prompt,
    action_decomposition_prompt,
    personalization_prompt,
    final_output_prompt,
)
from .tools import get_all_tools


class LifeOSWorkflow:
    """
    LifeOS 完整工作流
    
    流程：
    1. 意图识别 → 判断用户需求类型
    2. 任务提取 → 从输入中提取所有任务
    3. 任务分析 → 评估每个任务的属性
    4. 优先级排序 → 分为高/中/低优先级
    5. 行动拆解 → 推荐任务拆成小步骤
    6. 个性化调整 → 根据用户习惯调整
    7. 输出生成 → 生成最终友好的消息
    """
    
    def __init__(
        self,
        llm_provider: str = "hunyuan",
        db_path: str = "lifeos_data.db"
    ):
        """
        初始化工作流
        
        Args:
            llm_provider: LLM 提供者 (hunyuan/openai/mock)
            db_path: 数据库路径
        """
        # 初始化 LLM
        self.llm = self._init_llm(llm_provider)
        
        # 初始化工具
        self.tools = get_all_tools(db_path)
        
        # 构建工作流图
        self.workflow = self._build_workflow()
        
        # 编译为可执行应用
        self.app = self.workflow.compile()
    
    def _init_llm(self, provider: str) -> ChatOpenAI:
        """初始化 LLM"""
        if provider == "hunyuan":
            return ChatOpenAI(
                api_key=os.getenv("TENCENT_SECRET_KEY"),
                base_url="https://api.hunyuan.cloud.tencent.com/v1",
                model=os.getenv("HUNYUAN_MODEL", "hunyuan-large"),
                temperature=0.7
            )
        elif provider == "openai":
            return ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                temperature=0.7
            )
        else:
            # Mock mode - 使用假的 LLM
            return None
    
    def _build_workflow(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("intent_recognition", self._intent_recognition_node)
        workflow.add_node("task_extraction", self._task_extraction_node)
        workflow.add_node("task_analysis", self._task_analysis_node)
        workflow.add_node("priority_sorting", self._priority_sorting_node)
        workflow.add_node("action_decomposition", self._action_decomposition_node)
        workflow.add_node("personalization", self._personalization_node)
        workflow.add_node("output_generation", self._output_generation_node)
        workflow.add_node("emotion_support", self._emotion_support_node)
        
        # 设置入口点
        workflow.set_entry_point("intent_recognition")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "intent_recognition",
            self._route_by_intent,
            {
                "task": "task_extraction",
                "emotion": "emotion_support",
                "mixed": "task_extraction",
                "unknown": "emotion_support"
            }
        )
        
        # 任务处理流程
        workflow.add_edge("task_extraction", "task_analysis")
        workflow.add_edge("task_analysis", "priority_sorting")
        workflow.add_edge("priority_sorting", "action_decomposition")
        workflow.add_edge("action_decomposition", "personalization")
        workflow.add_edge("personalization", "output_generation")
        
        # 结束节点
        workflow.add_edge("output_generation", END)
        workflow.add_edge("emotion_support", END)
        
        return workflow
    
    # =========================================================================
    # 节点函数
    # =========================================================================
    
    def _intent_recognition_node(self, state: AgentState) -> Dict[str, Any]:
        """节点1: 意图识别"""
        print("🔍 [节点1] 意图识别中...")
        
        user_input = state["user_input"]
        
        if self.llm:
            # 使用 LLM 识别意图
            prompt = intent_recognition_prompt.format(user_input=user_input)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            try:
                result = json.loads(response.content)
                intent = result.get("intent", "unknown")
                confidence = result.get("confidence", 0.5)
                reasoning = result.get("reasoning", "")
            except:
                intent = "unknown"
                confidence = 0.3
                reasoning = "解析失败"
        else:
            # Mock 模式 - 简单规则
            user_lower = user_input.lower()
            if any(k in user_lower for k in ['累', '焦虑', '压力', '崩溃']):
                if any(k in user_lower for k in ['任务', '要做', '完成']):
                    intent = "mixed"
                    confidence = 0.85
                else:
                    intent = "emotion"
                    confidence = 0.9
            elif any(k in user_lower for k in ['任务', '要做', '整理', '安排']):
                intent = "task"
                confidence = 0.9
            else:
                intent = "unknown"
                confidence = 0.4
            reasoning = "基于关键词匹配"
        
        print(f"   ✓ 意图: {intent} (置信度: {confidence:.2f})")
        
        return {
            "intent": intent,
            "intent_confidence": confidence,
            "processing_steps": [f"意图识别: {intent} ({reasoning})"],
            "should_continue": True
        }
    
    def _task_extraction_node(self, state: AgentState) -> Dict[str, Any]:
        """节点2: 任务提取"""
        print("📝 [节点2] 提取任务中...")
        
        user_input = state["user_input"]
        
        if self.llm:
            prompt = task_extraction_prompt.format(user_input=user_input)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            try:
                tasks = json.loads(response.content)
            except:
                # 简单拆分
                tasks = [line.strip() for line in user_input.split('\n') if line.strip()]
        else:
            # Mock - 简单拆分
            tasks = []
            for line in user_input.split('\n'):
                line = line.strip()
                if line and any(char.isalnum() for char in line):
                    # 移除数字序号
                    import re
                    cleaned = re.sub(r'^\d+[\.\)、]?\s*', '', line)
                    if cleaned:
                        tasks.append(cleaned)
        
        print(f"   ✓ 提取到 {len(tasks)} 个任务")
        for i, task in enumerate(tasks, 1):
            print(f"      {i}. {task[:50]}...")
        
        return {
            "raw_tasks": tasks,
            "processing_steps": [f"任务提取: 找到 {len(tasks)} 个任务"]
        }
    
    def _task_analysis_node(self, state: AgentState) -> Dict[str, Any]:
        """节点3: 任务分析"""
        print("🔬 [节点3] 分析任务属性...")
        
        tasks = state["raw_tasks"]
        
        # 使用任务分析工具
        task_analyzer = self.tools[0]  # TaskAnalysisTool
        
        result_json = task_analyzer._run(
            tasks=tasks,
            user_context=state.get("user_context", {})
        )
        
        analyzed_tasks = json.loads(result_json)
        
        print(f"   ✓ 分析完成")
        for task in analyzed_tasks[:3]:
            print(f"      • {task['description'][:40]}")
            print(f"        重要性: {task['importance']}/10, 紧急性: {task['urgency']}/10")
        
        return {
            "analyzed_tasks": analyzed_tasks,
            "processing_steps": [f"任务分析: 评估了 {len(analyzed_tasks)} 个任务"]
        }
    
    def _priority_sorting_node(self, state: AgentState) -> Dict[str, Any]:
        """节点4: 优先级排序"""
        print("📊 [节点4] 优先级排序...")
        
        analyzed_tasks = state["analyzed_tasks"]
        
        # 按优先级分类
        high_priority = []
        medium_priority = []
        low_priority = []
        deferrable = []
        
        for task in analyzed_tasks:
            importance = task["importance"]
            urgency = task["urgency"]
            
            if (importance >= 7 and urgency >= 7) or urgency >= 9:
                high_priority.append(task)
            elif (importance >= 6 and urgency >= 5) or importance >= 8:
                medium_priority.append(task)
            else:
                low_priority.append(task)
            
            if task["can_defer"]:
                deferrable.append(task["description"])
        
        print(f"   ✓ 高优先级: {len(high_priority)} 个")
        print(f"   ✓ 中优先级: {len(medium_priority)} 个")
        print(f"   ✓ 低优先级: {len(low_priority)} 个")
        print(f"   ✓ 可延后: {len(deferrable)} 个")
        
        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "deferrable": deferrable,
            "processing_steps": [f"优先级排序: 高{len(high_priority)}/中{len(medium_priority)}/低{len(low_priority)}"]
        }
    
    def _action_decomposition_node(self, state: AgentState) -> Dict[str, Any]:
        """节点5: 行动拆解"""
        print("🔧 [节点5] 拆解行动步骤...")
        
        high_priority = state["high_priority"]
        
        if not high_priority:
            print("   ⚠ 无高优先级任务，跳过拆解")
            return {
                "recommended_task": None,
                "action_steps": [],
                "quick_start_action": None,
                "processing_steps": ["行动拆解: 无需拆解"]
            }
        
        # 选择第一个高优先级任务拆解
        recommended_task = high_priority[0]
        
        # 使用拆解工具
        decomposer = self.tools[4]  # ActionDecompositionTool
        
        result_json = decomposer._run(
            task=recommended_task["description"],
            total_minutes=recommended_task["estimated_minutes"],
            user_style="balanced"
        )
        
        result = json.loads(result_json)
        
        print(f"   ✓ 拆解任务: {recommended_task['description'][:50]}")
        print(f"   ✓ 生成 {len(result['steps'])} 个步骤")
        print(f"   ✓ 快速启动: {result['quick_start']['description']}")
        
        return {
            "recommended_task": recommended_task,
            "action_steps": result["steps"],
            "quick_start_action": result["quick_start"],
            "processing_steps": [f"行动拆解: 拆成 {len(result['steps'])} 步"]
        }
    
    def _personalization_node(self, state: AgentState) -> Dict[str, Any]:
        """节点6: 个性化调整"""
        print("🎯 [节点6] 个性化调整...")
        
        # 获取用户上下文
        user_id = state.get("user_id", "default")
        
        # 使用记忆搜索工具
        memory_tool = self.tools[3]  # MemorySearchTool
        
        try:
            memory_json = memory_tool._run(user_id=user_id, query="preferences")
            user_context = json.loads(memory_json)
        except:
            user_context = {}
        
        adjustments = []
        
        # 基于记忆的调整
        if user_context.get("morning_productivity"):
            adjustments.append("基于你的习惯，重要任务建议安排在早上（你早上效率最高）")
        
        if user_context.get("prefers_short_tasks"):
            adjustments.append("我已经把任务拆成了小块（你偏好短时任务）")
        
        if state.get("deferrable"):
            adjustments.append(f"建议延后 {len(state['deferrable'])} 个低优先级任务，专注核心工作")
        
        print(f"   ✓ 生成 {len(adjustments)} 条个性化建议")
        
        return {
            "user_context": user_context,
            "personalized_adjustments": adjustments,
            "processing_steps": [f"个性化: {len(adjustments)} 条调整"]
        }
    
    def _output_generation_node(self, state: AgentState) -> Dict[str, Any]:
        """节点7: 输出生成"""
        print("✨ [节点7] 生成最终输出...")
        
        # 构建输出
        output_parts = []
        
        # 1. 开场 + 总结
        total_tasks = len(state.get("analyzed_tasks", []))
        output_parts.append(f"📊 我帮你理了一下，你今天的负担来自 **{total_tasks} 类任务**：\n")
        
        # 2. 高优先级
        high_priority = state.get("high_priority", [])
        if high_priority:
            output_parts.append("📌 **高优先级**（必须今天完成）")
            for i, task in enumerate(high_priority, 1):
                output_parts.append(f"  {i}. {task['description']} ({task['reason']})")
            output_parts.append("")
        
        # 3. 中优先级
        medium_priority = state.get("medium_priority", [])
        if medium_priority:
            output_parts.append("📌 **中优先级**（今天完成更好）")
            for i, task in enumerate(medium_priority, 1):
                output_parts.append(f"  {i}. {task['description']}")
            output_parts.append("")
        
        # 4. 可延后
        deferrable = state.get("deferrable", [])
        if deferrable:
            output_parts.append("📌 **可延后**（不影响今天核心进度）")
            for i, task_desc in enumerate(deferrable, 1):
                output_parts.append(f"  {i}. {task_desc}")
            output_parts.append("")
        
        # 5. 下一步行动
        quick_start = state.get("quick_start_action")
        if quick_start:
            output_parts.append("🟦 **【下一步行动】**")
            output_parts.append(f"我建议从最重要的任务开始。")
            output_parts.append(f"这是一个 **{quick_start['estimated_minutes']} 分钟**就能启动的小步骤：\n")
            output_parts.append(f"   → {quick_start['description']}")
            output_parts.append(f"   （完成率：0/1）\n")
            output_parts.append("如果你愿意，我将在 15 分钟后提醒你回来继续。\n")
        
        # 6. 个性化提示
        adjustments = state.get("personalized_adjustments", [])
        if adjustments:
            output_parts.append("💡 **个性化调整：**")
            for adj in adjustments:
                output_parts.append(f"  • {adj}")
            output_parts.append("")
        
        # 7. 激励结尾
        output_parts.append("⭐ **我已经帮你整理好了：**\n")
        if high_priority:
            output_parts.append(f"• 今天你只要专注 **1 件最重要的事**（{high_priority[0]['description'][:30]}...）")
        if quick_start:
            output_parts.append(f"• 从一个 **{quick_start['estimated_minutes']} 分钟的小步骤**开始即可")
        if deferrable:
            output_parts.append(f"• 次要任务我已替你自动延后安排")
        output_parts.append("• 我会陪你一起推进，**不用担心失控感**。")
        
        final_message = "\n".join(output_parts)
        
        print(f"   ✓ 输出生成完成 ({len(final_message)} 字符)")
        
        return {
            "final_message": final_message,
            "should_continue": False,
            "processing_steps": ["输出生成: 完成最终消息"]
        }
    
    def _emotion_support_node(self, state: AgentState) -> Dict[str, Any]:
        """情绪支持节点"""
        print("💚 [情绪支持] 生成温暖回应...")
        
        message = """听起来你现在压力挺大的。别急，我们一起来处理。

要不这样：
1️⃣ 先用1分钟深呼吸放松，然后我帮你挑最重要的
2️⃣ 直接让我把你的事情整理成清单

你想试试哪个？"""
        
        return {
            "final_message": message,
            "should_continue": False,
            "processing_steps": ["情绪支持: 提供温暖回应"]
        }
    
    def _route_by_intent(self, state: AgentState) -> str:
        """根据意图路由"""
        intent = state.get("intent", "unknown")
        
        if intent in ["task", "decision"]:
            return "task"
        elif intent == "emotion":
            return "emotion"
        elif intent == "mixed":
            return "mixed"
        else:
            return "unknown"
    
    # =========================================================================
    # 主执行函数
    # =========================================================================
    
    def run(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        运行完整工作流
        
        Args:
            user_id: 用户ID
            user_input: 用户输入
            
        Returns:
            包含最终输出和所有中间状态的字典
        """
        print("\n" + "="*80)
        print(f"🚀 LifeOS 工作流启动")
        print(f"用户输入: {user_input[:100]}...")
        print("="*80 + "\n")
        
        # 初始化状态
        initial_state: AgentState = {
            "user_id": user_id,
            "user_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "intent": "",
            "intent_confidence": 0.0,
            "raw_tasks": [],
            "analyzed_tasks": [],
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "deferrable": [],
            "recommended_task": None,
            "action_steps": [],
            "quick_start_action": None,
            "user_context": None,
            "personalized_adjustments": [],
            "summary": "",
            "final_message": "",
            "next_action": "",
            "processing_steps": [],
            "errors": [],
            "should_continue": True,
            "needs_clarification": False,
        }
        
        # 执行工作流
        final_state = self.app.invoke(initial_state)
        
        print("\n" + "="*80)
        print("✅ 工作流执行完成")
        print("="*80)
        
        # 打印处理步骤
        print("\n📋 处理步骤：")
        for step in final_state.get("processing_steps", []):
            print(f"   • {step}")
        
        return final_state


# =============================================================================
# 便捷函数
# =============================================================================

def create_workflow(
    llm_provider: str = None,
    db_path: str = "lifeos_data.db"
) -> LifeOSWorkflow:
    """创建工作流实例"""
    if llm_provider is None:
        llm_provider = os.getenv("LLM_PROVIDER", "mock")
    
    return LifeOSWorkflow(llm_provider, db_path)


__all__ = ['LifeOSWorkflow', 'create_workflow']
