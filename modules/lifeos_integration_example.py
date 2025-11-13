"""
LifeOS 集成示例
演示如何组合所有模块构建完整的对话系统
"""

import json
from typing import Dict, Optional
from datetime import datetime

# 导入所有核心模块
from modules.conversation_flow import (
    ConversationFlowManager, 
    ConversationState,
    ConversationMode
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


class LifeOSAssistant:
    """LifeOS 主助手类"""
    
    def __init__(self, db_path: str = "lifeos_memory.db"):
        """初始化"""
        # 初始化各模块
        self.flow_manager = ConversationFlowManager()
        self.summary_parser = SmartSummaryParser()
        self.action_parser = NextActionParser()
        
        # 初始化记忆模块
        memory_store = MemoryStore(db_path)
        self.memory_manager = MemoryManager(memory_store)
        
        # 对话状态缓存
        self.conversation_states: Dict[str, ConversationState] = {}
    
    def chat(self, user_id: str, user_input: str) -> Dict:
        """
        处理用户输入的主入口
        
        Args:
            user_id: 用户 ID
            user_input: 用户输入
            
        Returns:
            响应字典
        """
        try:
            # 1. 获取或创建对话状态
            state = self.conversation_states.get(user_id)
            
            # 2. 路由到合适的模式
            mode, classification, response_suggestion = self.flow_manager.route(
                user_input, 
                state
            )
            
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
            print(f"错误: {e}")
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
        """处理情绪支持模式"""
        return {
            "success": True,
            "mode": "emotion_support",
            "response_type": "text",
            "content": {
                "text": response_suggestion,
                "options": [
                    {"label": "🌿 说说话", "action": "continue_emotion"},
                    {"label": "📋 帮我做点什么", "action": "switch_to_action"}
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_action_mode(
        self, 
        user_id: str, 
        user_input: str,
        classification
    ) -> Dict:
        """处理行动助理模式"""
        
        # 判断是摘要还是拆解
        if "要做" in user_input or "任务" in user_input or len(classification.signals) > 2:
            # 生成摘要
            return self._generate_summary(user_id, user_input)
        else:
            # 生成任务拆解
            return self._generate_action_plan(user_id, user_input)
    
    def _handle_mixed_mode(
        self, 
        user_id: str, 
        user_input: str, 
        response_suggestion: str
    ) -> Dict:
        """处理混合模式"""
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
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_unknown(self, user_id: str, response_suggestion: str) -> Dict:
        """处理未知情况"""
        return {
            "success": True,
            "mode": "clarification",
            "response_type": "text",
            "content": {
                "text": response_suggestion
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_summary(self, user_id: str, user_input: str) -> Dict:
        """生成智能摘要（模拟 LLM 调用）"""
        
        # 在实际应用中，这里会调用 LLM API
        # messages = build_smart_summary_prompt(user_input)
        # llm_response = call_llm(messages)
        
        # 这里使用模拟响应
        mock_llm_response = self._mock_summary_response(user_input)
        
        # 解析响应
        result = self.summary_parser.parse_llm_response(mock_llm_response, user_input)
        
        if result:
            # 获取用户偏好进行调整
            profile = self.memory_manager.get_user_profile(user_id)
            
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
                    }
                },
                "formatted_text": self.summary_parser.format_for_display(result),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "无法解析摘要"
            }
    
    def _generate_action_plan(self, user_id: str, user_input: str) -> Dict:
        """生成下一步行动计划（模拟 LLM 调用）"""
        
        # 模拟 LLM 响应
        mock_llm_response = self._mock_action_response(user_input)
        
        # 解析响应
        result = self.action_parser.parse_llm_response(mock_llm_response)
        
        if result:
            # 根据用户偏好调整
            prefs = UserPreferences(
                morning_productivity=True,
                prefers_short_tasks=True
            )
            adjusted_result = adjust_suggestions_by_preferences(result, prefs)
            
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
                "formatted_text": self.action_parser.format_for_display(adjusted_result),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "无法解析行动计划"
            }
    
    def _mock_summary_response(self, user_input: str) -> str:
        """模拟智能摘要的 LLM 响应"""
        return """{
  "one_line_summary": "用户有多个任务待处理",
  "categories": ["work", "personal"],
  "highlights": ["部分任务有时间限制", "任务量较多"],
  "priority_assessment": [
    {"item": "第一个任务", "importance": 8, "urgency": 7, "reason": "工作相关"},
    {"item": "第二个任务", "importance": 6, "urgency": 5, "reason": "可推迟"}
  ],
  "skip_candidates": ["不紧急的任务"],
  "one_hour_actions": [
    {
      "desc": "完成第一个小步骤",
      "est_minutes": 5,
      "next_step": "立即开始",
      "type": "immediate"
    }
  ],
  "suggested_next_action": {
    "desc": "先完成最简单的任务",
    "est_minutes": 5,
    "next_step": "打开工具开始",
    "type": "immediate"
  },
  "confidence": 0.85
}"""
    
    def _mock_action_response(self, user_input: str) -> str:
        """模拟任务拆解的 LLM 响应"""
        return """{
  "task": "用户的任务",
  "candidate_actions": [
    {
      "desc": "第一步：准备工作",
      "est_minutes": 3,
      "type": "prep",
      "suggest_add_to_calendar": false,
      "prerequisites": [],
      "expected_outcome": "准备就绪",
      "difficulty": 1
    },
    {
      "desc": "第二步：开始执行",
      "est_minutes": 15,
      "type": "immediate",
      "suggest_add_to_calendar": false,
      "prerequisites": ["第一步"],
      "expected_outcome": "完成主要部分",
      "difficulty": 2
    }
  ],
  "recommended_action_index": 0,
  "rationale": "先从简单的准备工作开始",
  "total_est_minutes": 18,
  "completion_strategy": "sequential",
  "confidence": 0.9
}"""
    
    def remember_preference(
        self, 
        user_id: str, 
        key: str, 
        value: any
    ) -> bool:
        """记住用户偏好"""
        try:
            self.memory_manager.remember(
                user_id=user_id,
                key=key,
                value=value,
                memory_type=MemoryType.PREFERENCE
            )
            return True
        except Exception as e:
            print(f"记忆保存失败: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Dict:
        """获取用户画像"""
        profile = self.memory_manager.get_user_profile(user_id)
        return {
            "morning_productivity": profile.morning_productivity,
            "prefers_short_tasks": profile.prefers_short_tasks,
            "planning_style": profile.planning_style,
            "long_term_goals": profile.long_term_goals
        }
    
    def forget_user_data(self, user_id: str) -> bool:
        """忘记用户数据"""
        return self.memory_manager.forget_all(user_id)


# ============================================================================
# 使用示例
# ============================================================================

def demo():
    """演示如何使用 LifeOS"""
    
    print("=" * 60)
    print("LifeOS 集成示例")
    print("=" * 60)
    
    # 初始化助手
    assistant = LifeOSAssistant(db_path="demo_lifeos.db")
    
    # 测试用例
    test_cases = [
        ("user_001", "我好累啊，今天还有好多事"),
        ("user_001", "帮我整理一下任务"),
        ("user_002", "今天要写报告、开会、买菜"),
        ("user_002", "我要学习 Python"),
    ]
    
    for user_id, user_input in test_cases:
        print(f"\n用户 ({user_id}): {user_input}")
        print("-" * 60)
        
        # 调用助手
        response = assistant.chat(user_id, user_input)
        
        # 显示响应
        if response["success"]:
            print(f"模式: {response['mode']}")
            print(f"响应类型: {response['response_type']}")
            
            if "formatted_text" in response:
                print("\n格式化输出:")
                print(response["formatted_text"])
            else:
                print("\n响应内容:")
                print(json.dumps(response["content"], indent=2, ensure_ascii=False))
        else:
            print(f"错误: {response.get('error')}")
        
        print("=" * 60)
    
    # 演示记忆功能
    print("\n\n记忆功能演示:")
    print("-" * 60)
    
    # 保存偏好
    assistant.remember_preference("user_001", "morning_productivity", True)
    assistant.remember_preference("user_001", "prefers_short_tasks", True)
    
    # 获取画像
    profile = assistant.get_user_profile("user_001")
    print(f"用户画像: {json.dumps(profile, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    demo()
