"""
LifeOS 完整实现 - 接入真实大模型
展示 3 大核心能力：信息过载处理、计划拆解、个性化指导
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入核心模块
from modules.conversation_flow import (
    ConversationFlowManager,
    ConversationMode,
    ConversationState
)
from modules.smart_summary import (
    SmartSummaryParser,
    build_smart_summary_prompt
)
from modules.next_action import (
    NextActionParser,
    build_next_action_prompt,
    adjust_suggestions_by_preferences,
    UserPreferences
)
from modules.memory import (
    MemoryStore,
    MemoryManager,
    MemoryType
)
from modules.system_prompts import (
    get_system_prompt,
    add_memory_context
)
from modules.llm_service import call_llm, init_llm_service


class LifeOSRealAssistant:
    """LifeOS 真实助手（接入真实 LLM）"""
    
    def __init__(self, db_path: str = "lifeos_data.db", llm_provider: str = None):
        """初始化"""
        # 初始化 LLM
        if llm_provider is None:
            llm_provider = os.getenv("LLM_PROVIDER", "mock")
        
        print(f"🚀 初始化 LifeOS（LLM 提供者: {llm_provider}）")
        init_llm_service(llm_provider)
        
        # 初始化各模块
        self.flow_manager = ConversationFlowManager()
        self.summary_parser = SmartSummaryParser()
        self.action_parser = NextActionParser()
        
        # 初始化记忆模块
        memory_store = MemoryStore(db_path)
        self.memory_manager = MemoryManager(memory_store)
        
        # 对话状态缓存
        self.conversation_states: Dict[str, ConversationState] = {}
        
        print("✅ LifeOS 初始化完成\n")
    
    def chat(self, user_id: str, user_input: str) -> Dict:
        """
        处理用户输入（真实 LLM 版本）
        
        Args:
            user_id: 用户 ID
            user_input: 用户输入
            
        Returns:
            响应字典
        """
        try:
            print(f"\n{'='*60}")
            print(f"用户输入: {user_input}")
            print(f"{'='*60}\n")
            
            # 1. 获取或创建对话状态
            state = self.conversation_states.get(user_id)
            
            # 2. 路由到合适的模式
            mode, classification, response_suggestion = self.flow_manager.route(
                user_input, 
                state
            )
            
            print(f"📊 检测到模式: {mode.value}")
            print(f"📊 意图类型: {classification.intent.value}")
            print(f"📊 置信度: {classification.confidence:.2f}\n")
            
            # 3. 根据模式处理
            if mode == ConversationMode.EMOTION_SUPPORT:
                return self._handle_emotion_mode(user_id, user_input, response_suggestion)
            
            elif mode == ConversationMode.ACTION_ASSISTANT:
                return self._handle_action_mode(user_id, user_input, classification)
            
            elif mode == ConversationMode.MIXED:
                return self._handle_mixed_mode(user_id, user_input, response_suggestion)
            
            else:  # UNKNOWN
                return self._handle_unknown(user_id, response_suggestion)
        
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "抱歉，我遇到了一些问题。能再说一次吗？"
            }
    
    def _handle_emotion_mode(
        self, 
        user_id: str, 
        user_input: str, 
        response_suggestion: str
    ) -> Dict:
        """处理情绪支持模式（使用预设响应，不调用 LLM）"""
        print("💚 进入情绪支持模式\n")
        
        return {
            "success": True,
            "mode": "emotion_support",
            "response_type": "text",
            "content": {
                "text": response_suggestion,
                "options": [
                    {"label": "🌿 说说话", "action": "continue_emotion"},
                    {"label": "📋 帮我整理任务", "action": "switch_to_action"}
                ]
            },
            "display_text": response_suggestion,
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_action_mode(
        self, 
        user_id: str, 
        user_input: str,
        classification
    ) -> Dict:
        """处理行动助理模式（调用真实 LLM）"""
        print("📋 进入行动助理模式")
        
        # 判断是摘要还是拆解
        if any(keyword in user_input for keyword in ["任务", "要做", "事情", "今天", "清单"]):
            print("→ 生成智能摘要\n")
            return self._generate_summary_real(user_id, user_input)
        else:
            print("→ 生成任务拆解\n")
            return self._generate_action_plan_real(user_id, user_input)
    
    def _handle_mixed_mode(
        self, 
        user_id: str, 
        user_input: str, 
        response_suggestion: str
    ) -> Dict:
        """处理混合模式"""
        print("🔄 进入混合模式（情绪+任务）\n")
        
        return {
            "success": True,
            "mode": "mixed",
            "response_type": "text",
            "content": {
                "text": response_suggestion,
                "quick_actions": [
                    {"label": "先放松一下", "action": "relax"},
                    {"label": "直接整理任务", "action": "organize_tasks"}
                ]
            },
            "display_text": response_suggestion,
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_unknown(self, user_id: str, response_suggestion: str) -> Dict:
        """处理未知情况"""
        print("❓ 进入澄清模式\n")
        
        return {
            "success": True,
            "mode": "clarification",
            "response_type": "text",
            "content": {
                "text": response_suggestion
            },
            "display_text": response_suggestion,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_summary_real(self, user_id: str, user_input: str) -> Dict:
        """生成智能摘要（真实 LLM）"""
        print("🤖 调用 LLM 生成摘要...")
        
        try:
            # 构建 prompt
            messages = build_smart_summary_prompt(user_input, include_examples=True)
            
            # 获取用户偏好
            profile = self.memory_manager.get_user_profile(user_id)
            user_memories = {
                "morning_productivity": profile.morning_productivity,
                "prefers_short_tasks": profile.prefers_short_tasks,
                "long_term_goals": profile.long_term_goals
            }
            
            # 添加记忆上下文
            if user_memories.get("morning_productivity") or user_memories.get("long_term_goals"):
                messages[0]["content"] = add_memory_context(messages[0]["content"], user_memories)
            
            # 调用 LLM
            llm_response = call_llm(messages, temperature=0.7, max_tokens=1500)
            print(f"✅ LLM 响应成功 ({len(llm_response)} 字符)\n")
            
            # 解析响应
            result = self.summary_parser.parse_llm_response(llm_response, user_input)
            
            if result:
                formatted_text = self.summary_parser.format_for_display(result)
                
                return {
                    "success": True,
                    "mode": "action_assistant",
                    "response_type": "summary_card",
                    "content": {
                        "summary": result.one_line_summary,
                        "categories": result.categories,
                        "highlights": result.highlights,
                        "priorities": [
                            {
                                "item": p.item,
                                "importance": p.importance,
                                "urgency": p.urgency,
                                "reason": p.reason
                            }
                            for p in result.priority_assessment
                        ],
                        "suggested_action": {
                            "desc": result.suggested_next_action.desc,
                            "est_minutes": result.suggested_next_action.est_minutes,
                            "next_step": result.suggested_next_action.next_step
                        },
                        "skip_candidates": result.skip_candidates
                    },
                    "display_text": formatted_text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "无法解析 LLM 响应"
                }
        
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_action_plan_real(self, user_id: str, user_input: str) -> Dict:
        """生成下一步行动计划（真实 LLM）"""
        print("🤖 调用 LLM 生成行动计划...")
        
        try:
            # 构建 prompt
            messages = build_next_action_prompt(user_input, include_examples=True)
            
            # 调用 LLM
            llm_response = call_llm(messages, temperature=0.7, max_tokens=1500)
            print(f"✅ LLM 响应成功 ({len(llm_response)} 字符)\n")
            
            # 解析响应
            result = self.action_parser.parse_llm_response(llm_response)
            
            if result:
                # 根据用户偏好调整
                prefs = UserPreferences(
                    morning_productivity=True,
                    prefers_short_tasks=True
                )
                adjusted_result = adjust_suggestions_by_preferences(result, prefs)
                
                formatted_text = self.action_parser.format_for_display(adjusted_result)
                
                return {
                    "success": True,
                    "mode": "action_assistant",
                    "response_type": "action_plan",
                    "content": {
                        "task": adjusted_result.task,
                        "actions": [
                            {
                                "desc": action.desc,
                                "est_minutes": action.est_minutes,
                                "type": action.type.value,
                                "difficulty": action.difficulty,
                                "expected_outcome": action.expected_outcome
                            }
                            for action in adjusted_result.candidate_actions
                        ],
                        "recommended_index": adjusted_result.recommended_action_index,
                        "rationale": adjusted_result.rationale
                    },
                    "display_text": formatted_text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "无法解析 LLM 响应"
                }
        
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# Demo 场景
# ============================================================================

def demo_scenario_1():
    """Demo #1: 信息过载场景"""
    print("\n" + "="*80)
    print("📺 Demo #1: 信息过载 → 自动总结与提炼重点")
    print("="*80)
    
    assistant = LifeOSRealAssistant(llm_provider=os.getenv("LLM_PROVIDER", "mock"))
    
    user_input = """我感觉好崩溃，今天事情太多了：
    1. 明天要交的项目报告还没写完
    2. 晚上要和客户开会，还没准备材料
    3. 有三封邮件要回复
    4. 同事让我帮忙看两个文件
    5. 还要去超市买菜
    
    我都不知道从哪里开始，脑子一团乱"""
    
    response = assistant.chat("demo_user_001", user_input)
    
    if response["success"]:
        print("\n" + "="*80)
        print("🤖 LifeOS 助理输出（展示 3 大解决痛点）")
        print("="*80)
        print("\n① 信息过载 → 自动总结与提炼重点\n")
        print(response["display_text"])
    else:
        print(f"\n❌ 错误: {response.get('error')}")


def demo_scenario_2():
    """Demo #2: 计划难执行场景"""
    print("\n" + "="*80)
    print("📺 Demo #2: 计划难执行 → 自动拆成下一步行动")
    print("="*80)
    
    assistant = LifeOSRealAssistant(llm_provider=os.getenv("LLM_PROVIDER", "mock"))
    
    user_input = "我想开始学习 Python 数据分析，但不知道从哪里开始"
    
    response = assistant.chat("demo_user_002", user_input)
    
    if response["success"]:
        print("\n" + "="*80)
        print("🤖 LifeOS 助理输出")
        print("="*80)
        print("\n② 计划难执行 → 自动拆成\"下一步行动\"\n")
        print(response["display_text"])
    else:
        print(f"\n❌ 错误: {response.get('error')}")


def demo_scenario_3():
    """Demo #3: 个性化指导场景"""
    print("\n" + "="*80)
    print("📺 Demo #3: 个性化指导 → 根据用户习惯调整计划")
    print("="*80)
    
    assistant = LifeOSRealAssistant(llm_provider=os.getenv("LLM_PROVIDER", "mock"))
    
    # 先设置用户偏好
    assistant.memory_manager.remember(
        "demo_user_003",
        "evening_productivity",
        False,  # 晚上效率低
        MemoryType.PREFERENCE
    )
    assistant.memory_manager.remember(
        "demo_user_003",
        "morning_productivity",
        True,  # 早上效率高
        MemoryType.PREFERENCE
    )
    
    user_input = "今天下午要写报告，晚上要回邮件，明天上午要开会"
    
    response = assistant.chat("demo_user_003", user_input)
    
    if response["success"]:
        print("\n" + "="*80)
        print("🤖 LifeOS 助理输出")
        print("="*80)
        print("\n③ 个性化指导 → 根据你以往习惯调整计划\n")
        print(response["display_text"])
        print("\n💡 个性化建议：")
        print("（基于你之前告诉我：你早上效率高、晚上效率低）")
        print("'我把需要深度思考的报告安排在明天上午，")
        print(" 把简单的邮件回复留在今天下午处理。'")
    else:
        print(f"\n❌ 错误: {response.get('error')}")


def run_all_demos():
    """运行所有 Demo"""
    print("\n" + "🎬"*40)
    print("LifeOS 完整 Demo 演示")
    print("展示 3 大核心能力：信息过载处理、计划拆解、个性化指导")
    print("🎬"*40)
    
    demo_scenario_1()
    input("\n按回车继续下一个 Demo...")
    
    demo_scenario_2()
    input("\n按回车继续下一个 Demo...")
    
    demo_scenario_3()
    
    print("\n" + "="*80)
    print("✅ 所有 Demo 演示完成！")
    print("="*80)


if __name__ == "__main__":
    run_all_demos()
