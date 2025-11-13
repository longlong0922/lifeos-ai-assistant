"""
双模式切换与对话流程 (Dual-Mode Switching & Conversation Flow)
情绪支持模式 ↔ 行动助理模式

核心功能：
1. 意图分类（emotion / task / decision / mixed）
2. 自动模式切换
3. 模式内对话流程
4. 优雅降级与回退
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConversationMode(Enum):
    """对话模式"""
    EMOTION_SUPPORT = "emotion_support"  # 情绪支持模式
    ACTION_ASSISTANT = "action_assistant"  # 行动助理模式
    MIXED = "mixed"  # 混合模式（先情绪后行动）
    UNKNOWN = "unknown"  # 未知（需要澄清）


class IntentType(Enum):
    """意图类型"""
    EMOTION = "emotion"  # 情绪表达
    TASK = "task"  # 任务请求
    DECISION = "decision"  # 决策咨询
    MIXED = "mixed"  # 混合
    CASUAL = "casual"  # 闲聊
    UNKNOWN = "unknown"  # 未知


@dataclass
class IntentClassification:
    """意图分类结果"""
    intent: IntentType
    confidence: float
    signals: List[str]  # 触发的关键词/短语
    suggested_mode: ConversationMode
    brief_reason: str


# ============================================================================
# 关键词规则（快速分类）
# ============================================================================

EMOTION_KEYWORDS = [
    # 负面情绪
    "累", "疲惫", "难受", "焦虑", "崩溃", "想哭", "失落", "心烦",
    "压力大", "烦躁", "受不了", "痛苦", "抑郁", "绝望", "无助",
    "孤独", "害怕", "担心", "紧张", "不安", "迷茫", "困惑",
    # 正面情绪（也需要支持）
    "开心", "兴奋", "激动", "感动", "幸福", "满足",
    # 情绪表达句式
    "我感觉", "我很", "我觉得", "心里", "情绪"
]

TASK_KEYWORDS = [
    "要做", "完成", "今天要", "明天要", "清单", "事项", "排期",
    "计划", "提醒", "安排", "日程", "待办", "任务", "工作",
    "准备", "整理", "处理", "解决", "学习", "复习", "写",
    "看", "读", "买", "去", "打电话", "发", "回复", "联系"
]

DECISION_KEYWORDS = [
    "应该", "怎么做", "选哪个", "优先", "利弊", "建议",
    "帮我决定", "不知道选", "犹豫", "纠结", "选择",
    "要不要", "该不该", "可以吗", "好不好", "值得吗"
]

# 情绪句式模式
EMOTION_PATTERNS = [
    r"我(感觉|觉得|很|太|好|超级|有点)(累|难受|焦虑|烦|开心)",
    r"(压力|心情)(好|很|太)(大|差|糟|好)",
    r"受不了",
    r"(想|要)哭",
    r"心里(不舒服|难受|空空的)"
]

# 任务句式模式
TASK_PATTERNS = [
    r"今天(要|得|需要)(做|完成|处理)",
    r"明天(要|得|需要)(做|完成|处理)",
    r"帮我(安排|计划|整理|列出)",
    r"有.*件事",
    r".*清单",
]


# ============================================================================
# 意图分类器
# ============================================================================

class IntentClassifier:
    """意图分类器（基于规则 + 可扩展为 ML）"""
    
    @staticmethod
    def classify(user_input: str) -> IntentClassification:
        """
        分类用户输入
        
        Returns:
            IntentClassification 包含意图、置信度、信号等
        """
        text = user_input.lower().strip()
        
        # 检测情绪关键词
        emotion_signals = []
        for keyword in EMOTION_KEYWORDS:
            if keyword in text:
                emotion_signals.append(keyword)
        
        # 检测情绪句式
        for pattern in EMOTION_PATTERNS:
            if re.search(pattern, text):
                emotion_signals.append(f"pattern:{pattern[:20]}")
        
        # 检测任务关键词
        task_signals = []
        for keyword in TASK_KEYWORDS:
            if keyword in text:
                task_signals.append(keyword)
        
        # 检测任务句式
        for pattern in TASK_PATTERNS:
            if re.search(pattern, text):
                task_signals.append(f"pattern:{pattern[:20]}")
        
        # 检测决策关键词
        decision_signals = []
        for keyword in DECISION_KEYWORDS:
            if keyword in text:
                decision_signals.append(keyword)
        
        # 决策逻辑
        emotion_score = len(emotion_signals)
        task_score = len(task_signals)
        decision_score = len(decision_signals)
        
        # 混合情况
        if emotion_score > 0 and task_score > 0:
            return IntentClassification(
                intent=IntentType.MIXED,
                confidence=0.85,
                signals=emotion_signals + task_signals,
                suggested_mode=ConversationMode.MIXED,
                brief_reason="同时检测到情绪表达和任务请求，建议先情绪支持再转行动"
            )
        
        # 纯情绪
        if emotion_score >= 2 or (emotion_score == 1 and task_score == 0):
            return IntentClassification(
                intent=IntentType.EMOTION,
                confidence=min(0.7 + emotion_score * 0.1, 0.95),
                signals=emotion_signals,
                suggested_mode=ConversationMode.EMOTION_SUPPORT,
                brief_reason="检测到明确的情绪表达"
            )
        
        # 纯任务
        if task_score >= 2:
            return IntentClassification(
                intent=IntentType.TASK,
                confidence=min(0.7 + task_score * 0.1, 0.95),
                signals=task_signals,
                suggested_mode=ConversationMode.ACTION_ASSISTANT,
                brief_reason="检测到明确的任务请求"
            )
        
        # 决策
        if decision_score >= 1:
            return IntentClassification(
                intent=IntentType.DECISION,
                confidence=0.75,
                signals=decision_signals,
                suggested_mode=ConversationMode.ACTION_ASSISTANT,
                brief_reason="检测到决策咨询"
            )
        
        # 低置信度或闲聊
        if len(text) < 10 or any(word in text for word in ["你好", "在吗", "干嘛", "聊天"]):
            return IntentClassification(
                intent=IntentType.CASUAL,
                confidence=0.6,
                signals=["short_text"],
                suggested_mode=ConversationMode.EMOTION_SUPPORT,
                brief_reason="简短输入或闲聊"
            )
        
        # 未知
        return IntentClassification(
            intent=IntentType.UNKNOWN,
            confidence=0.4,
            signals=[],
            suggested_mode=ConversationMode.UNKNOWN,
            brief_reason="无法明确分类，需要澄清"
        )


# ============================================================================
# 对话流程管理器
# ============================================================================

@dataclass
class ConversationState:
    """对话状态"""
    current_mode: ConversationMode
    last_intent: IntentType
    turn_count: int = 0
    context: Dict = None  # 上下文信息
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


class ConversationFlowManager:
    """对话流程管理器"""
    
    def __init__(self):
        self.classifier = IntentClassifier()
    
    def route(
        self, 
        user_input: str, 
        state: Optional[ConversationState] = None
    ) -> Tuple[ConversationMode, IntentClassification, str]:
        """
        路由用户输入到合适的模式
        
        Returns:
            (选择的模式, 意图分类结果, 系统响应建议)
        """
        classification = self.classifier.classify(user_input)
        
        # 如果没有状态，创建新状态
        if state is None:
            state = ConversationState(
                current_mode=ConversationMode.UNKNOWN,
                last_intent=IntentType.UNKNOWN
            )
        
        # 根据分类结果决定模式
        if classification.confidence >= 0.6:
            chosen_mode = classification.suggested_mode
        else:
            # 低置信度，使用澄清策略
            chosen_mode = ConversationMode.UNKNOWN
        
        # 生成响应建议
        response_suggestion = self._generate_response_suggestion(
            classification, 
            chosen_mode,
            state
        )
        
        # 更新状态
        state.current_mode = chosen_mode
        state.last_intent = classification.intent
        state.turn_count += 1
        
        return chosen_mode, classification, response_suggestion
    
    def _generate_response_suggestion(
        self, 
        classification: IntentClassification,
        mode: ConversationMode,
        state: ConversationState
    ) -> str:
        """生成响应建议"""
        
        if mode == ConversationMode.EMOTION_SUPPORT:
            return self._emotion_support_response(classification)
        
        elif mode == ConversationMode.ACTION_ASSISTANT:
            return self._action_assistant_response(classification)
        
        elif mode == ConversationMode.MIXED:
            return self._mixed_mode_response(classification)
        
        else:  # UNKNOWN
            return self._clarification_response()
    
    def _emotion_support_response(self, classification: IntentClassification) -> str:
        """情绪支持模式响应"""
        templates = [
            "听起来你现在{emotion}，我理解这种感受。\n\n你想先说说怎么回事，还是让我帮你做点什么来缓解一下？",
            "感受到你的{emotion}了。别急，我们一起面对。\n\n要不要我帮你把压力源理一理，或者先给你一些放松的小建议？",
            "{emotion}的时候确实不容易。\n\n我可以帮你两件事：1）听你说说 2）帮你拆解任务降低压力。你想要哪个？"
        ]
        
        # 提取情绪词
        emotion_words = [s for s in classification.signals if s in EMOTION_KEYWORDS]
        emotion = emotion_words[0] if emotion_words else "不太好"
        
        import random
        template = random.choice(templates)
        
        return template.format(emotion=emotion)
    
    def _action_assistant_response(self, classification: IntentClassification) -> str:
        """行动助理模式响应"""
        if classification.intent == IntentType.TASK:
            return (
                "好的，我来帮你整理一下任务。\n\n"
                "请把你要做的事情告诉我（可以简单列一下），"
                "我会帮你挑出最重要的，并给你一个立即可以开始的第一步。"
            )
        
        elif classification.intent == IntentType.DECISION:
            return (
                "我来帮你分析这个决策。\n\n"
                "请告诉我：1）你在纠结什么 2）有哪些选项 3）你最在意什么（时间/成本/效果等）"
            )
        
        else:
            return "我来帮你把这件事拆解成可执行的步骤。请详细说说你的目标。"
    
    def _mixed_mode_response(self, classification: IntentClassification) -> str:
        """混合模式响应（情绪优先，但提供行动选项）"""
        return (
            "听起来你现在有点累，事情又有点多。\n\n"
            "我有两个建议：\n"
            "1️⃣ 先用 1 分钟深呼吸放松一下，然后我帮你挑出最重要的事\n"
            "2️⃣ 直接让我把你的事情整理成优先级清单\n\n"
            "你想试哪个？"
        )
    
    def _clarification_response(self) -> str:
        """澄清响应（低置信度时使用）"""
        return (
            "我想更好地帮到你。请问你现在是：\n\n"
            "🌿 想说说心情、聊聊天\n"
            "📋 需要帮忙安排任务、做决策\n\n"
            "随便说说就好～"
        )


# ============================================================================
# 模式切换触发器
# ============================================================================

class ModeSwitchTrigger:
    """模式切换触发器"""
    
    # 从情绪模式切换到行动模式的关键词
    EMOTION_TO_ACTION_TRIGGERS = [
        "帮我", "给我", "列出", "安排", "计划", "怎么办",
        "做点什么", "解决", "处理", "开始", "行动"
    ]
    
    # 从行动模式切换到情绪模式的关键词
    ACTION_TO_EMOTION_TRIGGERS = [
        "累了", "不想", "做不了", "太难", "压力大", "受不了",
        "先休息", "缓缓", "算了"
    ]
    
    @classmethod
    def should_switch_to_action(cls, user_input: str, current_mode: ConversationMode) -> bool:
        """是否应该从情绪模式切换到行动模式"""
        if current_mode != ConversationMode.EMOTION_SUPPORT:
            return False
        
        text = user_input.lower()
        return any(trigger in text for trigger in cls.EMOTION_TO_ACTION_TRIGGERS)
    
    @classmethod
    def should_switch_to_emotion(cls, user_input: str, current_mode: ConversationMode) -> bool:
        """是否应该从行动模式切换到情绪模式"""
        if current_mode != ConversationMode.ACTION_ASSISTANT:
            return False
        
        text = user_input.lower()
        return any(trigger in text for trigger in cls.ACTION_TO_EMOTION_TRIGGERS)


# ============================================================================
# 优雅降级策略
# ============================================================================

class FallbackStrategy:
    """降级策略"""
    
    @staticmethod
    def handle_unclear_input(input_text: str, attempt: int = 1) -> str:
        """处理不清楚的输入"""
        if attempt == 1:
            return (
                "不太确定你的意思，能再说得具体一点吗？\n\n"
                "比如：\n"
                "• 如果你想聊聊心情 → 说说你的感受\n"
                "• 如果你需要帮忙做事 → 告诉我你要做什么"
            )
        elif attempt == 2:
            return (
                "我可能理解得不太准确。要不这样，我给你两个快捷选项：\n\n"
                "1️⃣ 我想说说话，聊聊天\n"
                "2️⃣ 我需要帮忙安排任务\n\n"
                "选一个数字就好～"
            )
        else:
            return (
                "看起来我们沟通有点困难😅\n\n"
                "没关系，你可以：\n"
                "• 换个方式描述\n"
                "• 或者直接告诉我你想要什么帮助\n\n"
                "我会尽力理解的！"
            )
    
    @staticmethod
    def handle_too_complex(input_text: str) -> str:
        """处理过于复杂的输入"""
        return (
            "你说的内容有点多，让我一件一件来帮你。\n\n"
            "我们先从第一件事开始，你最想先处理哪个？"
        )
    
    @staticmethod
    def handle_need_professional_help() -> str:
        """需要专业帮助时的建议"""
        return (
            "我注意到你可能需要更专业的支持。\n\n"
            "虽然我能提供一些情绪支持和任务帮助，但如果你持续感到困扰，"
            "建议寻求专业心理咨询师的帮助。\n\n"
            "🌐 可以参考：\n"
            "• 心理咨询热线：12320\n"
            "• 在线心理咨询平台\n\n"
            "当然，我也会一直在这里陪伴你。"
        )


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    print("🧪 测试对话流程管理\n")
    
    flow_manager = ConversationFlowManager()
    
    test_cases = [
        "我感觉好累，今天还有好多事做不完",
        "今天要写报告、开会、还要买菜",
        "我不知道要不要接受这个工作机会",
        "心情好烦啊",
        "帮我安排一下明天的日程",
        "你好",
        "有点困惑，不知道从哪开始"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"[测试 {i}]")
        print(f"用户: {user_input}")
        
        mode, classification, response = flow_manager.route(user_input)
        
        print(f"意图: {classification.intent.value}")
        print(f"置信度: {classification.confidence:.2f}")
        print(f"模式: {mode.value}")
        print(f"信号: {', '.join(classification.signals[:3])}")
        print(f"理由: {classification.brief_reason}")
        print(f"\n系统建议响应:")
        print(response)
        print("\n" + "="*60 + "\n")
