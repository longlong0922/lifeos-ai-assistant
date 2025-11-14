"""
完整 LifeOS 智能体工作流 - 改进版
修复：确保所有 prompt 都被正确使用
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.state import AgentState
from agents.prompts_complete import (
    complete_intent_recognition_prompt,
    enhanced_task_extraction_prompt,
    personalization_prompt,  # ← 新增：将被正确使用
    emotion_support_prompt,
    habit_management_prompt,
    goal_planning_prompt,
    reflection_prompt
)
from agents.tools_complete import get_complete_tools
from agents.conversation_manager import ConversationManager

# 尝试导入腾讯混元
try:
    from agents.hunyuan_llm import HunyuanLLM
    HUNYUAN_AVAILABLE = True
except ImportError:
    HUNYUAN_AVAILABLE = False
    print("⚠️ 腾讯云 SDK 未安装，无法使用混元模型")


class CompleteLifeOSWorkflow:
    """
    完整 LifeOS 智能体工作流
    """
    
    def __init__(
        self,
        llm: Optional[Union[ChatOpenAI, HunyuanLLM]] = None,
        db_path: str = "lifeos_data.db",
        enable_conversation_memory: bool = True
    ):
        self.llm = llm
        self.db_path = db_path
        self.tools = get_complete_tools(db_path)
        self.conversation_manager = ConversationManager(db_path) if enable_conversation_memory else None
        self.workflow_app = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """构建完整工作流图"""
        workflow = StateGraph(AgentState)
        
        # 添加所有节点
        workflow.add_node("intent_recognition", self._intent_recognition_node)
        workflow.add_node("task_processing", self._task_processing_node)
        workflow.add_node("emotion_support", self._emotion_support_node)
        workflow.add_node("habit_management", self._habit_management_node)
        workflow.add_node("goal_planning", self._goal_planning_node)
        workflow.add_node("reflection_guide", self._reflection_guide_node)
        workflow.add_node("casual_response", self._casual_response_node)
        workflow.add_node("personalization", self._personalization_node)  # ← 新增节点
        workflow.add_node("output_generation", self._output_generation_node)
        
        # 设置入口
        workflow.set_entry_point("intent_recognition")
        
        # 条件路由
        workflow.add_conditional_edges(
            "intent_recognition",
            self._route_by_intent,
            {
                "task_management": "task_processing",
                "emotion_support": "emotion_support",
                "habit_tracking": "habit_management",
                "goal_setting": "goal_planning",
                "reflection": "reflection_guide",
                "casual_chat": "casual_response"
            }
        )
        
        # 任务处理后可选择性进行个性化增强
        workflow.add_conditional_edges(
            "task_processing",
            self._should_personalize,
            {
                "personalize": "personalization",
                "skip": "output_generation"
            }
        )
        
        # 个性化后到输出
        workflow.add_edge("personalization", "output_generation")
        
        # 其他路径直接到输出
        for node in ["emotion_support", "habit_management",
                     "goal_planning", "reflection_guide", "casual_response"]:
            workflow.add_edge(node, "output_generation")
        
        workflow.add_edge("output_generation", END)
        
        return workflow.compile()
    
    def _should_personalize(self, state: AgentState) -> str:
        """判断是否需要个性化增强"""
        # 如果有多个任务且有用户画像，则进行个性化
        tasks = state.get("analyzed_tasks", [])
        if len(tasks) >= 2:
            return "personalize"
        return "skip"
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 JSON 响应（改进版，处理 Markdown 代码块）"""
        try:
            # 移除可能的 Markdown 代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # 尝试提取 JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            return {}
        except Exception as e:
            print(f"   ⚠️ JSON 解析失败: {e}")
            print(f"   📄 原始内容: {content[:200]}...")
            return {}
    
    def _build_conversation_summary(self, history: List[Dict]) -> str:
        """构建对话上下文摘要"""
        if not history:
            return "（这是新对话的开始）"
        
        recent = history[-3:]  # 最近3轮（增加上下文）
        if len(recent) == 0:
            return "（这是新对话的开始）"
        
        summary = []
        for i, turn in enumerate(recent, 1):
            user_msg = turn.get('user_message', '')
            assistant_msg = turn.get('assistant_message', '')
            intent = turn.get('intent', 'unknown')
            
            summary.append(f"第{i}轮:")
            summary.append(f"  用户: {user_msg[:50]}...")
            summary.append(f"  意图: {intent}")
            summary.append(f"  回复: {assistant_msg[:60]}...")
        
        return "\n".join(summary)
    
    def _extract_user_profile(self, conversation_history: List[Dict]) -> str:
        """从对话历史中提取用户画像（用于个性化）"""
        if not conversation_history:
            return "暂无用户画像数据"
        
        # 简单提取：统计用户的行为偏好
        task_count = sum(1 for h in conversation_history if h.get('intent') == 'task_management')
        emotion_count = sum(1 for h in conversation_history if h.get('intent') == 'emotion_support')
        goal_count = sum(1 for h in conversation_history if h.get('intent') == 'goal_setting')
        
        profile = []
        if task_count > 2:
            profile.append("工作风格: 任务导向型（喜欢整理和规划）")
        if emotion_count > 1:
            profile.append("压力应对: 情绪抒发型（需要情感支持）")
        if goal_count > 1:
            profile.append("目标特点: 目标驱动型（重视长期规划）")
        
        return "\n".join(profile) if profile else "暂无明显偏好"
    
    # =========================================================================
    # 节点函数
    # =========================================================================
    
    def _intent_recognition_node(self, state: AgentState) -> Dict:
        """意图识别节点 - 使用 complete_intent_recognition_prompt"""
        print("🔍 [意图识别] 调用 LLM 分析...")
        
        user_input = state["user_input"]
        conversation_history = state.get("conversation_history", [])
        
        conv_summary = self._build_conversation_summary(conversation_history)
        
        if self.llm:
            try:
                # ✅ 正确使用 complete_intent_recognition_prompt
                prompt = complete_intent_recognition_prompt.format_messages(
                    user_input=user_input,
                    conversation_summary=conv_summary
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                intent = result.get("intent", "casual_chat")
                confidence = result.get("confidence", 0.7)
                reasoning = result.get("reasoning", "LLM 分析")
                context_continuation = result.get("context_continuation", False)
                
                print(f"   ✓ 意图: {intent} (置信度: {confidence:.2f})")
                print(f"   💡 推理: {reasoning[:60]}...")
                if context_continuation:
                    print(f"   🔗 检测到上下文延续")
                
                return {
                    "intent": intent,
                    "confidence": confidence,
                    "context_continuation": context_continuation,
                    "processing_steps": [f"🤖 意图识别: {intent} - {reasoning}"]
                }
            
            except Exception as e:
                print(f"   ⚠️ LLM 调用失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级：简单规则匹配
        intent = self._fallback_intent_detection(user_input)
        return {
            "intent": intent,
            "confidence": 0.6,
            "context_continuation": False,
            "processing_steps": [f"规则匹配: {intent}"]
        }
    
    def _fallback_intent_detection(self, text: str) -> str:
        """降级的意图检测"""
        text_lower = text.lower()
        
        if any(k in text_lower for k in ['习惯', '坚持', '打卡']):
            return "habit_tracking"
        elif any(k in text_lower for k in ['目标', '想要', '计划', '实现', '学习']):
            return "goal_setting"
        elif any(k in text_lower for k in ['总结', '反思', '回顾', '复盘']):
            return "reflection"
        elif any(k in text_lower for k in ['累', '焦虑', '压力', '崩溃', '疲惫']):
            return "emotion_support"
        elif any(k in text_lower for k in ['任务', '要做', '整理', '待办', '安排']):
            return "task_management"
        else:
            return "casual_chat"
    
    def _task_processing_node(self, state: AgentState) -> Dict:
        """任务处理节点 - 使用 enhanced_task_extraction_prompt"""
        print("📋 [任务处理] 提取并分析任务...")
        
        user_input = state["user_input"]
        conv_summary = self._build_conversation_summary(
            state.get("conversation_history", [])
        )
        
        # 处理上下文延续（如"第二步呢"）
        context_continuation = state.get("context_continuation", False)
        if context_continuation and len(user_input) < 20:
            print("   🔍 检测到延续性提问，从对话历史中提取任务上下文...")
            user_input_with_context = f"{conv_summary}\n\n当前问题：{user_input}"
        else:
            user_input_with_context = user_input
        
        if self.llm:
            try:
                # ✅ 正确使用 enhanced_task_extraction_prompt
                # 注意：这个 prompt 只接受 user_input 参数
                prompt = enhanced_task_extraction_prompt.format_messages(
                    user_input=user_input_with_context
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                tasks = result.get("tasks", [])
                priority_analysis = result.get("priority_analysis", {})
                suggestions = result.get("suggestions", [])
                total_count = result.get("total_count", len(tasks))
                
                # 按优先级排序任务
                priority_order = {'high': 1, 'medium': 2, 'low': 3, '': 4}
                tasks.sort(key=lambda t: priority_order.get(t.get('priority', '').lower(), 4))
                
                print(f"   ✓ 提取到 {len(tasks)} 个任务")
                print(f"   📊 优先级分析: {priority_analysis}")
                
                if len(tasks) == 0:
                    # 根据建议生成智能回应
                    fallback_suggestions = suggestions if suggestions else [
                        "未检测到具体任务。你可以告诉我需要处理的事情，我会帮你整理。"
                    ]
                    return {
                        "analyzed_tasks": [],
                        "final_output": "\n".join(fallback_suggestions),
                        "processing_steps": ["📝 未检测到任务，提供引导建议"]
                    }
                
                # 构建输出
                output_parts = []
                output_parts.append(f"好的！我帮你整理了 {total_count} 个任务：\n")
                
                # 任务列表（带优先级标识）
                for i, t in enumerate(tasks[:5], 1):
                    title = t.get('title', '任务')
                    priority = t.get('priority', '').lower()
                    deadline = t.get('deadline', '')
                    estimated_time = t.get('estimated_time', '')
                    
                    priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
                    priority_text = {'high': '高优先级', 'medium': '中优先级', 'low': '低优先级'}.get(priority, '')
                    
                    task_line = f"{i}. {priority_icon} {title}"
                    if priority_text:
                        task_line += f" ({priority_text})"
                    if deadline:
                        task_line += f" | ⏰ {deadline}"
                    if estimated_time:
                        task_line += f" | 预计 {estimated_time}"
                    
                    output_parts.append(task_line)
                
                # 优先级分析
                urgent_count = priority_analysis.get('urgent_count', 0)
                important_first = priority_analysis.get('important_first', '')
                
                if urgent_count > 0:
                    output_parts.append(f"\n🔴 有 {urgent_count} 个高优先级任务需要优先处理")
                    if important_first:
                        output_parts.append(f"💡 建议先从「{important_first}」开始")
                
                # 执行建议
                if suggestions:
                    output_parts.append("\n💡 执行建议：")
                    for s in suggestions[:3]:
                        output_parts.append(f"• {s}")
                
                final_output = "\n".join(output_parts)
                
                print(f"   ✓ 任务分析完成")
                
                return {
                    "analyzed_tasks": tasks,
                    "priority_analysis": priority_analysis,
                    "final_output": final_output,
                    "processing_steps": [
                        f"📝 任务提取: {len(tasks)}个",
                        f"📊 优先级分析: {urgent_count}个紧急任务",
                        "💡 生成执行建议"
                    ]
                }
                
            except Exception as e:
                print(f"   ⚠️ 任务处理失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级处理
        lines = [l.strip() for l in user_input.split('\n') if l.strip()]
        task_list = "\n".join([f"{i+1}. {l}" for i, l in enumerate(lines[:5])])
        return {
            "analyzed_tasks": [{"title": l, "priority": "medium"} for l in lines[:5]],
            "final_output": f"我帮你整理了任务：\n\n{task_list}\n\n💡 建议先从最重要的开始！",
            "processing_steps": ["简单任务拆分（降级模式）"]
        }
    
    def _personalization_node(self, state: AgentState) -> Dict:
        """个性化增强节点 - 使用 personalization_prompt"""
        print("🎨 [个性化] 根据用户画像优化建议...")
        
        if not self.llm:
            print("   ⚠️ 无 LLM，跳过个性化")
            return {}
        
        try:
            # 提取用户画像
            conversation_history = state.get("conversation_history", [])
            user_profile = self._extract_user_profile(conversation_history)
            
            # 构建任务列表
            tasks = state.get("analyzed_tasks", [])
            current_tasks = "\n".join([
                f"- {t.get('title', '任务')} (优先级: {t.get('priority', 'medium')})"
                for t in tasks[:5]
            ])
            
            # 构建对话历史文本
            conv_history_text = self._build_conversation_summary(conversation_history)
            
            # ✅ 正确使用 personalization_prompt
            prompt = personalization_prompt.format_messages(
                user_profile=user_profile,
                current_tasks=current_tasks,
                conversation_history=conv_history_text
            )
            
            response = self.llm.invoke(prompt)
            result = self._parse_json_response(response.content)
            
            personalized_suggestions = result.get("personalized_suggestions", [])
            adapted_timeline = result.get("adapted_timeline", "")
            motivation_style = result.get("motivation_style", "目标驱动型")
            
            print(f"   ✓ 个性化完成 (激励方式: {motivation_style})")
            
            # 增强原有输出
            enhanced_output = state.get("final_output", "")
            if personalized_suggestions:
                enhanced_output += "\n\n🎯 根据你的习惯定制建议："
                for s in personalized_suggestions[:3]:
                    enhanced_output += f"\n• {s}"
            
            if adapted_timeline:
                enhanced_output += f"\n\n⏰ 推荐时间安排：\n{adapted_timeline}"
            
            return {
                "final_output": enhanced_output,
                "processing_steps": state.get("processing_steps", []) + [
                    f"🎨 个性化增强 ({motivation_style})"
                ]
            }
            
        except Exception as e:
            print(f"   ⚠️ 个性化失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _emotion_support_node(self, state: AgentState) -> Dict:
        """情绪支持节点 - 使用 emotion_support_prompt"""
        print("💚 [情绪支持] 生成温暖回应...")
        
        user_input = state["user_input"]
        conv_summary = self._build_conversation_summary(
            state.get("conversation_history", [])
        )
        
        if self.llm:
            try:
                # ✅ 正确使用 emotion_support_prompt
                prompt = emotion_support_prompt.format_messages(
                    user_input=user_input,
                    conversation_summary=conv_summary
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                empathy_response = result.get("empathy_response", "我理解你的感受")
                suggestions = result.get("suggestions", [])
                quick_actions = result.get("quick_actions", [])
                tone = result.get("tone", "温暖")
                
                print(f"   ✓ 回应语气: {tone}")
                
                # 构建输出
                output_parts = [empathy_response]
                
                if suggestions:
                    output_parts.append("\n💡 一些想法：")
                    for s in suggestions[:2]:
                        output_parts.append(f"• {s}")
                
                if quick_actions:
                    output_parts.append("\n🌟 如果你愿意，可以试试：")
                    for a in quick_actions[:2]:
                        output_parts.append(f"• {a}")
                
                final_output = "\n".join(output_parts)
                
                return {
                    "final_output": final_output,
                    "processing_steps": [f"💚 情绪支持 (语气: {tone})"]
                }
                
            except Exception as e:
                print(f"   ⚠️ 情绪支持失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级回应
        return {
            "final_output": "我理解你现在的感受。要不要先休息一下，然后我们一起整理思路？",
            "processing_steps": ["💚 简单情绪回应"]
        }
    
    def _habit_management_node(self, state: AgentState) -> Dict:
        """习惯管理节点 - 使用 habit_management_prompt"""
        print("🎯 [习惯管理] 处理习惯相关请求...")
        
        user_input = state["user_input"]
        
        if self.llm:
            try:
                # ✅ 正确使用 habit_management_prompt
                prompt = habit_management_prompt.format_messages(
                    user_input=user_input
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                habit_plan = result.get("habit_plan", {})
                motivation = result.get("motivation_message", "")
                
                print(f"   ✓ 习惯计划: {habit_plan.get('habit_name', '新习惯')}")
                
                # 构建输出
                output_parts = ["好的，帮你设计习惯计划：\n"]
                output_parts.append(f"📌 **习惯名称**: {habit_plan.get('habit_name', '新习惯')}")
                output_parts.append(f"⏰ **频率**: {habit_plan.get('frequency', '每天')}")
                output_parts.append(f"🎯 **触发条件**: {habit_plan.get('trigger', '设定一个触发条件')}")
                output_parts.append(f"🎁 **小奖励**: {habit_plan.get('reward', '完成后奖励自己')}")
                output_parts.append(f"🌱 **从小开始**: {habit_plan.get('start_small', '一步一步来')}")
                output_parts.append(f"📊 **追踪方式**: {habit_plan.get('tracking_method', '每日打卡')}")
                
                if motivation:
                    output_parts.append(f"\n💪 {motivation}")
                
                final_output = "\n".join(output_parts)
                
                return {
                    "final_output": final_output,
                    "processing_steps": ["🎯 习惯计划设计"]
                }
                
            except Exception as e:
                print(f"   ⚠️ 习惯管理失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级
        return {
            "final_output": "好的！要养成新习惯，建议：\n1. 从小目标开始\n2. 设定固定时间\n3. 记录打卡进度",
            "processing_steps": ["🎯 简单习惯建议"]
        }
    
    def _goal_planning_node(self, state: AgentState) -> Dict:
        """目标规划节点 - 使用 goal_planning_prompt"""
        print("🎯 [目标规划] 拆解目标...")
        
        user_input = state["user_input"]
        conversation_history = state.get("conversation_history", [])
        conv_summary = self._build_conversation_summary(conversation_history)
        
        if self.llm:
            try:
                # ✅ 正确使用 goal_planning_prompt
                prompt = goal_planning_prompt.format_messages(
                    user_input=user_input,
                    conversation_summary=conv_summary
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                # 检查是否为延续性回答
                is_continuation = result.get("is_continuation", False)
                
                if is_continuation:
                    # 处理"第X步"类型的问题
                    step_num = result.get("step_number", 2)
                    action = result.get("action", "继续行动")
                    details = result.get("details", "")
                    time_req = result.get("time_required", "")
                    result_exp = result.get("expected_result", "")
                    
                    print(f"   ✓ 延续目标: 第{step_num}步")
                    
                    output_parts = [f"🚀 **第{step_num}步**:\n"]
                    output_parts.append(f"📝 **行动**: {action}\n")
                    if details:
                        output_parts.append(f"💡 **详细说明**: {details}\n")
                    if time_req:
                        output_parts.append(f"⏱️ **预计耗时**: {time_req}")
                    if result_exp:
                        output_parts.append(f"✨ **预期成果**: {result_exp}")
                    
                    return {
                        "final_output": "\n".join(output_parts),
                        "processing_steps": [f"🎯 提供第{step_num}步指导"]
                    }
                
                # 处理新目标规划
                goal = result.get("goal", "目标")
                why = result.get("why", "")
                timeline = result.get("timeline", "")
                milestones = result.get("milestones", [])
                first_step_data = result.get("first_step", {})
                resources = result.get("resources", [])
                tips = result.get("tips", [])
                
                print(f"   ✓ 目标: {goal}")
                print(f"   ✓ 里程碑: {len(milestones)}个")
                
                # 构建输出
                output_parts = [f"🎯 **目标**: {goal}"]
                if why:
                    output_parts.append(f"💡 **动机**: {why}")
                if timeline:
                    output_parts.append(f"⏰ **时间规划**: {timeline}")
                
                output_parts.append("\n📍 **学习路径（里程碑）**:")
                for i, m in enumerate(milestones, 1):
                    milestone = m.get('milestone', '')
                    desc = m.get('description', '')
                    deadline = m.get('deadline', '')
                    actions = m.get('actions', [])
                    
                    output_parts.append(f"\n**阶段{i}: {milestone}**" + (f" ({deadline})" if deadline else ""))
                    if desc:
                        output_parts.append(f"   {desc}")
                    if actions:
                        output_parts.append("   行动清单:")
                        for action in actions[:3]:
                            output_parts.append(f"   ✓ {action}")
                
                # 第一步
                output_parts.append("\n🚀 **立即开始（第一步）**:")
                if isinstance(first_step_data, dict):
                    action = first_step_data.get('action', '开始行动')
                    time_req = first_step_data.get('time_required', '')
                    result_exp = first_step_data.get('expected_result', '')
                    
                    output_parts.append(f"   📝 {action}")
                    if time_req:
                        output_parts.append(f"   ⏱️ 预计耗时: {time_req}")
                    if result_exp:
                        output_parts.append(f"   ✨ 预期成果: {result_exp}")
                else:
                    output_parts.append(f"   {first_step_data}")
                
                # 资源
                if resources:
                    output_parts.append("\n📚 **推荐资源**:")
                    for res in resources[:3]:
                        output_parts.append(f"   • {res}")
                
                # 建议
                if tips:
                    output_parts.append("\n💡 **实用建议**:")
                    for tip in tips[:3]:
                        output_parts.append(f"   • {tip}")
                
                final_output = "\n".join(output_parts)
                
                return {
                    "final_output": final_output,
                    "processing_steps": ["🎯 完整目标规划和学习路径"]
                }
                
            except Exception as e:
                print(f"   ⚠️ 目标规划失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级
        return {
            "final_output": "好的！让我们把大目标拆解成小步骤，一步步实现！\n\n建议从最简单的第一步开始。",
            "processing_steps": ["🎯 简单目标建议"]
        }
    
    def _reflection_guide_node(self, state: AgentState) -> Dict:
        """反思引导节点 - 使用 reflection_prompt"""
        print("📝 [反思引导] 生成反思框架...")
        
        user_input = state["user_input"]
        conversation_history = state.get("conversation_history", [])
        
        # 从历史中提取数据（如果有）
        historical_data = ""
        if conversation_history:
            # 提取最近的任务、目标等信息
            recent_tasks = []
            recent_goals = []
            for turn in conversation_history[-5:]:
                if turn.get('intent') == 'task_management':
                    extracted = turn.get('extracted_data', {})
                    tasks = extracted.get('tasks', [])
                    recent_tasks.extend([t.get('title', '') for t in tasks[:3]])
                elif turn.get('intent') == 'goal_setting':
                    recent_goals.append(turn.get('user_message', '')[:50])
            
            if recent_tasks or recent_goals:
                historical_data = "最近活动:\n"
                if recent_tasks:
                    historical_data += f"任务: {', '.join(recent_tasks[:5])}\n"
                if recent_goals:
                    historical_data += f"目标: {', '.join(recent_goals[:3])}"
        
        if self.llm:
            try:
                # ✅ 正确使用 reflection_prompt
                prompt = reflection_prompt.format_messages(
                    user_input=user_input,
                    historical_data=historical_data if historical_data else "暂无历史数据"
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                summary = result.get("summary", "")
                achievements = result.get("achievements", [])
                learnings = result.get("learnings", [])
                improvements = result.get("improvements", [])
                next_actions = result.get("next_actions", [])
                
                print(f"   ✓ 反思总结生成完成")
                
                # 构建输出
                output_parts = []
                
                if summary:
                    output_parts.append(f"📊 **反思总结**\n{summary}\n")
                
                if achievements:
                    output_parts.append("✅ **小成就**:")
                    for a in achievements:
                        output_parts.append(f"• {a}")
                    output_parts.append("")
                
                if learnings:
                    output_parts.append("💡 **学到的**:")
                    for l in learnings:
                        output_parts.append(f"• {l}")
                    output_parts.append("")
                
                if improvements:
                    output_parts.append("🌱 **可以改进**:")
                    for imp in improvements[:2]:
                        output_parts.append(f"• {imp}")
                    output_parts.append("")
                
                if next_actions:
                    output_parts.append("🚀 **下一步行动**:")
                    for action in next_actions[:2]:
                        output_parts.append(f"• {action}")
                
                final_output = "\n".join(output_parts)
                
                return {
                    "final_output": final_output,
                    "processing_steps": ["📝 4D 反思模型生成"]
                }
                
            except Exception as e:
                print(f"   ⚠️ 反思引导失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级
        return {
            "final_output": "让我们一起回顾：\n\n1. ✅ 这段时间完成了什么？\n2. 💡 有什么收获？\n3. 🚀 下一步怎么做？",
            "processing_steps": ["📝 简单反思引导"]
        }
    
    def _casual_response_node(self, state: AgentState) -> Dict:
        """闲聊回应节点"""
        print("💬 [闲聊] 生成友好回应...")
        
        user_input = state["user_input"]
        conversation_history = state.get("conversation_history", [])
        
        if self.llm:
            try:
                # 构建对话历史上下文
                history_text = ""
                if conversation_history:
                    recent_history = conversation_history[-3:]
                    history_text = "\n".join([
                        f"用户: {h.get('user_message', '')}\n助理: {h.get('assistant_message', '')[:100]}"
                        for h in recent_history
                    ])
                
                # 调用大模型生成个性化回应
                from langchain_core.prompts import ChatPromptTemplate
                casual_prompt = ChatPromptTemplate.from_messages([
                    ("system", """你是 LifeOS 智能助理，一个温暖、专业、富有同理心的生活助手。

你的特点：
- 友善亲切，像朋友一样交流
- 善于倾听，理解用户情绪
- 适当使用 emoji 让对话更生动（但不过度）
- 回复简洁明了，不啰嗦
- 能够记住对话上下文，提供连贯回复

根据用户的输入，生成温暖、自然、贴合上下文的回应。"""),
                    ("human", f"""对话历史：
{history_text if history_text else '（这是第一轮对话）'}

用户当前输入：{user_input}

请生成一个友好、自然的回应。""")
                ])
                
                response = self.llm.invoke(casual_prompt.format_messages())
                output = response.content.strip()
                
                print(f"   ✓ 生成个性化回应")
                
                return {
                    "final_output": output,
                    "processing_steps": ["💬 AI 生成友好回应"]
                }
                
            except Exception as e:
                print(f"   ⚠️ 闲聊回应失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 降级回复（基于规则）
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['你好', 'hi', 'hello', '嗨']):
            output = "你好！我是 LifeOS 智能助理 😊\n\n我可以帮你：\n• 📋 管理任务和待办\n• 🎯 追踪习惯打卡\n• 🌟 设定和拆解目标\n• 📝 记录反思总结\n• 💚 提供情绪支持\n\n有什么可以帮到你的吗？"
        elif any(word in user_input_lower for word in ['功能', '能做', '可以做', '帮我']):
            output = "我有这些能力：\n\n1. 📋 **任务管理**：整理待办，智能排序\n2. 🎯 **习惯追踪**：打卡记录，数据统计\n3. 🌟 **目标规划**：拆解目标，制定计划\n4. 📝 **反思总结**：定期回顾，持续改进\n5. 💚 **情绪支持**：倾听理解，温暖陪伴\n\n试试告诉我你现在想做什么吧！"
        elif any(word in user_input_lower for word in ['谢谢', '感谢', 'thanks', 'thx']):
            output = "不客气！😊 很高兴能帮到你。\n\n有其他需要随时告诉我哦！"
        elif any(word in user_input_lower for word in ['再见', 'bye', '拜拜']):
            output = "再见！👋 记得随时回来找我，我会一直在这里支持你！"
        else:
            output = "我在呢！😊 有什么可以帮你的吗？\n\n你可以告诉我你的任务、目标，或者只是聊聊天也可以~"
        
        return {
            "final_output": output,
            "processing_steps": ["💬 友好回应"]
        }
    
    def _output_generation_node(self, state: AgentState) -> Dict:
        """输出生成节点 - 最终整合"""
        print("✨ [输出生成] 整合最终回复...")
        
        # 如果已有 final_output，保持不变
        if state.get("final_output"):
            final_output = state["final_output"]
            print(f"   ✓ 使用已生成的输出 ({len(final_output)} 字符)")
            return {"final_output": final_output}
        
        # 否则根据意图生成默认输出
        intent = state.get("intent", "casual_chat")
        
        if intent == "task_management":
            tasks = state.get("analyzed_tasks", [])
            if tasks:
                output = f"好的！我帮你整理了 {len(tasks)} 个任务：\n\n"
                for i, task in enumerate(tasks[:5], 1):
                    output += f"{i}. {task.get('title', '任务')}\n"
                output += "\n💡 建议从最重要的开始！"
            else:
                output = "我理解了，让我们开始整理任务吧！"
        else:
            output = "好的，我明白了！让我来帮你处理。"
        
        print(f"   ✓ 生成默认输出")
        return {"final_output": output}
    
    def _route_by_intent(self, state: AgentState) -> str:
        """根据意图路由"""
        intent = state.get("intent", "casual_chat")
        print(f"🔀 路由到: {intent}")
        return intent
    
    # =========================================================================
    # 执行方法
    # =========================================================================
    
    def run(
        self,
        user_input: str,
        user_id: str = "default_user",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行完整工作流
        
        Args:
            user_input: 用户输入
            user_id: 用户ID
            session_id: 会话ID（用于多轮对话）
        
        Returns:
            执行结果
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始处理用户输入: {user_input[:50]}...")
        print(f"{'='*60}\n")
        
        # 获取对话历史
        conversation_history = []
        if self.conversation_manager and session_id:
            conversation_history = self.conversation_manager.get_conversation_history(
                session_id, last_n_turns=5
            )
            print(f"📚 加载对话历史: {len(conversation_history)} 轮")
        elif self.conversation_manager:
            # 创建新会话
            session_id = self.conversation_manager.create_session(user_id)
            print(f"✨ 创建新会话: {session_id}")
        
        # 初始化状态
        initial_state = {
            "user_input": user_input,
            "user_id": user_id,
            "session_id": session_id or "temp_session",
            "conversation_history": conversation_history,
            "intent": "",
            "confidence": 0.0,
            "context_continuation": False,
            "analyzed_tasks": [],
            "priority_analysis": {},
            "processing_steps": [],
            "final_output": "",
            "timestamp": datetime.now().isoformat()
        }
        
        # 执行工作流
        try:
            result = self.workflow_app.invoke(initial_state)
            print(f"\n✅ 工作流执行成功")
            print(f"📊 处理步骤: {result.get('processing_steps', [])}")
        except Exception as e:
            print(f"\n❌ 工作流执行失败: {e}")
            import traceback
            traceback.print_exc()
            result = {
                **initial_state,
                "final_output": "抱歉，处理过程中出现了问题。请稍后再试。",
                "processing_steps": [f"错误: {str(e)}"]
            }
        
        # 保存对话
        if self.conversation_manager and session_id:
            try:
                self.conversation_manager.add_turn(
                    session_id=session_id,
                    user_id=user_id,
                    user_message=user_input,
                    assistant_message=result.get("final_output", ""),
                    intent=result.get("intent", "unknown"),
                    intent_confidence=result.get("confidence", 0.0),
                    extracted_data={
                        "tasks": result.get("analyzed_tasks", []),
                        "steps": result.get("processing_steps", []),
                        "priority_analysis": result.get("priority_analysis", {})
                    }
                )
                print(f"💾 对话已保存")
            except Exception as e:
                print(f"⚠️ 保存对话失败: {e}")
        
        print(f"\n{'='*60}\n")
        return result


def create_complete_workflow(
    llm_provider: str = "mock",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model_name: str = "gpt-3.5-turbo",
    db_path: str = "lifeos_data.db"
) -> CompleteLifeOSWorkflow:
    """
    创建完整工作流实例
    
    Args:
        llm_provider: LLM 提供商 (mock/openai/hunyuan)
        api_key: API 密钥（OpenAI）或 SecretId:SecretKey（腾讯混元）
        base_url: API 基础 URL
        model_name: 模型名称
        db_path: 数据库路径
    
    Returns:
        完整工作流实例
    """
    llm = None
    
    if llm_provider == "hunyuan":
        # 使用腾讯混元 SDK
        if not HUNYUAN_AVAILABLE:
            print("❌ 腾讯云 SDK 未安装，请运行: pip install tencentcloud-sdk-python")
            print("🔄 切换到 Mock 模式")
            llm_provider = "mock"
        else:
            try:
                from agents.hunyuan_llm import create_hunyuan_llm
                # 从环境变量直接读取
                llm = create_hunyuan_llm(
                    secret_id=os.getenv("TENCENT_SECRET_ID"),
                    secret_key=os.getenv("TENCENT_SECRET_KEY"),
                    model=model_name or "hunyuan-large"
                )
                print("✅ 腾讯混元 LLM 初始化成功")
            except Exception as e:
                print(f"❌ 腾讯混元初始化失败: {str(e)}")
                print("🔄 切换到 Mock 模式")
                llm_provider = "mock"
                llm = None
    
    elif llm_provider == "openai":
        # 使用 OpenAI
        try:
            llm = ChatOpenAI(
                api_key=api_key or os.getenv("OPENAI_API_KEY", "dummy"),
                base_url=base_url,
                model=model_name,
                temperature=0.7
            )
            print(f"✅ OpenAI LLM 初始化成功 (模型: {model_name})")
        except Exception as e:
            print(f"❌ OpenAI 初始化失败: {e}")
            print("🔄 切换到 Mock 模式")
            llm = None
    
    elif llm_provider == "mock":
        llm = None
        print("✅ 使用 Mock 模式（规则匹配，测试用）")
    
    else:
        print(f"⚠️ 未知的 LLM 提供商: {llm_provider}")
        print("🔄 使用 Mock 模式")
        llm = None
    
    return CompleteLifeOSWorkflow(
        llm=llm,
        db_path=db_path,
        enable_conversation_memory=True
    )