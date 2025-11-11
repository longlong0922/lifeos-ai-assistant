# 🎯 LifeOS 使用指南

## 快速开始

你的 LifeOS AI Assistant 已经配置好了腾讯混元 LLM，现在有**三种使用方式**：

---

## 🌟 方式 1: 交互式聊天（最简单）

**一键启动，直接对话！**

```powershell
cd d:\code\progranm\lifeos-ai-assistant
python scripts\chat.py
```

**能做什么？**
- 💬 自然对话
- 🏃 记录习惯打卡
- 🔮 获取决策建议
- 🎯 拆解学习目标
- 💭 深度反思记录

**示例对话：**
```
😊 你: 我今天完成了跑步！
🤖 LifeOS: 太棒了！是什么让你今天成功了？记录下来可以帮助我们找到你的成功模式。

😊 你: 今天要不要去健身房？
🤖 LifeOS: 让我帮你分析一下。首先，你上次去健身房时感觉如何？

😊 你: 我想学 Python，怎么开始？
🤖 LifeOS: 很好的目标！让我们一起拆解，把它变成可执行的小步骤...
```

---

## 🎬 方式 2: 功能演示（快速体验）

**看看 LifeOS 能做什么**

```powershell
python scripts\demo_all.py
```

这会自动演示所有 5 大核心功能：
1. 💬 智能对话
2. 🏃 习惯追踪与教练
3. 🔮 决策支持
4. 🎯 目标拆解
5. 💭 深度反思

---

## 🌐 方式 3: Web API（最完整）

**启动 Web 服务，通过 HTTP API 调用**

### 启动服务

```powershell
python run.py
```

服务将在 `http://localhost:8000` 启动

### 访问 API 文档

在浏览器打开：
- **交互式文档**: http://localhost:8000/docs
- **API 说明**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/health

### API 端点

#### 1. 聊天接口

```powershell
curl -X POST "http://localhost:8000/api/chat" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": 1,
    "message": "我今天完成了跑步！"
  }'
```

#### 2. 创建习惯

```powershell
curl -X POST "http://localhost:8000/api/habit" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": 1,
    "name": "每天跑步",
    "description": "保持健康",
    "frequency": "daily"
  }'
```

#### 3. 获取用户统计

```powershell
curl "http://localhost:8000/api/stats/1"
```

#### 4. 创建目标

```powershell
curl -X POST "http://localhost:8000/api/goal" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": 1,
    "title": "学习 Python",
    "description": "掌握 Python 基础"
  }'
```

#### 5. 获取每日简报

```powershell
curl "http://localhost:8000/api/brief/1"
```

---

## 💡 使用场景示例

### 场景 1: 习惯追踪

**目标**: 养成跑步习惯

```
你: 我今天跑了5公里！
AI: 太棒了！具体说说，你是什么时候去跑的？心情如何？

你: 早上7点，感觉很清醒！
AI: 很好的发现！早上7点似乎是你的黄金时间。明天也试试这个时间吧！
```

### 场景 2: 决策支持

**目标**: 做出困难的选择

```
你: 我收到两个工作 offer，不知道选哪个
AI: 让我们一起分析。首先，你最看重工作的哪些方面？

你: 成长机会和工作氛围
AI: 那么，每个 offer 在这两方面的情况如何？上次你选择工作时，什么因素让你最满意？
```

### 场景 3: 目标拆解

**目标**: 学习新技能

```
你: 我想学 Python，完全零基础
AI: 很好的目标！让我们拆解成 21 天计划：

Week 1: 建立基础（第1-7天）
- Day 1: 安装 Python 和 VS Code (15分钟)
- Day 2: 学习变量和数据类型 (30分钟)
- Day 3: 编写第一个程序 (30分钟)
...

现在就开始：花10分钟访问 python.org 下载安装！
```

### 场景 4: 深度反思

**目标**: 自我认知

```
你: 最近总是焦虑，感觉很累
AI: 我理解你的感受。能具体说说什么让你焦虑吗？

你: 总担心工作做不完
AI: 我注意到这是你第3次提到工作焦虑了。上次你说过时间管理有问题。
    是否我们该聊聊如何改善时间规划？
```

---

## 🎯 核心功能说明

### 1. 习惯追踪与教练 🏃

**不是监工，是教练**
- ✅ 记录习惯完成情况
- ✅ 分析成功/失败模式
- ✅ 识别最佳时间和环境
- ✅ 个性化建议

**关键词触发**: 习惯、打卡、跑步、锻炼、坚持

### 2. 决策支持 🔮

**苏格拉底式提问**
- ✅ 引导性问题帮你思考
- ✅ 基于历史决策分析
- ✅ 不替你做决定，给洞察
- ✅ 考虑你的价值观和经验

**关键词触发**: 决策、选择、要不要、应该、还是

### 3. 每日简报 📋

**智能排程助手**
- ✅ 能量预测（基于睡眠和习惯）
- ✅ 今日重点任务推荐
- ✅ 风险提示和应对建议
- ✅ 个性化鼓励

**关键词触发**: 简报、今天计划、今日、安排

### 4. 目标拆解器 🎯

**从模糊到具体**
- ✅ 明确目标定义
- ✅ 21天可执行计划
- ✅ 每日具体任务
- ✅ 立刻可做的第一步

**关键词触发**: 目标、想学、想做、计划学、打算

### 5. 深度反思对话 💭

**长期模式识别**
- ✅ 发现重复主题
- ✅ 情绪模式分析
- ✅ 非评判性倾听
- ✅ 从抱怨到行动

**关键词触发**: 反思、回顾、今天怎么样、心情

---

## 🔧 高级使用

### 查看数据

```powershell
# 查看所有习惯
curl "http://localhost:8000/api/habit/1"

# 查看所有目标
curl "http://localhost:8000/api/goal/1"

# 查看反思记录
curl "http://localhost:8000/api/reflect/1"

# 查看统计信息
curl "http://localhost:8000/api/stats/1"
```

### 切换 LLM 提供者

```powershell
# 交互式切换
python scripts\switch_provider.py

# 或手动编辑 .env 文件
# LLM_PROVIDER="openai"  # 或 "hunyuan" 或 "mock"
```

### 测试和诊断

```powershell
# 测试 LLM 连接
python scripts\test_llm.py

# 系统诊断
python scripts\diagnose.py

# 简单测试
python scripts\test_simple.py
```

---

## 📊 数据管理

### 数据库位置
```
data/lifeos.db
```

### 查看数据
可以使用 SQLite 工具查看数据库：
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- VS Code 扩展: SQLite Viewer

### 备份数据
```powershell
# 备份
copy data\lifeos.db data\lifeos_backup.db

# 恢复
copy data\lifeos_backup.db data\lifeos.db
```

---

## ⚙️ 配置优化

### 调整模型温度

编辑 `app/nodes/` 中的各个节点文件，修改 `temperature` 参数：

```python
response = llm.chat(messages, temperature=0.7)  # 0.0-1.0
```

- `0.0-0.3`: 更准确、一致
- `0.4-0.7`: 平衡创意和准确性 ✅ **推荐**
- `0.8-1.0`: 更有创意、随机

### 控制响应长度

```python
response = llm.chat(messages, max_tokens=500)  # 调整数字
```

---

## 💰 成本控制

### 查看用量

访问腾讯云控制台查看 API 调用量和费用

### 降低成本

1. **使用更便宜的模型**
   ```env
   HUNYUAN_MODEL="hunyuan-lite"  # 最便宜
   ```

2. **减少 max_tokens**
   限制响应长度

3. **缓存常见响应**
   对重复问题使用缓存

---

## 🐛 故障排除

### 问题 1: 连接失败

```powershell
# 运行诊断
python scripts\diagnose.py
```

### 问题 2: 响应很慢

- 检查网络连接
- 考虑使用 hunyuan-lite 模型

### 问题 3: API 错误

```powershell
# 测试 API Key
python scripts\test_llm.py
```

### 查看日志

```powershell
type logs\lifeos.log
```

---

## 🎓 学习资源

- **项目文档**: `README.md`
- **部署指南**: `DEPLOYMENT_GUIDE.md`
- **API 参考**: `http://localhost:8000/docs`
- **更新日志**: `CHANGELOG_REAL_LLM.md`

---

## 🚀 下一步

1. **试试交互式聊天**: `python scripts\chat.py`
2. **看看功能演示**: `python scripts\demo_all.py`
3. **启动 Web 服务**: `python run.py`
4. **探索 API 文档**: http://localhost:8000/docs

---

**祝使用愉快！** 🎉

有问题随时问我！
