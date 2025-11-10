# LifeOS AI Assistant

LifeOS 是一个轻量级的 AI 原生个人助理原型，专注于帮助用户在日常生活、学习成长和时间管理上保持节奏。项目完全离线运行，不依赖外部数据源，适合作为竞赛 Demo 或快速验证的本地工具。

## 功能亮点

- **智能日程规划**：根据任务优先级与能量节奏，生成带有恢复性休息时间的日程安排，并输出可执行的洞察提醒。
- **习惯养成教练**：围绕触发-行动-奖励模型生成习惯设计方案，强调极简起步与责任机制。
- **个性化学习路径**：根据每日可投入时间推荐学习周程、关键里程碑和实践点子，便于持续迭代。
- **情绪日记分析**：对日记文本做轻量级情绪词频统计，给出主导情绪、能量评分与鼓励建议。
- **每日反思提示**：结合用户关注领域，输出简短提醒，帮助保持长期目标感。

## 快速上手

### 安装依赖

项目使用纯标准库，无需额外安装依赖。建议使用 Python 3.11 及以上版本运行。

### 命令行体验

1. 准备任务文件 `tasks.json`：

   ```json
   [
     {"title": "Deep work", "duration": 120, "priority": 1, "energy": "high"},
     {"title": "Team sync", "duration": 45, "priority": 2, "energy": "medium"},
     {"title": "Workout", "duration": 60, "priority": 2, "energy": "high"}
   ]
   ```

2. 生成日程：

   ```bash
   python main.py plan --name "小宇" --tasks tasks.json --focus 健康 成长
   ```

3. 获取每日反思：

   ```bash
   python main.py reflect --name "小宇" --focus 健康 成长
   ```

### 以代码方式集成

```python
from lifeos_ai_assistant import LifeOSAssistant, Task, UserProfile

profile = UserProfile(
    name="小宇",
    focus_areas=("健康", "成长"),
    wake_time="07:00",
    sleep_time="22:30",
)
assistant = LifeOSAssistant(profile)

schedule, insights = assistant.plan_day([
    Task(title="深度工作", duration_minutes=90, priority=1, energy="high"),
    Task(title="阅读", duration_minutes=40, priority=2, energy="medium"),
])

habit = assistant.design_habit("每日晨练", trigger="起床喝水", rewards=["周末咖啡奖励"])
learning = assistant.recommend_learning_path("数据分析", available_minutes_per_day=45)
mood = assistant.analyse_mood([
    "今天感觉很专注，也为完成任务感到开心。",
    "下午有些疲惫，但对新的课程保持期待。",
])
```

## 测试

运行单元测试：

```bash
pytest
```

## 许可证

MIT License
