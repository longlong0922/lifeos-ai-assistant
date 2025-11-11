# LifeOS AI Assistant 🚀

> 不只是习惯追踪，而是理解你的 AI 生活助手

LifeOS 是一个基于 AI 的智能生活助理，通过 **LangGraph** 实现多功能路由，帮助用户进行习惯追踪、决策支持、深度反思和目标管理。

## 🎉 新用户？从这里开始！

### ✨ **v1.1.0 新功能:完整用户认证系统!**

现在 LifeOS AI 支持:
- 🔐 **独立账号** - 每个用户都有自己的账号和数据
- 👤 **用户注册/登录** - 安全的密码加密和 JWT Token 认证  
- 🎓 **新手引导** - 首次使用时的友好引导流程
- 📊 **数据隔离** - 你的数据完全私密,只属于你

**➡️ [认证系统使用指南](docs/AUTHENTICATION.md)** - 了解登录、注册和安全机制 🔐  
**➡️ [Agent 工作原理](docs/AGENT_EXPLAINED.md)** - 了解 AI 如何处理你的消息 🤖

---

**➡️ [新用户快速上手指南](新用户快速上手.md)** - 5分钟快速入门教程 ⭐

或者直接运行：
```powershell
python start.py
# 选择你喜欢的使用方式！
```

## 📚 文档导航

- **[🎉 新用户快速上手](新用户快速上手.md)** - 5分钟入门教程（强烈推荐！）
- **[📘 用户界面指南](USER_GUIDE.md)** - Web、命令行、启动菜单完整指南
- **[📊 查看用户数据](docs/VIEW_USER_DATA.md)** - 如何查看和管理数据
- **[� 详细使用说明](HOW_TO_USE.md)** - 完整功能使用教程
- **[⚙️ 工作原理](HOW_IT_WORKS.md)** - 技术架构和原理
- **[🌐 API 开发指南](API_GUIDE.md)** - API 接口文档
- **[🚀 部署指南](DEPLOYMENT_GUIDE.md)** - 生产环境部署
- **[⚡ LLM 配置](QUICK_START_REAL_LLM.md)** - 配置真实 AI
- **[📊 项目总结](PROJECT_SUMMARY.md)** - 功能清单和技术细节
- **[🔌 在线 API 文档](http://localhost:8000/docs)** - 启动服务后访问

## ⚡ 超级快速开始（3步）

### 第一次使用？

```powershell
# 1. 进入项目目录
cd lifeos-ai-assistant

# 2. 一键启动
python start.py

# 3. 按照菜单提示选择！
```

就这么简单！系统会引导你完成一切。🎉

---

## ⚡ 传统方式快速开始（需要手动配置）

```powershell
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化（一次性）
python scripts\init_db.py
python scripts\load_sample_data.py

# 3. 启动服务
python run.py

# 4. 访问 http://localhost:8000/docs 开始使用
```

**💡 重要提示：**
- ✅ 默认使用 Mock 模式（无需 API key，立即可用）
- 🔑 如需更智能的 AI，可配置 OpenAI 或腾讯混元
  - 查看 **[部署指南 🚀](DEPLOYMENT_GUIDE.md)** 了解如何配置真实 LLM
  - 运行 `python scripts\test_llm.py` 测试配置
  - 运行 `python scripts\diagnose.py` 诊断问题

## ✨ 核心功能

### 1. 🎯 AI 习惯追踪器
- **不是监工，是教练**：AI 不会责怪你，而是帮你找到成功和失败的模式
- **模式识别**：自动分析你在什么时间、什么情境下最容易坚持
- **个性化建议**：基于你的历史数据给出真正有用的建议

### 2. 🔮 决策助手
- **苏格拉底式提问**：通过引导性问题帮你思考
- **基于历史**：分析你过去的决策和感受
- **不替你做决定**：给出洞察，而非指令

### 3. 📋 每日简报
- **能量预测**：基于睡眠、习惯完成情况预测今天的状态
- **智能排程**：在你效率最高的时段安排重要任务
- **风险提示**：提前预警可能的障碍

### 4. 💭 深度反思对话
- **长期模式识别**：发现重复出现的主题和情绪
- **洞察生成**：AI 帮你看到自己看不到的模式
- **非评判性**：温暖、共情的对话风格

### 5. 🎓 目标拆解器
- **从模糊到具体**：帮你明确目标
- **可执行计划**：分解为每日任务
- **立刻行动**：给出第一步，现在就开始

## 🏗️ 项目结构（概览）

```
LifeOS/
├── app/                    # 核心应用
│   ├── main.py            # FastAPI 入口
│   ├── graph.py           # LangGraph 状态图
│   ├── database.py        # SQLite 数据库
│   ├── models.py          # 数据模型
│   ├── llm_provider.py    # LLM 统一接口
│   └── nodes/             # LangGraph 节点
│
├── api/                   # API 路由
│
├── configs/              # 配置
│
├── data/                # 数据持久化
│
├── scripts/             # 辅助脚本
│   └── init_db.py      # 初始化数据库
│
├── docker/              # 容器化
│
└── tests/              # 测试
```

## 🚀 快速开始（Windows PowerShell）

### 方法 1：使用启动脚本（推荐）

```powershell
# 1. 克隆仓库
git clone https://github.com/yourusername/lifeos-ai-assistant.git
cd lifeos-ai-assistant

# 2. 创建虚拟环境并激活
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python scripts\init_db.py

# 5. 加载示例数据（可选）
python scripts\load_sample_data.py

# 6. 启动服务
python run.py
```

### 方法 2：使用 Docker

```powershell
# 构建并启动
cd docker
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务启动后：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health
- **根路径**: http://localhost:8000/

## 📖 API 使用示例

### 1. 聊天接口

```powershell
# 发送消息
curl -X POST "http://localhost:8000/api/chat" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": 1, \"message\": \"你好\"}'
```

### 2. 创建习惯

```powershell
curl -X POST "http://localhost:8000/api/habit" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": 1, \"name\": \"每天跑步\", \"description\": \"保持健康\"}'
```

### 3. 获取用户统计

```powershell
curl "http://localhost:8000/api/stats/1"
```

### 4. 获取每日简报

```powershell
curl "http://localhost:8000/api/brief/1"
```

## 🧪 运行测试

```powershell
# 运行所有测试
pytest -v

# 运行特定测试
python tests\test_graph.py
python tests\test_api.py

# 运行演示
python scripts\demo.py
```

## 📊 项目统计

- **代码文件**: 20+ 个 Python 模块
- **API 端点**: 10+ 个 REST API
- **数据库表**: 8 个核心表
- **测试覆盖**: Graph、API、Database 层
- **示例数据**: 完整的演示数据集