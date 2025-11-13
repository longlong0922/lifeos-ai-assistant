# LifeOS 模块使用指南

> 本目录包含 LifeOS（轻量生活助手）的核心模块实现

## 📚 模块概览

### 1. `smart_summary.py` - 智能摘要模块
**功能**: 处理信息过载，将杂乱任务整理成结构化摘要

**核心类**:
- `SmartSummaryParser`: 解析 LLM 响应
- `SummaryResult`: 摘要结果数据类

**主要 Prompt**:
- `SMART_SUMMARY_SYSTEM_PROMPT`: 系统提示词
- `FEW_SHOT_EXAMPLES`: Few-shot 示例

**使用示例**:
```python
from modules.smart_summary import SmartSummaryParser, build_smart_summary_prompt

# 构建 prompt
messages = build_smart_summary_prompt("今天要做很多事...")

# 调用 LLM（需要自己实现）
llm_response = call_your_llm(messages)

# 解析结果
parser = SmartSummaryParser()
result = parser.parse_llm_response(llm_response, user_input)

# 格式化显示
print(parser.format_for_display(result))
```

---

### 2. `next_action.py` - 下一步行动模块
**功能**: 把任务拆解成可执行的小步骤（优先 1-5 分钟）

**核心类**:
- `NextActionParser`: 解析任务拆解结果
- `NextActionResult`: 拆解结果数据类
- `UserPreferences`: 用户偏好

**使用示例**:
```python
from modules.next_action import NextActionParser, adjust_suggestions_by_preferences

# 构建 prompt
messages = build_next_action_prompt("学习 Python 数据分析")

# 调用 LLM
llm_response = call_your_llm(messages)

# 解析
parser = NextActionParser()
result = parser.parse_llm_response(llm_response)

# 根据用户偏好调整
prefs = UserPreferences(morning_productivity=True, prefers_short_tasks=True)
adjusted = adjust_suggestions_by_preferences(result, prefs)

print(parser.format_for_display(adjusted))
```

---

### 3. `memory.py` - 个性化记忆模块
**功能**: 轻量级用户偏好与习惯存储

**核心类**:
- `MemoryStore`: SQLite 存储实现
- `MemoryManager`: 高级记忆管理 API
- `UserProfile`: 用户画像

**使用示例**:
```python
from modules.memory import MemoryStore, MemoryManager, MemoryType

# 初始化
store = MemoryStore("lifeos_memory.db")
manager = MemoryManager(store)

# 记住偏好
manager.remember(
    user_id="user_001",
    key="morning_productivity",
    value=True,
    memory_type=MemoryType.PREFERENCE
)

# 回忆
is_morning_productive = manager.recall("user_001", "morning_productivity")

# 获取用户画像
profile = manager.get_user_profile("user_001")
print(f"早上效率高: {profile.morning_productivity}")

# 忘记所有记忆
manager.forget_all("user_001")
```

---

### 4. `conversation_flow.py` - 对话流程管理
**功能**: 意图分类、模式切换、对话路由

**核心类**:
- `IntentClassifier`: 意图分类器
- `ConversationFlowManager`: 对话流程管理器
- `ModeSwitchTrigger`: 模式切换触发器

**使用示例**:
```python
from modules.conversation_flow import ConversationFlowManager

flow_manager = ConversationFlowManager()

# 路由用户输入
user_input = "我好累，今天还有好多事"
mode, classification, response = flow_manager.route(user_input)

print(f"检测到的模式: {mode.value}")
print(f"意图: {classification.intent.value}")
print(f"置信度: {classification.confidence}")
print(f"\n建议响应:\n{response}")
```

---

### 5. `system_prompts.py` - 系统提示词
**功能**: 为不同模式提供系统提示词

**主要内容**:
- `MASTER_SYSTEM_PROMPT`: 主系统提示词
- `EMOTION_SUPPORT_PROMPT`: 情绪支持模式提示词
- `ACTION_ASSISTANT_PROMPT`: 行动助理模式提示词
- `FINE_TUNING_RECOMMENDATIONS`: 微调建议

**使用示例**:
```python
from modules.system_prompts import get_system_prompt, add_memory_context

# 获取情绪模式的系统提示词
prompt = get_system_prompt("emotion")

# 添加用户记忆上下文
user_memories = {
    "morning_productivity": True,
    "long_term_goals": ["学习Python"]
}
enhanced_prompt = add_memory_context(prompt, user_memories)

# 用于 LLM API
messages = [
    {"role": "system", "content": enhanced_prompt},
    {"role": "user", "content": "用户输入..."}
]
```

---

### 6. `ui_design.py` - UI 交互设计
**功能**: 前端 UI 设计规范和实现建议

**主要内容**:
- `PAGE_STRUCTURE`: 页面结构
- `COMPONENT_DESIGNS`: 组件设计
- `DESIGN_SYSTEM`: 视觉规范
- `INTERACTION_FLOWS`: 交互流程
- `IMPLEMENTATION_GUIDE`: 实现建议

**适用对象**: 前端开发人员

---

### 7. `integration_testing.py` - 集成测试
**功能**: 完整的集成步骤和测试用例

**主要内容**:
- `INTEGRATION_STEPS`: 分阶段集成指南
- `E2E_TEST_CASES`: 10 个端到端测试用例
- `EVALUATION_METRICS`: 评估指标与基准
- `DEPLOYMENT_CHECKLIST`: 部署检查清单

---

### 8. `lifeos_integration_example.py` - 集成示例
**功能**: 演示如何组合所有模块

**核心类**:
- `LifeOSAssistant`: 主助手类

**快速开始**:
```python
from modules.lifeos_integration_example import LifeOSAssistant

# 初始化
assistant = LifeOSAssistant(db_path="lifeos_memory.db")

# 处理用户输入
response = assistant.chat(
    user_id="user_001",
    user_input="我好累，今天还有好多事做不完"
)

# 查看响应
print(response["formatted_text"])

# 保存用户偏好
assistant.remember_preference("user_001", "morning_productivity", True)

# 获取用户画像
profile = assistant.get_user_profile("user_001")
```

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
# 测试智能摘要模块
python -m modules.smart_summary

# 测试下一步行动模块
python -m modules.next_action

# 测试记忆模块
python -m modules.memory

# 测试对话流程
python -m modules.conversation_flow

# 运行完整示例
python -m modules.lifeos_integration_example
```

---

## 🔧 集成到现有项目

### 方法1：直接导入
```python
from modules.lifeos_integration_example import LifeOSAssistant

assistant = LifeOSAssistant()
response = assistant.chat("user_id", "用户输入")
```

### 方法2：按需使用单个模块
```python
# 只使用智能摘要
from modules.smart_summary import SmartSummaryParser
parser = SmartSummaryParser()

# 只使用记忆功能
from modules.memory import MemoryManager
memory = MemoryManager(store)
```

### 方法3：构建自己的控制器
参考 `lifeos_integration_example.py` 中的 `LifeOSAssistant` 类实现

---

## 📊 架构图

```
用户输入
    ↓
[conversation_flow] 意图分类 & 模式路由
    ↓
    ├─→ [情绪支持模式]
    │       ↓
    │   [system_prompts] 获取情绪模式 prompt
    │       ↓
    │   返回同理响应 + 行动邀约
    │
    └─→ [行动助理模式]
            ↓
        判断任务类型
            ↓
            ├─→ [smart_summary] 生成摘要
            │       ↓
            │   优先级 + 下一步建议
            │
            └─→ [next_action] 任务拆解
                    ↓
                1-5分钟可执行步骤
            ↓
    [memory] 引用用户偏好 & 更新记忆
            ↓
    返回结构化响应
```

---

## 🎯 核心特性

✅ **双模式切换**: 自动识别情绪支持 vs 行动助理  
✅ **信息过载处理**: 智能摘要 + 优先级排序  
✅ **低摩擦启动**: 优先推荐 1-5 分钟任务  
✅ **个性化记忆**: 记住用户偏好与习惯  
✅ **可扩展架构**: 模块化设计，易于集成  

---

## 📝 注意事项

1. **LLM 集成**: 示例代码中的 LLM 调用是模拟的，需要接入真实的 LLM API（OpenAI / 本地模型）
2. **数据库**: 默认使用 SQLite，生产环境建议使用 PostgreSQL
3. **隐私**: 所有敏感记忆都应加密存储，提供"忘记我"功能
4. **性能**: 响应时间目标 < 3 秒（P95 < 5 秒）

---

## 🔗 相关文档

- [完整架构说明](../docs/architecture.md)（如果有）
- [API 文档](../docs/api.md)（如果有）
- [部署指南](../docs/deployment.md)（如果有）

---

## 🤝 贡献

欢迎贡献！请参考以下优先级：

1. 完善 LLM 集成（支持更多模型）
2. 增加测试覆盖率
3. 优化 prompt 工程
4. 改进用户体验

---

## 📄 许可证

[在此添加许可证信息]

---

## 💬 联系方式

[在此添加联系方式]
