# LifeOS API 使用文档

## 快速开始

### 1. 基础使用

```python
from modules.lifeos_real import LifeOSRealAssistant

# 初始化助手（自动读取 .env 配置）
assistant = LifeOSRealAssistant()

# 简单对话
response = assistant.chat(
    user_id="user_001",
    user_input="今天有好多事要做，感觉好累"
)

# 获取响应文本
print(response["display_text"])
```

### 2. 指定 LLM 提供者

```python
# 使用腾讯混元
assistant = LifeOSRealAssistant(llm_provider="hunyuan")

# 使用 OpenAI
assistant = LifeOSRealAssistant(llm_provider="openai")

# 使用 Mock 模式（测试）
assistant = LifeOSRealAssistant(llm_provider="mock")
```

## 核心 API

### LifeOSRealAssistant

主控制器类，协调所有模块。

#### 初始化

```python
assistant = LifeOSRealAssistant(
    db_path="lifeos_data.db",  # 数据库路径
    llm_provider="hunyuan"      # LLM 提供者
)
```

#### chat() 方法

处理用户输入，返回结构化响应。

**参数：**
- `user_id` (str): 用户唯一标识
- `user_input` (str): 用户输入文本

**返回：**
```python
{
    "success": True,                    # 是否成功
    "mode": "action_assistant",         # 模式：emotion_support / action_assistant / mixed
    "response_type": "summary_card",    # 响应类型
    "content": {                        # 结构化内容
        "summary": "...",
        "priorities": [...],
        "suggested_action": {...}
    },
    "display_text": "...",             # 可直接显示的文本
    "timestamp": "2024-01-13T10:30:00"
}
```

**示例：**

```python
# 情绪支持场景
response = assistant.chat("user_001", "我今天心情不好")
# mode = "emotion_support"

# 任务处理场景
response = assistant.chat("user_001", "帮我整理今天的任务")
# mode = "action_assistant"
# response_type = "summary_card"

# 任务拆解场景
response = assistant.chat("user_001", "我想学习 Python")
# mode = "action_assistant"
# response_type = "action_plan"
```

### 记忆管理

记录用户偏好和习惯。

```python
from modules.memory import MemoryType

# 记录偏好
assistant.memory_manager.remember(
    user_id="user_001",
    key="morning_productivity",
    value=True,
    memory_type=MemoryType.PREFERENCE
)

# 记录习惯
assistant.memory_manager.remember(
    user_id="user_001",
    key="work_start_time",
    value="9:00",
    memory_type=MemoryType.ROUTINE
)

# 记录长期目标
assistant.memory_manager.remember(
    user_id="user_001",
    key="career_goal",
    value="成为数据科学家",
    memory_type=MemoryType.GOAL
)

# 获取用户画像
profile = assistant.memory_manager.get_user_profile("user_001")
print(profile.morning_productivity)  # True
print(profile.long_term_goals)       # ["成为数据科学家"]

# 删除记忆
assistant.memory_manager.forget("user_001", "morning_productivity")
```

### 直接调用 LLM

```python
from modules.llm_service import call_llm

messages = [
    {"role": "system", "content": "你是 LifeOS 助手"},
    {"role": "user", "content": "帮我整理任务"}
]

response = call_llm(
    messages,
    temperature=0.7,
    max_tokens=1500
)
```

## 响应类型详解

### 1. 情绪支持响应 (emotion_support)

```python
{
    "success": True,
    "mode": "emotion_support",
    "response_type": "text",
    "content": {
        "text": "听起来你现在...",
        "options": [
            {"label": "🌿 说说话", "action": "continue_emotion"},
            {"label": "📋 帮我整理任务", "action": "switch_to_action"}
        ]
    },
    "display_text": "..."
}
```

### 2. 智能摘要响应 (summary_card)

```python
{
    "success": True,
    "mode": "action_assistant",
    "response_type": "summary_card",
    "content": {
        "summary": "用户有5个任务待处理",
        "categories": ["work", "personal"],
        "highlights": ["部分任务时间紧迫"],
        "priorities": [
            {
                "item": "明天要交的报告",
                "importance": 10,
                "urgency": 10,
                "reason": "明天截止"
            }
        ],
        "suggested_action": {
            "desc": "先花5分钟写报告摘要",
            "est_minutes": 5,
            "next_step": "打开文档，列出3个要点"
        },
        "skip_candidates": ["不紧急的邮件"]
    }
}
```

### 3. 任务拆解响应 (action_plan)

```python
{
    "success": True,
    "mode": "action_assistant",
    "response_type": "action_plan",
    "content": {
        "task": "学习 Python 数据分析",
        "actions": [
            {
                "desc": "安装 Anaconda 环境",
                "est_minutes": 5,
                "type": "immediate",
                "difficulty": "easy",
                "expected_outcome": "环境安装完成"
            },
            {
                "desc": "下载数据集",
                "est_minutes": 20,
                "type": "prep",
                "difficulty": "easy",
                "expected_outcome": "有了练手数据"
            }
        ],
        "recommended_index": 0,
        "rationale": "推荐从最简单的环境安装开始"
    }
}
```

## 高级用法

### 1. 自定义 LLM 提供者

```python
from modules.llm_service import LLMProvider, LLMService

class CustomProvider(LLMProvider):
    def chat(self, messages, temperature=0.7, max_tokens=2000):
        # 实现你的 LLM 调用逻辑
        response = your_llm_api(messages)
        return response

# 注册自定义提供者
service = LLMService()
service.provider = CustomProvider()
```

### 2. 批量处理

```python
user_inputs = [
    "今天要做什么",
    "帮我整理任务",
    "我想学编程"
]

results = []
for user_input in user_inputs:
    response = assistant.chat("user_001", user_input)
    results.append(response)
```

### 3. 持久化会话

```python
# 会话状态会自动保存在数据库中
# 用户下次访问时会记住之前的偏好

# 获取用户画像
profile = assistant.memory_manager.get_user_profile("user_001")

# 基于画像提供个性化服务
if profile.morning_productivity:
    print("建议早上处理重要任务")
```

## 错误处理

```python
response = assistant.chat("user_001", user_input)

if response["success"]:
    print(response["display_text"])
else:
    error_message = response.get("error", "未知错误")
    fallback = response.get("fallback_message", "")
    print(f"错误: {error_message}")
    print(f"回退响应: {fallback}")
```

## 环境配置

### .env 文件

```ini
# LLM 提供者
LLM_PROVIDER="hunyuan"

# 腾讯混元
TENCENT_SECRET_ID="your_id"
TENCENT_SECRET_KEY="your_key"
HUNYUAN_MODEL="hunyuan-large"

# OpenAI（可选）
OPENAI_API_KEY="sk-xxx"
OPENAI_MODEL="gpt-3.5-turbo"

# 数据库
DB_PATH="data/lifeos.db"
```

## 性能优化建议

1. **缓存 LLM 响应**
   ```python
   # TODO: 实现响应缓存
   ```

2. **异步处理**
   ```python
   # TODO: 使用 asyncio 提升并发性能
   ```

3. **批量 API 调用**
   ```python
   # TODO: 批量调用 LLM API
   ```

## 最佳实践

1. **合理使用 Mock 模式**
   - 开发时使用 Mock 模式节省 API 费用
   - 生产环境切换到真实 LLM

2. **用户画像更新**
   - 定期更新用户偏好
   - 根据行为模式调整记忆

3. **错误处理**
   - 始终检查 `response["success"]`
   - 提供友好的错误提示

4. **隐私保护**
   - 敏感信息不要存入记忆
   - 支持用户"忘记我"功能

---

更多信息请参考 [README.md](README.md) 和 [UPGRADE_REPORT.md](UPGRADE_REPORT.md)
