# 🤔 LifeOS 如何知道你的习惯和数据？

## 数据来源方式

LifeOS 通过以下几种方式获取和管理你的数据：

---

## 1️⃣ 初始示例数据

### 系统自带演示数据

当你运行以下命令时：
```powershell
python scripts\load_sample_data.py
```

系统会加载 `data/samples/demo_data.json` 中的示例数据，包括：

- **习惯**: 每天跑步、阅读、冥想
- **习惯记录**: 过去几天的打卡情况
- **反思记录**: 之前的对话和洞察
- **目标**: 学习目标和计划
- **决策记录**: 历史决策

**这是为了让你能快速体验功能！**

---

## 2️⃣ 对话中自动记录

### AI 在聊天时会自动记录数据

当你和 LifeOS 对话时，系统会：

#### 场景 A: 习惯打卡
```
你: 我今天完成了跑步！
```
↓
系统自动：
- ✅ 识别意图为"习惯追踪"
- ✅ 查找你的"跑步"习惯
- ✅ 记录一条 `completed` 状态的记录
- ✅ 保存上下文（"感觉很棒"等）

#### 场景 B: 未完成习惯
```
你: 今天没去跑步，太累了
```
↓
系统自动：
- ✅ 记录 `missed` 状态
- ✅ 保存原因（"太累了"）
- ✅ 用于后续模式分析

#### 场景 C: 反思记录
```
你: 今天心情不好
AI: 能说说发生了什么吗？
你: 工作不顺利...
```
↓
系统自动：
- ✅ 保存完整对话历史
- ✅ 识别情绪关键词
- ✅ 发现重复模式

---

## 3️⃣ API 手动创建

### 通过 API 主动创建习惯

你可以通过 Web API 手动创建习惯：

```powershell
# 创建新习惯
curl -X POST "http://localhost:8000/api/habit" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": 1,
    "name": "学习Python",
    "description": "每天学习30分钟",
    "target_frequency": "daily"
  }'
```

---

## 📊 数据库结构

所有数据存储在 SQLite 数据库 `data/lifeos.db` 中：

```
📁 数据库表结构:

├── users               # 用户信息
├── habits              # 习惯定义
├── habit_records       # 习惯打卡记录
├── reflections         # 反思对话记录
├── decisions           # 决策记录
├── goals               # 目标和计划
└── chat_messages       # 聊天历史
```

---

## 🔍 查看当前数据

### 方法 1: 命令行查询

```powershell
# 查看所有习惯
curl "http://localhost:8000/api/habit/1"

# 查看统计信息
curl "http://localhost:8000/api/stats/1"
```

### 方法 2: 交互式聊天

在 `python scripts\chat.py` 中输入：
```
stats
```

### 方法 3: 直接查看数据库

使用 SQLite 工具打开 `data/lifeos.db`

---

## 💡 实际工作流程示例

### 完整对话示例

```
😊 你: 我想养成跑步习惯

🤖 AI: 很好的想法！让我为你创建这个习惯...
      (系统在 habits 表创建记录)

😊 你: 我今天跑了5公里！

🤖 AI: 太棒了！是什么让你今天成功的？
      (系统在 habit_records 表记录 completed)

😊 你: 天气好，早上7点去的

🤖 AI: 好的，我记下了。早上7点似乎是你的黄金时间
      (系统保存 context: "天气好，早上7点")

😊 你: 帮我分析一下我的跑步习惯

🤖 AI: 查看你的记录...
      - 最近7天完成了5次
      - 成功率: 71%
      - 最佳时间: 早上7点
      - 成功因素: 天气好、早起
      (系统查询 habit_records 并分析模式)
```

---

## 🎯 关键点理解

### 1. AI 不会"无中生有"

- ❌ AI 不会凭空知道你的习惯
- ✅ AI 从数据库读取你创建的习惯
- ✅ AI 从对话中提取并保存信息

### 2. 初次使用需要创建数据

**选项 A: 加载示例数据**（快速体验）
```powershell
python scripts\load_sample_data.py
```

**选项 B: 自己创建**（从零开始）
通过对话或 API 创建你的习惯和目标

### 3. 数据越多，AI 越智能

随着你的使用：
- 📈 记录越来越多
- 🧠 AI 能识别更多模式
- 💡 建议越来越个性化

---

## 🔧 数据管理

### 查看现有数据

```powershell
# 启动服务
python run.py

# 查看 API 文档
浏览器打开: http://localhost:8000/docs

# 使用 GET 端点查看所有数据
```

### 清空数据重新开始

```powershell
# 备份现有数据
copy data\lifeos.db data\lifeos_backup.db

# 删除数据库
del data\lifeos.db

# 重新初始化
python scripts\init_db.py
python scripts\load_sample_data.py
```

### 导出数据

未来可以添加导出功能，将数据导出为 JSON

---

## 📖 使用建议

### 新用户（第一次使用）

1. **加载示例数据** - 快速体验功能
   ```powershell
   python scripts\load_sample_data.py
   ```

2. **试试交互式聊天**
   ```powershell
   python scripts\chat.py
   ```

3. **输入**: "帮我分析一下最近的习惯"
   - 看看 AI 如何使用示例数据

4. **创建自己的习惯**
   - 说："我想养成XXX习惯"
   - AI 会引导你创建

### 老用户（已有数据）

- 继续日常打卡和反思
- 数据会持续积累
- AI 的建议会越来越准确

---

## 🤖 AI 的"记忆"原理

```
用户对话 
   ↓
识别意图（习惯/反思/决策等）
   ↓
调用对应节点处理
   ↓
查询数据库获取历史数据
   ↓
组装成 prompt 发给 LLM
   ↓
LLM 基于历史数据生成响应
   ↓
保存新的记录到数据库
```

**关键**: AI 本身不记忆，但每次对话都会：
1. 从数据库读取你的历史
2. 结合当前对话
3. 生成个性化响应
4. 保存新的记录

---

## ❓ 常见问题

### Q: AI 怎么知道我有跑步习惯？
A: 
- 要么你之前创建过
- 要么加载了示例数据
- 要么对话中提到并被记录

### Q: 我的数据安全吗？
A: 
- 所有数据存储在本地 `data/lifeos.db`
- 不会上传到任何服务器
- 只有 LLM API 调用会发送当前对话内容

### Q: 可以修改或删除记录吗？
A: 
- 目前需要直接操作数据库
- 未来版本会添加管理界面

### Q: 能导入导出数据吗？
A: 
- 数据库文件可以直接复制
- 可以自己写脚本导出为 JSON

---

## 🚀 下一步

1. **加载示例数据**: `python scripts\load_sample_data.py`
2. **开始对话**: `python scripts\chat.py`
3. **查看数据**: 访问 http://localhost:8000/docs
4. **创建自己的习惯**: 通过对话或 API

---

**总结**: LifeOS 就像一个智能笔记本，它会记录你告诉它的所有信息，并在需要时调取这些信息来提供个性化建议。🎯
