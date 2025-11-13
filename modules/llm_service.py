"""
LLM 服务层
支持多种大模型接入：OpenAI、腾讯混元、本地模型等
"""

import os
import json
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from openai import OpenAI


class LLMProvider(ABC):
    """LLM 提供者基类"""
    
    @abstractmethod
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用 LLM 生成响应"""
        pass


class HunyuanProvider(LLMProvider):
    """腾讯混元大模型（通过 OpenAI 兼容接口）"""
    
    def __init__(
        self, 
        secret_id: str,
        secret_key: str,
        model: str = "hunyuan-large"
    ):
        self.model = model
        
        # 腾讯混元的 OpenAI 兼容接口
        self.client = OpenAI(
            api_key=secret_key,
            base_url="https://api.hunyuan.cloud.tencent.com/v1"
        )
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用混元大模型"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"混元 API 调用错误: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI 大模型"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用 OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 调用错误: {e}")
            raise


class MockProvider(LLMProvider):
    """Mock 提供者（用于测试）"""
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """返回模拟响应"""
        user_message = messages[-1]["content"] if messages else ""
        
        # 简单的规则匹配
        if any(keyword in user_message for keyword in ["累", "焦虑", "压力", "崩溃"]):
            return """听起来你现在压力挺大的。别急，我们一起来处理。

要不这样：
1️⃣ 先用1分钟深呼吸放松，然后我帮你挑最重要的
2️⃣ 直接让我把你的事情整理成清单

你想试试哪个？"""
        
        elif any(keyword in user_message for keyword in ["任务", "要做", "事情"]):
            return """{
  "one_line_summary": "用户有多个任务待处理",
  "categories": ["work", "personal"],
  "highlights": ["部分任务有时间限制", "任务量较多"],
  "priority_assessment": [
    {"item": "明天要交的报告", "importance": 10, "urgency": 10, "reason": "明天截止，必须今天完成"},
    {"item": "客户会面准备", "importance": 8, "urgency": 7, "reason": "今晚会议，需要提前准备"}
  ],
  "skip_candidates": ["不紧急的邮件"],
  "one_hour_actions": [
    {"desc": "打开报告文档，写3行摘要", "est_minutes": 5, "next_step": "打开文档开始", "type": "immediate"}
  ],
  "suggested_next_action": {
    "desc": "先花5分钟写报告摘要（最轻松的启动点）",
    "est_minutes": 5,
    "next_step": "打开报告文档，列出3个核心要点",
    "type": "immediate"
  },
  "confidence": 0.9
}"""
        
        else:
            return "我在这里陪你。你可以说说你现在的情况，或者告诉我你需要帮忙做什么。"


class LLMService:
    """LLM 服务管理器"""
    
    def __init__(self, provider_type: str = "mock"):
        """
        初始化 LLM 服务
        
        Args:
            provider_type: "openai" | "hunyuan" | "mock"
        """
        self.provider = self._create_provider(provider_type)
    
    def _create_provider(self, provider_type: str) -> LLMProvider:
        """创建 LLM 提供者"""
        
        if provider_type == "hunyuan":
            secret_id = os.getenv("TENCENT_SECRET_ID")
            secret_key = os.getenv("TENCENT_SECRET_KEY")
            model = os.getenv("HUNYUAN_MODEL", "hunyuan-large")
            
            if not secret_id or not secret_key:
                raise ValueError("缺少腾讯云配置：TENCENT_SECRET_ID 或 TENCENT_SECRET_KEY")
            
            return HunyuanProvider(secret_id, secret_key, model)
        
        elif provider_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            if not api_key:
                raise ValueError("缺少 OpenAI 配置：OPENAI_API_KEY")
            
            return OpenAIProvider(api_key, model)
        
        elif provider_type == "mock":
            return MockProvider()
        
        else:
            raise ValueError(f"不支持的 LLM 提供者: {provider_type}")
    
    def call(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用 LLM"""
        return self.provider.chat(messages, temperature, max_tokens)


# 全局 LLM 服务实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取全局 LLM 服务实例"""
    global _llm_service
    
    if _llm_service is None:
        provider_type = os.getenv("LLM_PROVIDER", "mock")
        _llm_service = LLMService(provider_type)
    
    return _llm_service


def init_llm_service(provider_type: str):
    """初始化 LLM 服务"""
    global _llm_service
    _llm_service = LLMService(provider_type)


# 便捷函数
def call_llm(
    messages: List[Dict[str, str]], 
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """便捷函数：调用 LLM"""
    service = get_llm_service()
    return service.call(messages, temperature, max_tokens)


if __name__ == "__main__":
    # 测试
    print("测试 LLM 服务\n")
    
    # 使用 Mock 提供者测试
    service = LLMService("mock")
    
    messages = [
        {"role": "system", "content": "你是 LifeOS 助手"},
        {"role": "user", "content": "我好累，今天还有好多事要做"}
    ]
    
    response = service.call(messages)
    print("Mock 响应:")
    print(response)
