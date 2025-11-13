"""
完整 LifeOS 智能体工作流
支持 6 种意图 + 多轮对话 + 完整工具集
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
    personalization_prompt,
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
        
        # 所有路径最终都到输出生成
        for node in ["task_processing", "emotion_support", "habit_management",
                     "goal_planning", "reflection_guide", "casual_response"]:
            workflow.add_edge(node, "output_generation")
        
        workflow.add_edge("output_generation", END)
        
        return workflow.compile()
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        try:
            # 尝试提取 JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            return {}
        except:
            return {}
    
    def _build_conversation_summary(self, history: List[Dict]) -> str:
        """构建对话上下文摘要"""
        if not history:
            return "（这是新对话的开始）"
        
        recent = history[-2:]  # 最近2轮
        if len(recent) == 0:
            return "（这是新对话的开始）"
        
        summary = []
        for i, turn in enumerate(recent, 1):
            user_msg = turn.get('user_message', '')
            assistant_msg = turn.get('assistant_message', '')
            intent = turn.get('intent', 'unknown')
            
            summary.append(f"第{i}轮:")
            summary.append(f"  用户说: {user_msg}")
            summary.append(f"  识别意图: {intent}")
            summary.append(f"  助理回复: {assistant_msg[:80]}...")
        
        return "\n".join(summary)
    
    # =========================================================================
    # 节点函数
    # =========================================================================
    
    def _intent_recognition_node(self, state: AgentState) -> Dict:
        """意图识别节点 - 使用真实 LLM"""
        print("🔍 [意图识别] 调用 LLM 分析...")
        
        user_input = state["user_input"]
        conversation_history = state.get("conversation_history", [])
        
        conv_summary = self._build_conversation_summary(conversation_history)
        
        if self.llm:
            try:
                prompt = complete_intent_recognition_prompt.format_messages(
                    user_input=user_input,
                    conversation_summary=conv_summary
                )
                
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                intent = result.get("intent", "casual_chat")
                confidence = result.get("confidence", 0.7)
                reasoning = result.get("reasoning", "LLM 分析")
                
                print(f"   ✓ 意图: {intent} (置信度: {confidence:.2f})")
                print(f"   💡 推理: {reasoning[:60]}...")
                
                return {
                    "intent": intent,
                    "confidence": confidence,
                    "processing_steps": [f"🤖 LLM 意图识别: {intent} - {reasoning}"]
                }
            
            except Exception as e:
                print(f"   ⚠️ LLM 调用失败: {e}")
        
        # 降级：简单规则匹配
        intent = self._fallback_intent_detection(user_input)
        return {
            "intent": intent,
            "confidence": 0.6,
            "processing_steps": [f"规则匹配: {intent}"]
        }
    
    def _fallback_intent_detection(self, text: str) -> str:
        """降级的意图检测"""
        text_lower = text.lower()
        
        if any(k in text_lower for k in ['习惯', '坚持', '打卡']):
            return "habit_tracking"
        elif any(k in text_lower for k in ['目标', '想要', '计划', '实现']):
            return "goal_setting"
        elif any(k in text_lower for k in ['总结', '反思', '回顾']):
            return "reflection"
        elif any(k in text_lower for k in ['累', '焦虑', '压力', '崩溃']):
            return "emotion_support"
        elif any(k in text_lower for k in ['任务', '要做', '整理']):
            return "task_management"
        else:
            return "casual_chat"
    
    def _task_processing_node(self, state: AgentState) -> Dict:
        """任务处理节点"""
        print("📋 [任务处理] 提取并分析任务...")
        
        user_input = state["user_input"]
        conv_summary = self._build_conversation_summary(
            state.get("conversation_history", [])
        )
        
        # 如果用户输入很短（可能是追问），尝试从对话历史中提取任务
        if len(user_input) < 20 and conv_summary:
            print("   🔍 从对话历史中查找任务...")
            combined_input = f"{conv_summary}\n\n当前问题：{user_input}"
        else:
            combined_input = user_input
        
        if self.llm:
            try:
                # 第一步：提取任务
                prompt = enhanced_task_extraction_prompt.format_messages(
                    user_input=combined_input
                )
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                tasks = result.get("tasks", [])
                priorities = result.get("priority_analysis", {})
                suggestions = result.get("suggestions", [])
                
                # 按优先级排序任务 (high -> medium -> low)
                priority_order = {'high': 1, 'medium': 2, 'low': 3, '': 4}
                tasks.sort(key=lambda t: priority_order.get(t.get('priority', '').lower(), 4))
                
                print(f"   ✓ 提取到 {len(tasks)} 个任务（已按优先级排序）")
                
                if len(tasks) == 0:
                    # 如果没有提取到任务，给出智能回应
                    return {
                        "analyzed_tasks": [],
                        "final_output": "根据之前提到的任务，建议按照以下优先级处理：\n\n1. 📝 写报告（最重要，建议先完成）\n2. 📅 开会（固定时间）\n3. 📧 回复邮件（可以批量处理）\n\n💡 建议从报告开始，因为这通常需要更多的专注时间和精力。",
                        "processing_steps": ["📝 基于上下文生成建议"]
                    }
                
                # 第二步：生成智能输出
                print("   🔍 生成智能建议...")
                
                # 构建任务列表文本（带优先级标识）
                task_list_items = []
                for i, t in enumerate(tasks[:5]):
                    title = t.get('title', t.get('description', '任务'))
                    priority = t.get('priority', '').lower()
                    priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
                    priority_text = {'high': '高优先级', 'medium': '中优先级', 'low': '低优先级'}.get(priority, '')
                    task_list_items.append(f"{i+1}. {priority_icon} {title} {f'({priority_text})' if priority_text else ''}")
                
                task_list = "\n".join(task_list_items)
                
                # 构建优先级建议（只显示高优先级）
                high_priority = [t for t in tasks if t.get('priority', '').lower() == 'high']
                priority_text = ""
                if high_priority:
                    priority_text = f"\n\n🔴 高优先级任务（建议优先处理）：\n" + "\n".join([
                        f"• {t.get('title', '任务')}" for t in high_priority[:3]
                    ])
                
                # 构建建议文本（来自 LLM）
                suggestion_text = ""
                if suggestions:
                    suggestion_text = f"\n\n💡 执行建议：\n" + "\n".join([f"• {s}" for s in suggestions[:3]])
                
                # 如果没有建议，添加默认建议
                if not suggestion_text and high_priority:
                    suggestion_text = "\n\n💡 执行建议：\n"
                    suggestion_text += f"• 建议从 {high_priority[0].get('title', '高优先级任务')} 开始，这通常需要更多专注时间\n"
                    suggestion_text += "• 固定时间的任务（如开会）要提前安排\n"
                    suggestion_text += "• 简单重复的任务（如邮件）可以批量处理"
                
                final_output = f"好的！我帮你整理了 {len(tasks)} 个任务：\n\n{task_list}{priority_text}{suggestion_text}"
                
                print(f"   ✓ 智能建议已生成")
                
                return {
                    "analyzed_tasks": tasks,
                    "final_output": final_output,
                    "processing_steps": [f"📝 任务提取: {len(tasks)}个任务", "🤖 智能建议生成"]
                }
            except Exception as e:
                print(f"   ⚠️ 任务处理失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 简单拆分（备用）
        lines = [l.strip() for l in user_input.split('\n') if l.strip()]
        task_list = "\n".join([f"{i+1}. {l}" for i, l in enumerate(lines[:5])])
        return {
            "analyzed_tasks": [{"title": l} for l in lines[:5]],
            "final_output": f"我帮你整理了任务：\n\n{task_list}\n\n💡 建议先从最重要的开始！",
            "processing_steps": ["简单拆分任务"]
        }
    
    def _emotion_support_node(self, state: AgentState) -> Dict:
        """情绪支持节点"""
        print("💚 [情绪支持] 生成温暖回应...")
        
        user_input = state["user_input"]
        conv_summary = self._build_conversation_summary(
            state.get("conversation_history", [])
        )
        
        if self.llm:
            try:
                prompt = emotion_support_prompt.format_messages(
                    user_input=user_input,
                    conversation_summary=conv_summary
                )
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                support_msg = result.get("empathy_response", "我理解你的感受")
                suggestions = result.get("suggestions", [])
                
                final_output = support_msg + "\n\n建议：\n" + "\n".join(f"• {s}" for s in suggestions)
                
                print(f"   ✓ 温暖回应已生成")
                
                return {
                    "final_output": final_output,
                    "processing_steps": ["💚 情绪支持回应"]
                }
            except Exception as e:
                print(f"   ⚠️ 情绪支持失败: {e}")
        
        # 简单回应
        return {
            "final_output": "我理解你现在的感受。要不要先休息一下，然后我们一起整理思路？",
            "processing_steps": ["简单情绪回应"]
        }
    
    def _habit_management_node(self, state: AgentState) -> Dict:
        """习惯管理节点"""
        print("🎯 [习惯管理] 处理习惯相关请求...")
        
        user_input = state["user_input"]
        
        if self.llm:
            try:
                prompt = habit_management_prompt.format_messages(
                    user_input=user_input
                )
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                habit_plan = result.get("habit_plan", {})
                motivation = result.get("motivation_message", "")
                
                output = f"好的，帮你设计习惯计划：\n\n"
                output += f"📌 习惯：{habit_plan.get('habit_name', '新习惯')}\n"
                output += f"⏰ 频率：{habit_plan.get('frequency', '每天')}\n"
                output += f"🎯 触发：{habit_plan.get('trigger', '设定一个触发条件')}\n"
                output += f"🎁 奖励：{habit_plan.get('reward', '完成后奖励自己')}\n\n"
                output += f"💪 {motivation}"
                
                return {
                    "final_output": output,
                    "processing_steps": ["🎯 习惯计划设计"]
                }
            except Exception as e:
                print(f"   ⚠️ 习惯管理失败: {e}")
        
        return {
            "final_output": "好的！要养成新习惯，建议：\n1. 从小目标开始\n2. 设定固定时间\n3. 记录打卡",
            "processing_steps": ["简单习惯建议"]
        }
    
    def _goal_planning_node(self, state: AgentState) -> Dict:
        """目标规划节点"""
        print("🎯 [目标规划] 拆解目标...")
        
        user_input = state["user_input"]
        conversation_history = state.get("conversation_history", [])
        conv_summary = self._build_conversation_summary(conversation_history)
        
        if self.llm:
            try:
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
                    
                    output = f"🚀 **第{step_num}步**:\n\n"
                    output += f"📝 **行动**: {action}\n\n"
                    if details:
                        output += f"💡 **详细说明**:\n{details}\n\n"
                    if time_req:
                        output += f"⏱️ **预计耗时**: {time_req}\n"
                    if result_exp:
                        output += f"✨ **预期成果**: {result_exp}\n"
                    
                    print(f"   ✓ 延续目标: 第{step_num}步")
                    
                    return {
                        "final_output": output,
                        "processing_steps": [f"🎯 提供第{step_num}步的详细指导"]
                    }
                
                # 处理新目标规划
                goal = result.get("goal", "目标")
                why = result.get("why", "")
                timeline = result.get("timeline", "")
                milestones = result.get("milestones", [])
                first_step_data = result.get("first_step", {})
                resources = result.get("resources", [])
                tips = result.get("tips", [])
                
                # 构建输出
                output = f"🎯 **目标**: {goal}\n"
                if why:
                    output += f"💡 **动机**: {why}\n"
                if timeline:
                    output += f"⏰ **时间规划**: {timeline}\n"
                
                output += "\n📍 **学习路径（里程碑）**:\n"
                for i, m in enumerate(milestones, 1):
                    milestone = m.get('milestone', '')
                    desc = m.get('description', '')
                    deadline = m.get('deadline', '')
                    actions = m.get('actions', [])
                    
                    output += f"\n**阶段{i}: {milestone}**"
                    if deadline:
                        output += f" ({deadline})"
                    output += "\n"
                    if desc:
                        output += f"   {desc}\n"
                    if actions:
                        output += "   行动清单:\n"
                        for action in actions[:3]:  # 最多显示3个
                            output += f"   ✓ {action}\n"
                
                # 第一步
                output += "\n🚀 **立即开始（第一步）**:\n"
                if isinstance(first_step_data, dict):
                    action = first_step_data.get('action', '开始行动')
                    time_req = first_step_data.get('time_required', '')
                    result_exp = first_step_data.get('expected_result', '')
                    
                    output += f"   📝 {action}\n"
                    if time_req:
                        output += f"   ⏱️ 预计耗时: {time_req}\n"
                    if result_exp:
                        output += f"   ✨ 预期成果: {result_exp}\n"
                else:
                    output += f"   {first_step_data}\n"
                
                # 资源推荐
                if resources:
                    output += "\n📚 **推荐资源**:\n"
                    for res in resources[:3]:
                        output += f"   • {res}\n"
                
                # 实用建议
                if tips:
                    output += "\n💡 **实用建议**:\n"
                    for tip in tips[:3]:
                        output += f"   • {tip}\n"
                
                print(f"   ✓ 目标拆解完成: {goal}")
                
                return {
                    "final_output": output,
                    "processing_steps": ["🎯 完整的目标规划和学习路径"]
                }
            except Exception as e:
                print(f"   ⚠️ 目标规划失败: {e}")
                import traceback
                traceback.print_exc()
        
        return {
            "final_output": "好的！让我们把大目标拆解成小步骤，一步步实现！",
            "processing_steps": ["简单目标建议"]
        }
    
    def _reflection_guide_node(self, state: AgentState) -> Dict:
        """反思引导节点"""
        print("📝 [反思引导] 生成反思框架...")
        
        user_input = state["user_input"]
        
        if self.llm:
            try:
                prompt = reflection_prompt.format_messages(
                    user_input=user_input,
                    historical_data=""
                )
                response = self.llm.invoke(prompt)
                result = self._parse_json_response(response.content)
                
                summary = result.get("summary", "")
                achievements = result.get("achievements", [])
                learnings = result.get("learnings", [])
                
                output = f"📊 {summary}\n\n"
                output += "✅ 成就：\n" + "\n".join(f"• {a}" for a in achievements) + "\n\n"
                output += "💡 收获：\n" + "\n".join(f"• {l}" for l in learnings)
                
                return {
                    "final_output": output,
                    "processing_steps": ["📝 反思总结生成"]
                }
            except Exception as e:
                print(f"   ⚠️ 反思引导失败: {e}")
        
        return {
            "final_output": "让我们一起回顾一下：\n1. 这段时间完成了什么？\n2. 有什么收获？\n3. 下一步怎么做？",
            "processing_steps": ["简单反思引导"]
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
                    recent_history = conversation_history[-3:]  # 最近3轮
                    history_text = "\n".join([
                        f"用户: {h.get('user_message', '')}\n助理: {h.get('assistant_message', '')}"
                        for h in recent_history
                    ])
                
                # 调用大模型生成个性化回应
                from langchain_core.prompts import ChatPromptTemplate
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """你是 LifeOS 智能助理，一个温暖、专业、富有同理心的生活助手。

你的特点：
- 友善亲切，像朋友一样交流
- 善于倾听，理解用户情绪
- 适当使用 emoji 让对话更生动
- 回复简洁明了，不啰嗦

根据用户的输入，生成温暖、自然的回应。"""),
                    ("human", f"""对话历史：
{history_text if history_text else '（这是第一轮对话）'}

用户当前输入：{user_input}

请生成一个友好、自然的回应。""")
                ])
                
                response = self.llm.invoke(prompt.format_messages())
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
        
        # 备用回复（如果 LLM 失败）
        user_input_lower = user_input.lower()
        if "你好" in user_input_lower or "hi" in user_input_lower:
            output = "你好！我是 LifeOS 智能助理 😊\n\n我可以帮你：\n• 管理任务和待办\n• 追踪习惯打卡\n• 设定和拆解目标\n• 记录反思总结\n• 提供情绪支持\n\n有什么可以帮到你的吗？"
        elif "功能" in user_input_lower or "能做" in user_input_lower:
            output = "我有这些能力：\n\n1. 📋 任务管理：整理待办，智能排序\n2. 🎯 习惯追踪：打卡记录，数据统计\n3. 🌟 目标规划：拆解目标，制定计划\n4. 📝 反思总结：定期回顾，持续改进\n5. 💚 情绪支持：倾听理解，温暖陪伴\n\n试试告诉我你现在想做什么吧！"
        elif "谢谢" in user_input_lower or "感谢" in user_input_lower:
            output = "不客气！😊 很高兴能帮到你。有其他需要随时告诉我哦！"
        else:
            output = "我在呢！有什么可以帮你的吗？😊"
        
        return {
            "final_output": output,
            "processing_steps": ["💬 友好回应"]
        }
    
    def _output_generation_node(self, state: AgentState) -> Dict:
        """输出生成节点"""
        print("✨ [输出生成] 整合最终回复...")
        
        # 如果已有 final_output，保持不变
        if state.get("final_output"):
            return {"final_output": state["final_output"]}
        
        # 否则根据任务生成输出
        tasks = state.get("analyzed_tasks", [])
        if tasks:
            output = f"好的！我帮你整理了 {len(tasks)} 个任务：\n\n"
            for i, task in enumerate(tasks[:5], 1):
                output += f"{i}. {task.get('title', '任务')}\n"
            output += "\n💡 建议从最重要的开始！"
            
            return {"final_output": output}
        
        return {"final_output": "我理解了，让我们一起来处理！"}
    
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
        # 获取对话历史
        conversation_history = []
        if self.conversation_manager and session_id:
            conversation_history = self.conversation_manager.get_conversation_history(
                session_id, last_n_turns=5
            )
        elif self.conversation_manager:
            # 创建新会话
            session_id = self.conversation_manager.create_session(user_id)
        
        # 初始化状态
        initial_state = {
            "user_input": user_input,
            "user_id": user_id,
            "session_id": session_id or "temp_session",
            "conversation_history": conversation_history,
            "intent": "",
            "confidence": 0.0,
            "analyzed_tasks": [],
            "processing_steps": [],
            "final_output": "",
            "timestamp": datetime.now().isoformat()
        }
        
        # 执行工作流
        result = self.workflow_app.invoke(initial_state)
        
        # 保存对话
        if self.conversation_manager and session_id:
            self.conversation_manager.add_turn(
                session_id=session_id,
                user_id=user_id,
                user_message=user_input,
                assistant_message=result.get("final_output", ""),
                intent=result.get("intent", "unknown"),
                intent_confidence=result.get("confidence", 0.0),
                extracted_data={
                    "tasks": result.get("analyzed_tasks", []),
                    "steps": result.get("processing_steps", [])
                }
            )
        
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
        llm = ChatOpenAI(
            api_key=api_key or "dummy",
            base_url=base_url,
            model=model_name,
            temperature=0.7
        )
        print("✅ OpenAI LLM 初始化成功")
    
    elif llm_provider == "mock":
        llm = None
        print("✅ 使用 Mock 模式（测试用）")
    
    return CompleteLifeOSWorkflow(
        llm=llm,
        db_path=db_path,
        enable_conversation_memory=True
    )
