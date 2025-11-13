"""
LifeOS Modules - 轻量生活助手核心模块

导入快捷方式
"""

# 智能摘要模块
from .smart_summary import (
    SmartSummaryParser,
    SummaryResult,
    build_smart_summary_prompt,
    SMART_SUMMARY_SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES as SUMMARY_EXAMPLES
)

# 下一步行动模块
from .next_action import (
    NextActionParser,
    NextActionResult,
    UserPreferences,
    build_next_action_prompt,
    adjust_suggestions_by_preferences,
    NEXT_ACTION_SYSTEM_PROMPT
)

# 记忆模块
from .memory import (
    MemoryStore,
    MemoryManager,
    Memory,
    MemoryType,
    UserProfile
)

# 对话流程模块
from .conversation_flow import (
    ConversationFlowManager,
    IntentClassifier,
    ConversationMode,
    IntentType,
    IntentClassification,
    ConversationState
)

# 系统提示词模块
from .system_prompts import (
    MASTER_SYSTEM_PROMPT,
    EMOTION_SUPPORT_PROMPT,
    ACTION_ASSISTANT_PROMPT,
    get_system_prompt,
    add_memory_context
)

# LLM 服务模块
from .llm_service import (
    LLMService,
    LLMProvider,
    HunyuanProvider,
    OpenAIProvider,
    MockProvider,
    call_llm,
    init_llm_service,
    get_llm_service
)

# 集成示例
from .lifeos_integration_example import LifeOSAssistant

# 真实 LLM 集成
from .lifeos_real import LifeOSRealAssistant


__version__ = "2.0.0"

__all__ = [
    # 智能摘要
    'SmartSummaryParser',
    'SummaryResult',
    'build_smart_summary_prompt',
    'SMART_SUMMARY_SYSTEM_PROMPT',
    'SUMMARY_EXAMPLES',
    
    # 下一步行动
    'NextActionParser',
    'NextActionResult',
    'UserPreferences',
    'build_next_action_prompt',
    'adjust_suggestions_by_preferences',
    'NEXT_ACTION_SYSTEM_PROMPT',
    
    # 记忆
    'MemoryStore',
    'MemoryManager',
    'Memory',
    'MemoryType',
    'UserProfile',
    
    # 对话流程
    'ConversationFlowManager',
    'IntentClassifier',
    'ConversationMode',
    'IntentType',
    'IntentClassification',
    'ConversationState',
    
    # 系统提示词
    'MASTER_SYSTEM_PROMPT',
    'EMOTION_SUPPORT_PROMPT',
    'ACTION_ASSISTANT_PROMPT',
    'get_system_prompt',
    'add_memory_context',
    
    # LLM 服务
    'LLMService',
    'LLMProvider',
    'HunyuanProvider',
    'OpenAIProvider',
    'MockProvider',
    'call_llm',
    'init_llm_service',
    'get_llm_service',
    
    # 集成
    'LifeOSAssistant',
    'LifeOSRealAssistant',
]
