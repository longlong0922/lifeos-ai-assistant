# LifeOS - AI 原生个人成长助理

<div align="center">

![LifeOS](https://img.shields.io/badge/LifeOS-AI%20助理-blue)
![React](https://img.shields.io/badge/React-19-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178c6)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-38bdf8)

一个轻量级 AI 原生个人助理，它不是任务清单或提醒器，而是理解你的生活教练与成长伙伴。

[English](#english) | [中文](#中文)

</div>

---

## 中文

### ✨ 功能特性

- 🤖 **AI 对话助理** - 基于 Claude API 的智能对话，陪伴你的成长之旅
- ✅ **习惯追踪** - 创建和管理每日/每周习惯，追踪完成率
- 📔 **每日反思** - 记录想法、心情和成长，支持与习惯关联
- 💾 **本地存储** - 所有数据保存在浏览器 localStorage，完全私密
- 🎨 **精美动画** - 使用 Framer Motion 打造流畅的用户体验
- 📱 **响应式设计** - 支持桌面和移动端，随时随地使用

### 🚀 快速开始

#### 环境要求

- Node.js 16.x 或更高版本
- npm 或 yarn 包管理器

#### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/longlong0922/lifeos-ai-assistant.git
cd lifeos-ai-assistant
```

2. **安装依赖**

```bash
npm install
```

3. **启动开发服务器**

```bash
npm run dev
```

4. **访问应用**

打开浏览器访问 `http://localhost:5173`

### 📦 项目结构

```
lifeos-ai-assistant/
├── src/
│   ├── components/          # React 组件
│   │   ├── Chat.tsx        # 对话界面组件
│   │   ├── Habits.tsx      # 习惯追踪组件
│   │   └── Reflections.tsx # 反思记录组件
│   ├── services/           # 服务层
│   │   ├── storage.ts      # localStorage 服务
│   │   └── claude.ts       # Claude API 模拟服务
│   ├── hooks/              # 自定义 React Hooks
│   │   └── useLifeOS.ts    # 主应用状态管理
│   ├── types/              # TypeScript 类型定义
│   │   └── index.ts
│   ├── utils/              # 工具函数
│   │   └── helpers.ts
│   ├── App.tsx             # 主应用组件
│   ├── main.tsx            # 应用入口
│   └── index.css           # 全局样式
├── public/                 # 静态资源
├── index.html             # HTML 模板
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript 配置
├── tailwind.config.js     # TailwindCSS 配置
└── vite.config.ts         # Vite 配置
```

### 🎯 使用指南

#### 对话功能

1. 点击"对话"标签
2. 在输入框中输入你的想法或问题
3. AI 助理会给出相应的回复和建议

#### 习惯追踪

1. 点击"习惯"标签
2. 点击"添加新习惯"按钮
3. 填写习惯名称、描述和频率
4. 每天点击圆圈图标标记习惯完成

#### 每日反思

1. 点击"反思"标签
2. 点击"写下今天的想法"按钮
3. 记录你的想法和心情
4. 可选择关联相关习惯

### 🛠️ 技术栈

- **前端框架**: React 19 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS
- **动画**: Framer Motion
- **状态管理**: React Hooks
- **数据存储**: localStorage

### 📝 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

### 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

### 🙏 致谢

- React 团队提供的优秀框架
- TailwindCSS 提供的实用 CSS 框架
- Framer Motion 提供的动画库
- Claude AI 的启发

---

## English

### ✨ Features

- 🤖 **AI Chat Assistant** - Intelligent conversation based on Claude API to accompany your growth journey
- ✅ **Habit Tracking** - Create and manage daily/weekly habits, track completion rates
- 📔 **Daily Reflections** - Record thoughts, moods, and growth, with habit association support
- 💾 **Local Storage** - All data saved in browser localStorage, completely private
- 🎨 **Beautiful Animations** - Smooth user experience with Framer Motion
- 📱 **Responsive Design** - Support for desktop and mobile, use anytime, anywhere

### 🚀 Quick Start

#### Requirements

- Node.js 16.x or higher
- npm or yarn package manager

#### Installation

1. **Clone the repository**

```bash
git clone https://github.com/longlong0922/lifeos-ai-assistant.git
cd lifeos-ai-assistant
```

2. **Install dependencies**

```bash
npm install
```

3. **Start development server**

```bash
npm run dev
```

4. **Access the application**

Open your browser and visit `http://localhost:5173`

### 📦 Project Structure

```
lifeos-ai-assistant/
├── src/
│   ├── components/          # React components
│   │   ├── Chat.tsx        # Chat interface component
│   │   ├── Habits.tsx      # Habit tracking component
│   │   └── Reflections.tsx # Reflection recording component
│   ├── services/           # Services layer
│   │   ├── storage.ts      # localStorage service
│   │   └── claude.ts       # Claude API mock service
│   ├── hooks/              # Custom React Hooks
│   │   └── useLifeOS.ts    # Main app state management
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/              # Utility functions
│   │   └── helpers.ts
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Application entry
│   └── index.css           # Global styles
├── public/                 # Static assets
├── index.html             # HTML template
├── package.json           # Project configuration
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # TailwindCSS configuration
└── vite.config.ts         # Vite configuration
```

### 🎯 User Guide

#### Chat Feature

1. Click the "Chat" tab
2. Enter your thoughts or questions in the input box
3. The AI assistant will provide responses and suggestions

#### Habit Tracking

1. Click the "Habits" tab
2. Click the "Add New Habit" button
3. Fill in the habit name, description, and frequency
4. Click the circle icon daily to mark habit completion

#### Daily Reflections

1. Click the "Reflections" tab
2. Click the "Write Today's Thoughts" button
3. Record your thoughts and mood
4. Optionally associate related habits

### 🛠️ Tech Stack

- **Frontend Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Animations**: Framer Motion
- **State Management**: React Hooks
- **Data Storage**: localStorage

### 📝 Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### 🙏 Acknowledgments

- React team for the excellent framework
- TailwindCSS for the utility-first CSS framework
- Framer Motion for the animation library
- Claude AI for the inspiration
