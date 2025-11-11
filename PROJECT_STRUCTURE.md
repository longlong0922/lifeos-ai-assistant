# 📁 LifeOS 项目结构说明

## 🎯 整理后的清爽结构

```
lifeos-ai-assistant/
├── 📄 核心文件
│   ├── .env                    # 环境配置（API密钥等）
│   ├── .env.example            # 配置模板
│   ├── .gitignore              # Git忽略规则
│   ├── requirements.txt        # Python依赖
│   ├── run.py                  # Web服务启动脚本
│   └── start.py                # 用户友好的启动菜单 ⭐
│
├── 📚 文档
│   ├── README.md               # 项目主页
│   ├── 新用户快速上手.md       # 5分钟入门教程 ⭐
│   ├── 新用户使用总结.md       # 使用方式对比
│   ├── USER_GUIDE.md           # 用户界面完整指南
│   ├── HOW_TO_USE.md           # 详细使用说明
│   ├── HOW_IT_WORKS.md         # 技术架构原理
│   ├── API_GUIDE.md            # API开发文档
│   ├── DEPLOYMENT_GUIDE.md     # 部署指南
│   ├── QUICK_START_REAL_LLM.md # LLM配置教程
│   └── PROJECT_SUMMARY.md      # 项目完整总结
│
├── 📂 核心代码
│   ├── app/                    # 应用主代码
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── graph.py           # LangGraph工作流
│   │   ├── database.py        # 数据库操作
│   │   ├── llm_provider.py    # LLM统一接口
│   │   ├── models.py          # 数据模型
│   │   └── nodes/             # LangGraph节点
│   │       ├── router_node.py     # 路由节点
│   │       ├── habit_node.py      # 习惯追踪
│   │       ├── plan_node.py       # 每日规划
│   │       ├── reflect_node.py    # 深度反思
│   │       ├── coach_node.py      # 决策和目标
│   │       └── chat_node.py       # 普通对话
│   │
│   ├── api/                    # API路由
│   │   ├── routes_chat.py     # 聊天相关接口
│   │   └── routes_habit.py    # 习惯管理接口
│   │
│   └── web/                    # Web界面
│       └── index.html         # 漂亮的聊天界面
│
├── 🛠️ 工具脚本
│   └── scripts/
│       ├── chat.py            # 命令行聊天
│       ├── demo.py            # 功能演示
│       ├── demo_all.py        # 完整演示
│       ├── load_sample_data.py # 加载示例数据
│       ├── view_user_data.py  # 查看用户数据 ⭐
│       ├── show_data.py       # 快速查看数据
│       ├── test_llm.py        # 测试LLM连接
│       ├── diagnose.py        # 系统诊断
│       ├── switch_provider.py # 切换LLM提供者
│       └── cleanup_files.py   # 文件清理工具
│
├── 📊 数据存储
│   └── data/
│       ├── lifeos.db          # SQLite数据库
│       └── samples/           # 示例数据
│
├── ⚙️ 配置
│   └── configs/
│       └── settings.py        # 应用配置
│
├── 📝 文档补充
│   └── docs/
│       └── VIEW_USER_DATA.md  # 数据查看工具文档
│
├── 🧪 测试
│   └── tests/
│       ├── test_graph.py      # 工作流测试
│       ├── test_api.py        # API测试
│       └── test_db.py         # 数据库测试
│
├── 🐳 容器化
│   └── docker/
│       ├── Dockerfile
│       └── docker-compose.yml
│
└── 📋 其他
    ├── .github/               # GitHub配置
    └── logs/                  # 日志文件
```

---

## 🎯 关键入口点

### 新用户从这里开始
```powershell
python start.py
```
启动菜单，选择使用方式

### 命令行聊天
```powershell
python scripts\chat.py
```
直接开始对话

### Web界面
```powershell
python run.py
```
浏览器访问 http://localhost:8000

### 查看数据
```powershell
python scripts\view_user_data.py
```
查看所有用户数据

---

## 📚 文档阅读顺序

### 🎯 新手必读（按顺序）
1. **README.md** - 快速了解项目
2. **新用户快速上手.md** - 5分钟上手
3. **新用户使用总结.md** - 使用方式对比
4. **USER_GUIDE.md** - 界面使用指南

### 📘 进阶阅读
5. **HOW_TO_USE.md** - 详细功能说明
6. **docs/VIEW_USER_DATA.md** - 数据管理
7. **HOW_IT_WORKS.md** - 技术原理

### 🔧 开发者阅读
8. **API_GUIDE.md** - API开发
9. **DEPLOYMENT_GUIDE.md** - 生产部署
10. **PROJECT_SUMMARY.md** - 完整技术总结

---

## 🗂️ 目录职责

### `app/` - 应用核心
- 所有业务逻辑
- LangGraph工作流
- 数据库操作
- LLM接口

### `api/` - API接口
- RESTful API路由
- 请求处理
- 响应格式化

### `web/` - 前端界面
- HTML/CSS/JavaScript
- 聊天界面
- 静态资源

### `scripts/` - 实用工具
- 命令行工具
- 数据管理
- 系统维护
- 演示程序

### `data/` - 数据持久化
- SQLite数据库
- 示例数据
- 用户数据

### `tests/` - 自动化测试
- 单元测试
- 集成测试
- API测试

### `docs/` - 补充文档
- 专题文档
- 详细说明
- 使用指南

---

## 🧹 已清理的内容

### 删除的文件
- ❌ `main.py` - 旧的入口，已被 `start.py` 替代
- ❌ `CHANGELOG_REAL_LLM.md` - 临时日志
- ❌ `QUICK_REFERENCE.md` - 内容已整合
- ❌ `USAGE_GUIDE.md` - 与 `USER_GUIDE.md` 重复

### 删除的目录
- ❌ `lifeos_ai_assistant/` - 旧代码目录
- ❌ `demo/` - 旧演示代码
- ❌ `__pycache__/` - Python缓存

### 保持整洁的规则
已添加 `.gitignore`，自动忽略：
- Python缓存文件
- 虚拟环境
- 日志文件
- 临时文件
- IDE配置

---

## 💡 维护建议

### 添加新功能时
1. 代码放在 `app/` 目录
2. API路由放在 `api/` 目录
3. 工具脚本放在 `scripts/` 目录
4. 更新相应的文档

### 文档更新
- 新功能 → 更新 `HOW_TO_USE.md`
- 新API → 更新 `API_GUIDE.md`
- 技术变更 → 更新 `HOW_IT_WORKS.md`
- 重大变化 → 更新 `README.md`

### 清理习惯
- 定期运行 `python scripts\cleanup_files.py`
- 删除不需要的 `.py[cod]` 文件
- 清理旧的日志文件
- 保持文档同步

---

## 🎉 结果

现在项目结构：
- ✅ 清晰简洁
- ✅ 易于导航
- ✅ 文档齐全
- ✅ 职责分明
- ✅ 便于维护

开始使用：
```powershell
python start.py
```

就这么简单！🚀
