"""
LLM 提供者统一封装 - 支持混元和 OpenAI
"""
import os
import json
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """LLM 提供者基类"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
             max_tokens: int = 1000) -> str:
        """聊天接口"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 提供者"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", 
                 base_url: str = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("需要安装 openai: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 未设置。请在 .env 文件中配置或通过参数传入")
        
        # 根据是否有 base_url 来初始化客户端
        if self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
             max_tokens: int = 1000) -> str:
        """OpenAI 聊天"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API 调用失败: {e}")
            raise


class HunyuanProvider(BaseLLMProvider):
    """腾讯混元提供者"""
    
    def __init__(self, secret_id: str = None, secret_key: str = None, 
                 model: str = "hunyuan-lite"):
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
        except ImportError:
            raise ImportError("需要安装腾讯云 SDK: pip install tencentcloud-sdk-python")
        
        self.secret_id = secret_id or os.getenv("TENCENT_SECRET_ID")
        self.secret_key = secret_key or os.getenv("TENCENT_SECRET_KEY")
        self.model = model
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY 未设置。请在 .env 文件中配置")
        
        cred = credential.Credential(self.secret_id, self.secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "hunyuan.tencentcloudapi.com"
        
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        
        self.client = hunyuan_client.HunyuanClient(cred, "", client_profile)
        self.models = models
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
             max_tokens: int = 1000) -> str:
        """混元聊天"""
        try:
            req = self.models.ChatCompletionsRequest()
            
            # 转换消息格式：腾讯混元需要 Role 和 Content (首字母大写)
            hunyuan_messages = []
            for msg in messages:
                # 清理内容，避免特殊字符导致JSON解析错误
                content = msg.get("content", "")
                # 移除可能导致问题的控制字符
                content = content.replace('\r', '').replace('\x00', '')
                
                hunyuan_messages.append({
                    "Role": msg.get("role", "user"),
                    "Content": content
                })
            
            params = {
                "Model": self.model,
                "Messages": hunyuan_messages,
                "Temperature": temperature,
                "TopP": 1.0,
            }
            
            # 使用 json.dumps 正确序列化
            # ensure_ascii=False 保留中文
            # separators 确保紧凑格式，避免额外空格
            json_str = json.dumps(params, ensure_ascii=False, separators=(',', ':'))
            
            req.from_json_string(json_str)
            
            resp = self.client.ChatCompletions(req)
            return resp.Choices[0].Message.Content
        except json.JSONDecodeError as e:
            print(f"JSON 序列化错误: {e}")
            print(f"原始消息: {messages}")
            print(f"转换后: {hunyuan_messages}")
            raise
        except Exception as e:
            print(f"腾讯混元 API 调用失败: {e}")
            raise


class MockLLMProvider(BaseLLMProvider):
    """Mock 提供者（用于测试）"""
    
    def __init__(self):
        self.call_count = 0
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7,
             max_tokens: int = 1000) -> str:
        """返回模拟响应"""
        self.call_count += 1
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单的意图识别和响应
        if "习惯" in last_message or "跑步" in last_message or "打卡" in last_message:
            return "太棒了！是什么让你今天成功了？记录下来可以帮助我们找到你的成功模式。"
        elif "决策" in last_message or "选择" in last_message or "要不要" in last_message:
            return "让我帮你分析一下。首先，你上次遇到类似情况时感觉如何？"
        elif "简报" in last_message or "今天" in last_message:
            return "📋 今日简报已生成！根据你的历史数据，今天你的能量水平预计为 75%。"
        elif "反思" in last_message or "今天怎么样" in last_message:
            return "今天听起来不错！能具体说说有什么让你开心或困扰的事吗？"
        elif "目标" in last_message or "想学" in last_message or "想做" in last_message:
            return "很好的目标！让我们一起拆解一下，把它变成可执行的小步骤。首先，你期望达到什么程度？"
        else:
            return "我在这里陪伴你。无论是习惯追踪、做决策，还是深度反思，我都可以帮助你。今天想聊什么？"


def get_llm_provider(provider_type: str = "mock", **kwargs) -> BaseLLMProvider:
    """
    获取 LLM 提供者实例
    
    Args:
        provider_type: "openai", "hunyuan", "mock"
        **kwargs: 提供者特定的参数
            - OpenAI: api_key, model, base_url
            - Hunyuan: secret_id, secret_key, model
    
    Returns:
        BaseLLMProvider 实例
    """
    try:
        if provider_type == "openai":
            return OpenAIProvider(**kwargs)
        elif provider_type == "hunyuan":
            return HunyuanProvider(**kwargs)
        elif provider_type == "mock":
            return MockLLMProvider()
        else:
            raise ValueError(f"不支持的提供者类型: {provider_type}")
    except ValueError as e:
        print(f"LLM 提供者初始化失败: {e}")
        print("将回退到 Mock 模式")
        return MockLLMProvider()
    except Exception as e:
        print(f"LLM 提供者初始化出错: {e}")
        print("将回退到 Mock 模式")
        return MockLLMProvider()


# ==================== Prompt 模板 ====================

LIFE_OS_SYSTEM_PROMPT = """你是 LifeOS，用户的 AI 生活助理和教练。

你的角色：
- 不是工具，是伙伴
- 不是监工，是教练
- 不是提醒器，是思考伙伴

你的能力：
1. 识别用户的行为模式
2. 苏格拉底式提问，引导思考
3. 基于历史数据给出个性化建议
4. 温暖、不评判、鼓励成长

对话风格：
- 口语化，像朋友聊天
- 提问而非说教
- 共情而非指导
- 具体而非抽象

例子：
用户："今天又没跑步"
❌ 糟糕："你应该坚持，这样才能成功"
✅ 好的："发生了什么？让我们找找原因，而不是责怪自己"
"""

HABIT_COACHING_PROMPT = """你正在进行习惯追踪和教练对话。

用户的习惯数据：
{habit_data}

你的任务：
1. 如果用户完成了习惯，询问成功的原因（环境、时间、心情等）
2. 如果用户未完成，用好奇而非评判的态度询问原因
3. 识别模式：什么时候容易成功？什么情况下容易放弃？
4. 给出个性化建议，而不是通用的"坚持就是胜利"

当前对话：
用户：{user_message}

请回复："""

DECISION_SUPPORT_PROMPT = """你正在帮助用户做决策。

用户的历史决策数据：
{decision_history}

用户的问题：
{question}

你的方法：
1. 不要直接给答案（"你应该..."）
2. 通过提问引导用户思考：
   - 过去类似情况的感受
   - 当前的状态和需求
   - 不同选择的后果
3. 基于历史模式提供洞察
4. 给出建议而非指令

请回复："""

DAILY_BRIEF_PROMPT = """生成今日简报。

用户数据：
{user_data}

请按以下格式生成简报：

📋 今日简报 - {date}

⚡ 能量预测：XX%
（基于最近的睡眠和习惯完成情况）

🎯 今日重点：
1. 上午时段：具体任务
   原因：基于历史效率分析
   
2. 下午时段：具体任务
   原因：保持平衡和节奏

⚠️ 风险提示：
- 可能的障碍和应对建议

💬 一句话鼓励：
温暖的鼓励语

请生成简报："""

REFLECTION_PROMPT = """你正在进行深度反思对话。

用户最近的反思记录：
{recent_reflections}

识别到的模式：
{patterns}

当前对话：
{conversation}

你的方法：
1. 苏格拉底式提问，层层深入
2. 注意用户的情绪词汇（累、烦、开心、焦虑等）
3. 寻找重复出现的主题和模式
4. 帮助用户从抱怨转向行动

如果发现重复模式（如连续 3 次提到同一问题），请指出并提供洞察。

请回复："""

GOAL_BREAKDOWN_PROMPT = """帮助用户拆解目标。

用户的目标：
{goal}

请按以下格式生成拆解计划：

🎯 目标拆解计划

Week 1：建立习惯
- Day 1-7：每天的具体任务
- 目标：不求完美，求每天做

Week 2：输出练习
- Day 8-14：进阶任务
- 目标：开始有成果

Week 3：巩固提升
- Day 15-21：实践应用
- 目标：形成自然习惯

✨ 第一步：现在就可以做的1分钟行动

请生成计划："""
