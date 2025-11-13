"""
下一步行动模块 (Next Action Module)
把任务拆解成可执行的小步骤（优先 1-5 分钟）

核心功能：
1. 任务拆解（1分钟 > 5分钟 > 15分钟）
2. 优先级建议
3. 时间估算
4. 日历/提醒建议
5. 执行路径推荐
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class ActionType(Enum):
    """动作类型"""
    IMMEDIATE = "immediate"  # 立即可做
    PREP = "prep"           # 准备性动作
    CALENDAR = "calendar"   # 需要放入日历
    DELEGATE = "delegate"   # 可委托他人
    BATCH = "batch"         # 可批量处理


@dataclass
class CandidateAction:
    """候选动作"""
    desc: str
    est_minutes: int
    type: ActionType
    suggest_add_to_calendar: bool
    suggest_time: Optional[str] = None  # ISO format
    prerequisites: List[str] = None
    expected_outcome: str = ""
    difficulty: int = 1  # 1-5
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if isinstance(self.type, str):
            self.type = ActionType(self.type)


@dataclass
class NextActionResult:
    """下一步行动结果"""
    task: str
    candidate_actions: List[CandidateAction]
    recommended_action_index: int
    rationale: str
    total_est_minutes: int
    completion_strategy: str  # sequential | parallel | flexible
    confidence: float
    created_at: str


# ============================================================================
# System Prompt
# ============================================================================

NEXT_ACTION_SYSTEM_PROMPT = """你是 LifeOS 的任务拆解专家，专门把复杂任务变成可执行的小步骤。

## 你的任务
接收用户的一个任务描述，输出可执行的下一步行动方案（JSON 格式）。

## 输出格式
{
  "task": "原始任务描述",
  "candidate_actions": [
    {
      "desc": "动作描述",
      "est_minutes": 估计时间（分钟）,
      "type": "immediate|prep|calendar|delegate|batch",
      "suggest_add_to_calendar": true/false,
      "suggest_time": "2025-11-14T09:00:00" (可选),
      "prerequisites": ["前置条件"],
      "expected_outcome": "预期结果",
      "difficulty": 1-5
    }
  ],
  "recommended_action_index": 0,
  "rationale": "推荐理由",
  "total_est_minutes": 总预计时间,
  "completion_strategy": "sequential|parallel|flexible",
  "confidence": 0.0-1.0
}

## 核心原则（按优先级）
1. **低阻力优先**：能在 1 分钟内完成的动作最优先
2. **心理启动**：选择"能快速看到成果"的动作作为第一步
3. **递进式**：从简单到复杂，从准备到执行
4. **具体可验证**：每个动作都要有明确的完成标准

## 时间分类标准
- ≤1分钟：发消息、确认信息、打开文件、设置提醒
- ≤5分钟：列要点、快速回复、整理清单、搜索资料
- ≤15分钟：初步研究、准备材料、简短会议
- ≤30分钟：写草稿、深度阅读、小型任务
- >30分钟：深度工作、需要放入日历

## 动作类型说明
- immediate: 现在就能做，无需准备
- prep: 为主任务做准备（如收集材料、设置环境）
- calendar: 需要专门时间块，应该加入日历
- delegate: 可以委托他人完成
- batch: 可以与其他类似任务一起批量完成

## 日历建议规则
- 预计时间 ≥30 分钟 → 建议加入日历
- 需要深度集中 → 建议加入日历，并标注"深度工作"
- 有截止时间 → 建议加入日历，在截止前留足缓冲

## 推荐动作选择逻辑
1. 如果有 ≤1 分钟的动作 → 推荐它（快速启动）
2. 如果没有，但有 ≤5 分钟的准备动作 → 推荐它
3. 如果都是长任务 → 推荐"第一个准备步骤"

输出必须是可解析的 JSON。
"""


# ============================================================================
# Few-Shot Examples
# ============================================================================

FEW_SHOT_EXAMPLES = [
    {
        "user_input": "写一份项目报告，大概需要2小时",
        "assistant_output": {
            "task": "写一份项目报告（2小时）",
            "candidate_actions": [
                {
                    "desc": "列出报告的3-5个核心要点",
                    "est_minutes": 5,
                    "type": "prep",
                    "suggest_add_to_calendar": False,
                    "prerequisites": [],
                    "expected_outcome": "报告框架清晰",
                    "difficulty": 1
                },
                {
                    "desc": "收集相关数据和资料",
                    "est_minutes": 15,
                    "type": "prep",
                    "suggest_add_to_calendar": False,
                    "prerequisites": ["列出要点"],
                    "expected_outcome": "所需数据齐全",
                    "difficulty": 2
                },
                {
                    "desc": "设置90分钟专注时间块开始撰写",
                    "est_minutes": 90,
                    "type": "calendar",
                    "suggest_add_to_calendar": True,
                    "suggest_time": "2025-11-14T09:00:00",
                    "prerequisites": ["列出要点", "收集资料"],
                    "expected_outcome": "完成报告初稿",
                    "difficulty": 4
                }
            ],
            "recommended_action_index": 0,
            "rationale": "先用5分钟列出框架，这是最低阻力的启动方式，能快速进入状态",
            "total_est_minutes": 110,
            "completion_strategy": "sequential",
            "confidence": 0.95
        }
    },
    {
        "user_input": "准备明天的面试",
        "assistant_output": {
            "task": "准备明天的面试",
            "candidate_actions": [
                {
                    "desc": "列出可能被问到的3个核心问题",
                    "est_minutes": 5,
                    "type": "prep",
                    "suggest_add_to_calendar": False,
                    "prerequisites": [],
                    "expected_outcome": "心中有数",
                    "difficulty": 1
                },
                {
                    "desc": "准备1分钟自我介绍并练习3遍",
                    "est_minutes": 10,
                    "type": "immediate",
                    "suggest_add_to_calendar": False,
                    "prerequisites": [],
                    "expected_outcome": "自我介绍流畅",
                    "difficulty": 2
                },
                {
                    "desc": "研究公司背景和岗位要求",
                    "est_minutes": 20,
                    "type": "prep",
                    "suggest_add_to_calendar": False,
                    "prerequisites": [],
                    "expected_outcome": "了解公司和岗位",
                    "difficulty": 2
                },
                {
                    "desc": "准备2-3个提问问题",
                    "est_minutes": 5,
                    "type": "prep",
                    "suggest_add_to_calendar": False,
                    "prerequisites": ["研究公司"],
                    "expected_outcome": "有针对性的提问",
                    "difficulty": 1
                },
                {
                    "desc": "模拟面试完整流程",
                    "est_minutes": 30,
                    "type": "calendar",
                    "suggest_add_to_calendar": True,
                    "suggest_time": "2025-11-13T19:00:00",
                    "prerequisites": ["准备问题", "研究公司"],
                    "expected_outcome": "增强信心",
                    "difficulty": 3
                }
            ],
            "recommended_action_index": 1,
            "rationale": "准备自我介绍是最基础且能快速完成的，可以立即开始练习",
            "total_est_minutes": 70,
            "completion_strategy": "sequential",
            "confidence": 0.92
        }
    },
    {
        "user_input": "整理家里，太乱了",
        "assistant_output": {
            "task": "整理家里",
            "candidate_actions": [
                {
                    "desc": "设置15分钟计时器，整理一个小区域（如书桌）",
                    "est_minutes": 15,
                    "type": "immediate",
                    "suggest_add_to_calendar": False,
                    "prerequisites": [],
                    "expected_outcome": "一个区域变整洁",
                    "difficulty": 1
                },
                {
                    "desc": "扔掉明显的垃圾和不要的东西",
                    "est_minutes": 10,
                    "type": "immediate",
                    "suggest_add_to_calendar": False,
                    "prerequisites": [],
                    "expected_outcome": "减少杂物",
                    "difficulty": 1
                },
                {
                    "desc": "将物品分类（保留/捐赠/丢弃）",
                    "est_minutes": 30,
                    "type": "calendar",
                    "suggest_add_to_calendar": True,
                    "prerequisites": [],
                    "expected_outcome": "物品分类清楚",
                    "difficulty": 3
                }
            ],
            "recommended_action_index": 1,
            "rationale": "扔垃圾是最简单的启动方式，能立即看到效果，增强动力",
            "total_est_minutes": 55,
            "completion_strategy": "flexible",
            "confidence": 0.88
        }
    }
]


# ============================================================================
# 解析器
# ============================================================================

class NextActionParser:
    """下一步行动解析器"""
    
    @staticmethod
    def parse_llm_response(response_text: str) -> Optional[NextActionResult]:
        """解析 LLM 返回的 JSON"""
        try:
            json_text = response_text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            data = json.loads(json_text)
            
            # 构建候选动作列表
            candidate_actions = []
            for action_data in data.get("candidate_actions", []):
                action = CandidateAction(
                    desc=action_data.get("desc", ""),
                    est_minutes=action_data.get("est_minutes", 5),
                    type=ActionType(action_data.get("type", "immediate")),
                    suggest_add_to_calendar=action_data.get("suggest_add_to_calendar", False),
                    suggest_time=action_data.get("suggest_time"),
                    prerequisites=action_data.get("prerequisites", []),
                    expected_outcome=action_data.get("expected_outcome", ""),
                    difficulty=action_data.get("difficulty", 1)
                )
                candidate_actions.append(action)
            
            return NextActionResult(
                task=data.get("task", ""),
                candidate_actions=candidate_actions,
                recommended_action_index=data.get("recommended_action_index", 0),
                rationale=data.get("rationale", ""),
                total_est_minutes=data.get("total_est_minutes", 0),
                completion_strategy=data.get("completion_strategy", "sequential"),
                confidence=data.get("confidence", 0.8),
                created_at=datetime.now().isoformat()
            )
            
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"解析错误: {e}")
            return None
    
    @staticmethod
    def to_json(result: NextActionResult) -> str:
        """转换为 JSON"""
        def convert(obj):
            if isinstance(obj, ActionType):
                return obj.value
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, '__dict__'):
                return {k: convert(v) for k, v in obj.__dict__.items()}
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            return obj
        
        data = convert(result)
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def format_for_display(result: NextActionResult) -> str:
        """格式化显示"""
        lines = [
            f"📝 任务: {result.task}",
            f"⏱️ 总预计时间: {result.total_est_minutes} 分钟",
            f"📋 完成策略: {result.completion_strategy}",
            "",
            "🎯 候选动作:"
        ]
        
        for i, action in enumerate(result.candidate_actions):
            marker = "⭐" if i == result.recommended_action_index else "  "
            lines.append(f"{marker} [{i+1}] {action.desc}")
            lines.append(f"      ⏱️ {action.est_minutes}分钟 | 类型: {action.type.value} | 难度: {'⭐'*action.difficulty}")
            if action.expected_outcome:
                lines.append(f"      ✅ 预期: {action.expected_outcome}")
            if action.prerequisites:
                lines.append(f"      📌 前置: {', '.join(action.prerequisites)}")
            if action.suggest_add_to_calendar:
                time_str = action.suggest_time or "待定"
                lines.append(f"      📅 建议加入日历: {time_str}")
            lines.append("")
        
        lines.append(f"💡 推荐: 第 {result.recommended_action_index + 1} 项")
        lines.append(f"   理由: {result.rationale}")
        
        return "\n".join(lines)


# ============================================================================
# 用户偏好感知（用于个性化推荐）
# ============================================================================

@dataclass
class UserPreferences:
    """用户偏好"""
    morning_productivity: bool = True  # 早上效率高
    prefers_short_tasks: bool = True   # 偏好短任务
    needs_calendar_structure: bool = False  # 需要日历结构
    timezone: str = "Asia/Shanghai"
    work_hours_start: int = 9  # 工作开始时间
    work_hours_end: int = 18   # 工作结束时间


def adjust_suggestions_by_preferences(
    result: NextActionResult, 
    prefs: UserPreferences
) -> NextActionResult:
    """根据用户偏好调整建议"""
    
    # 如果用户偏好短任务，调整推荐
    if prefs.prefers_short_tasks:
        # 找最短的动作
        shortest_idx = min(
            range(len(result.candidate_actions)),
            key=lambda i: result.candidate_actions[i].est_minutes
        )
        if result.candidate_actions[shortest_idx].est_minutes <= 5:
            result.recommended_action_index = shortest_idx
            result.rationale = f"根据你的偏好，推荐最短的任务作为启动（{result.candidate_actions[shortest_idx].est_minutes}分钟）"
    
    # 调整建议时间
    if prefs.morning_productivity:
        for action in result.candidate_actions:
            if action.suggest_add_to_calendar and action.suggest_time:
                # 建议放在早上
                dt = datetime.fromisoformat(action.suggest_time.replace('Z', '+00:00'))
                if dt.hour >= 12:
                    dt = dt.replace(hour=prefs.work_hours_start)
                    action.suggest_time = dt.isoformat()
    
    return result


# ============================================================================
# 辅助函数
# ============================================================================

def build_next_action_prompt(task: str, include_examples: bool = True) -> List[Dict[str, str]]:
    """构建完整 prompt"""
    messages = [
        {"role": "system", "content": NEXT_ACTION_SYSTEM_PROMPT}
    ]
    
    if include_examples:
        for example in FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user_input"]})
            messages.append({
                "role": "assistant",
                "content": json.dumps(example["assistant_output"], ensure_ascii=False, indent=2)
            })
    
    messages.append({"role": "user", "content": f"任务：{task}"})
    
    return messages


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    test_task = "学习 Python 数据分析"
    
    # 模拟 LLM 响应
    mock_response = """{
  "task": "学习 Python 数据分析",
  "candidate_actions": [
    {
      "desc": "安装 pandas 和 numpy",
      "est_minutes": 3,
      "type": "immediate",
      "suggest_add_to_calendar": false,
      "prerequisites": [],
      "expected_outcome": "环境准备完成",
      "difficulty": 1
    },
    {
      "desc": "找一个10分钟的入门教程视频",
      "est_minutes": 5,
      "type": "prep",
      "suggest_add_to_calendar": false,
      "prerequisites": [],
      "expected_outcome": "知道从哪里开始",
      "difficulty": 1
    },
    {
      "desc": "跟着教程完成第一个数据分析示例",
      "est_minutes": 30,
      "type": "calendar",
      "suggest_add_to_calendar": true,
      "suggest_time": "2025-11-14T09:00:00",
      "prerequisites": ["安装工具", "找教程"],
      "expected_outcome": "完成第一个实践",
      "difficulty": 3
    }
  ],
  "recommended_action_index": 0,
  "rationale": "先安装工具，3分钟就能完成，立即有成就感",
  "total_est_minutes": 38,
  "completion_strategy": "sequential",
  "confidence": 0.9
}"""
    
    parser = NextActionParser()
    result = parser.parse_llm_response(mock_response)
    
    if result:
        print("✅ 解析成功！\n")
        print(parser.format_for_display(result))
        print("\n" + "="*60)
        
        # 测试用户偏好调整
        prefs = UserPreferences(
            morning_productivity=True,
            prefers_short_tasks=True
        )
        adjusted = adjust_suggestions_by_preferences(result, prefs)
        print("\n🎨 根据用户偏好调整后:")
        print(f"推荐动作: 第 {adjusted.recommended_action_index + 1} 项")
        print(f"理由: {adjusted.rationale}")
    else:
        print("❌ 解析失败")
