# LifeOS AI Assistant

LifeOS is positioned as a lightweight "second brain" rather than another to-do
list, diary or generic chatbot.  This repository contains an offline friendly
prototype that mirrors the competition vision: the assistant learns from daily
inputs, spots behaviour patterns and responds with warm, coach-style prompts.

## ✨ Core capabilities

| 功能 | 描述 |
| --- | --- |
| AI 习惯教练 | 识别成功触发因素与阻力，给出灵活调整建议，强调“找到成功条件”而非自我苛责。 |
| 决策助手 | 通过苏格拉底式提问帮你厘清真实需求，并结合历史记录给出带有退出条件的策略。 |
| 今日策略简报 | 不是简单的待办清单，而是能量预测、重点建议、风险提醒与鼓励语组成的“作战手册”。 |
| 深度反思对话 | 以陪伴式语气追问情绪与身体信号，指出反复出现的模式，给出可立即执行的微行动。 |
| 目标拆解器 | 将模糊愿望分解成周度里程碑、日常行动以及首个 1 分钟启动步骤。 |

所有推理都在本地完成，不依赖外部 API 或模型调用，方便在 Demo 或评审现场快速演示。

## 🧱 模块概览

- `lifeos_ai_assistant/assistant.py`：核心推理引擎，包含习惯洞察、决策辅导、每日简报、反思对话与目标拆解等逻辑。
- `main.py`：命令行入口，支持加载样本记忆数据，快速体验不同场景。
- `tests/`：单元测试覆盖关键分支，确保提示语和计算逻辑稳定可靠。

## 🚀 快速体验

准备一份历史数据（可选）：

```json
{
  "habits": [
    {
      "name": "晨跑",
      "history": [
        {"date": "2025-11-10", "completed": true, "note": "天气好 下午无会"},
        {"date": "2025-11-11", "completed": false, "note": "加班 累"}
      ]
    }
  ],
  "reflections": [
    {"date": "2025-11-09", "mood": 6, "energy": 68, "content": "下午开会太多"},
    {"date": "2025-11-10", "mood": 7, "energy": 74, "content": "晨跑后效率高"}
  ],
  "insights": {
    "productiveDays": ["周二", "周四"],
    "stressTriggers": ["会议多", "deadline"]
  }
}
```

保存为 `memory.json` 后即可运行：

```bash
python main.py --name 小明 --focus 成长 健康 --memory memory.json habit --habit 晨跑
python main.py --name 小明 --focus 成长 健康 --memory memory.json decision --question "周末要不要参加聚会" --options 去 休息
python main.py --name 小明 --focus 成长 健康 --memory memory.json brief
python main.py --name 小明 --focus 成长 健康 --memory memory.json reflect --message "今天开了三个会，好累"
python main.py --name 小明 --focus 成长 健康 goal --goal "提升英语口语" --minutes 30 --weeks 6 --focus-area 学习
```

所有命令都会输出结构化 JSON，方便接入前端或移动端原型。

## 🧪 运行测试

```bash
pytest
```

## 🏗️ 下一步构想

1. **记忆可视化**：基于本地数据生成趋势图与决策树，强化“第二大脑”的沉浸感。
2. **多语言调优**：针对中文与英文混合输入进一步优化分词与情感识别。
3. **前端 Demo**：配合命令行输出构建渐进式 Web UI，展示 LifeOS 的对话式交互范式。

欢迎在比赛现场自由扩展 Prompt 或 UI，保持“温暖、智能、主动洞察”的核心理念即可。
