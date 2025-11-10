"""LifeOS assistant core logic tailored to the product vision.

The module implements a lightweight reasoning engine that mirrors the
competition brief: LifeOS is not a simple to-do list or diary.  It behaves like a
second brain that understands context, spots behaviour patterns and coaches the
user with Socratic style prompts.  The implementation is fully local and
dependency free so it can be embedded in offline demos.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterable, Sequence
import re

__all__ = [
    "HabitEntry",
    "ReflectionEntry",
    "DecisionRecord",
    "LifeOSMemory",
    "UserProfile",
    "HabitInsight",
    "DecisionGuide",
    "DailyBrief",
    "ReflectionResponse",
    "GoalPlan",
    "LifeOSAssistant",
]


STOP_WORDS = {
    "the",
    "and",
    "to",
    "a",
    "of",
    "for",
    "that",
    "is",
    "was",
    "你",
    "我",
    "了",
    "很",
    "又",
    "有",
    "在",
    "今天",
    "昨天",
    "就是",
}

TOKEN_PATTERN = re.compile(r"[A-Za-z]+|[0-9]+|[\u4e00-\u9fff]+")

TIME_KEYWORDS = {
    "清晨": {"morning", "早上", "清晨", "am", "早"},
    "上午": {"上午", "before lunch", "9点", "10点"},
    "午间": {"中午", "noon", "午饭", "午间"},
    "下午": {"下午", "after lunch", "pm", "15点", "下午4-6点"},
    "傍晚": {"傍晚", "evening", "晚饭前", "黄昏"},
    "夜间": {"晚上", "night", "睡前", "深夜"},
}

STRESS_KEYWORDS = {
    "加班",
    "rain",
    "下雨",
    "meeting",
    "traffic",
    "deadline",
    "deadline",
    "熬夜",
    "生病",
    "疲惫",
    "累",
    "tired",
    "stress",
    "压力",
}

EMOTION_KEYWORDS = {
    "疲惫": {"累", "疲", "drained", "tired", "exhausted"},
    "焦虑": {"焦虑", "worried", "担心", "anxious"},
    "挫败": {"挫败", "frustrated", "无力", "stuck"},
    "兴奋": {"兴奋", "excited", "期待", "energised"},
    "满足": {"满足", "proud", "开心", "happy", "满足"},
}

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def _tokenise(text: str) -> list[str]:
    tokens: list[str] = []
    for token in TOKEN_PATTERN.findall(text.lower()):
        if token and token not in STOP_WORDS:
            tokens.append(token)
    return tokens


@dataclass(slots=True)
class HabitEntry:
    """Snapshot of a habit attempt."""

    date: date
    completed: bool
    note: str = ""

    @classmethod
    def from_dict(cls, raw: dict) -> "HabitEntry":
        return cls(
            date=_parse_date(raw.get("date", date.today())),
            completed=bool(raw.get("completed", False)),
            note=str(raw.get("note", "")),
        )


@dataclass(slots=True)
class ReflectionEntry:
    date: date
    mood: int | None = None
    energy: int | None = None
    content: str = ""

    @classmethod
    def from_dict(cls, raw: dict) -> "ReflectionEntry":
        mood = raw.get("mood")
        energy = raw.get("energy") or raw.get("energyScore")
        return cls(
            date=_parse_date(raw.get("date", date.today())),
            mood=int(mood) if mood is not None else None,
            energy=int(energy) if energy is not None else None,
            content=str(raw.get("content", raw.get("aiInsight", ""))),
        )


@dataclass(slots=True)
class DecisionRecord:
    date: date
    question: str
    result: str = ""
    mood_after: int | None = None

    @classmethod
    def from_dict(cls, raw: dict) -> "DecisionRecord":
        return cls(
            date=_parse_date(raw.get("date", date.today())),
            question=str(raw.get("question", "")),
            result=str(raw.get("result", "")),
            mood_after=(int(raw["moodAfter"]) if "moodAfter" in raw else None),
        )


@dataclass(slots=True)
class LifeOSMemory:
    habits: dict[str, list[HabitEntry]] = field(default_factory=dict)
    reflections: list[ReflectionEntry] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    insights: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict) -> "LifeOSMemory":
        memory = cls()
        for habit in raw.get("habits", []):
            name = habit.get("name") or habit.get("id") or "habit"
            history = [HabitEntry.from_dict(entry) for entry in habit.get("history", [])]
            memory.habits[name] = history
        memory.reflections = [
            ReflectionEntry.from_dict(item) for item in raw.get("reflections", [])
        ]
        memory.decisions = [
            DecisionRecord.from_dict(item) for item in raw.get("decisions", [])
        ]
        memory.insights = dict(raw.get("insights", {}))
        return memory


@dataclass(slots=True)
class UserProfile:
    name: str
    timezone: str = "Asia/Shanghai"
    focus_areas: Sequence[str] = field(default_factory=tuple)
    energy_pattern: str = "上午高，下午轻微下滑"


@dataclass(slots=True)
class HabitInsight:
    name: str
    success_rate: float
    best_windows: list[str]
    stressors: list[str]
    momentum_message: str
    suggestions: list[str]
    reflection_prompt: str

    def as_dict(self) -> dict[str, object]:
        return {
            "habit": self.name,
            "successRate": round(self.success_rate, 2),
            "bestWindows": self.best_windows,
            "stressors": self.stressors,
            "momentum": self.momentum_message,
            "suggestions": self.suggestions,
            "reflectionPrompt": self.reflection_prompt,
        }


@dataclass(slots=True)
class DecisionGuide:
    clarifying_questions: list[str]
    pattern_summary: str
    recommendation: str
    rationale: list[str]
    decision_path: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "clarifyingQuestions": self.clarifying_questions,
            "patternSummary": self.pattern_summary,
            "recommendation": self.recommendation,
            "rationale": self.rationale,
            "decisionPath": self.decision_path,
        }


@dataclass(slots=True)
class DailyBrief:
    date: date
    energy_prediction: int
    priorities: list[dict[str, str]]
    risks: list[str]
    encouragement: str
    narrative: str

    def as_dict(self) -> dict[str, object]:
        return {
            "date": self.date.isoformat(),
            "energyPrediction": self.energy_prediction,
            "priorities": self.priorities,
            "risks": self.risks,
            "encouragement": self.encouragement,
            "narrative": self.narrative,
        }


@dataclass(slots=True)
class ReflectionResponse:
    opening: str
    follow_up_questions: list[str]
    detected_emotions: list[str]
    recurring_pattern: str | None
    micro_actions: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "opening": self.opening,
            "followUp": self.follow_up_questions,
            "emotions": self.detected_emotions,
            "pattern": self.recurring_pattern,
            "microActions": self.micro_actions,
        }


@dataclass(slots=True)
class GoalPlan:
    goal: str
    vision: str
    milestones: list[str]
    weekly_focus: list[str]
    daily_actions: list[str]
    first_step: str
    tracking_metrics: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "goal": self.goal,
            "vision": self.vision,
            "milestones": self.milestones,
            "weeklyFocus": self.weekly_focus,
            "dailyActions": self.daily_actions,
            "firstStep": self.first_step,
            "trackingMetrics": self.tracking_metrics,
        }


class LifeOSAssistant:
    """Rule-based engine that approximates LifeOS coaching behaviours."""

    def __init__(self, profile: UserProfile, memory: LifeOSMemory | None = None) -> None:
        self.profile = profile
        self.memory = memory or LifeOSMemory()

    # ------------------------------------------------------------------
    # Habit analysis
    def habit_coaching(self, habit_name: str, history: Sequence[HabitEntry] | None = None) -> HabitInsight:
        history = list(history if history is not None else self.memory.habits.get(habit_name, []))
        if not history:
            return HabitInsight(
                name=habit_name,
                success_rate=0.0,
                best_windows=[],
                stressors=[],
                momentum_message="我们还没有足够的数据，一起从今天的小行动开始。",
                suggestions=["为这个习惯找到一个稳定的触发事件，例如早餐后立即进行。"],
                reflection_prompt="完成后告诉我：是什么让你做到了？",
            )

        total_attempts = len(history)
        successes = [entry for entry in history if entry.completed]
        failures = [entry for entry in history if not entry.completed]
        success_rate = len(successes) / total_attempts

        # Window detection
        window_counts: Counter[str] = Counter()
        for entry in successes:
            tokens = _tokenise(entry.note)
            for window, keywords in TIME_KEYWORDS.items():
                if any(token in keywords for token in tokens):
                    window_counts[window] += 1
        best_windows = [window for window, _ in window_counts.most_common(3)]

        # Day of week stats
        day_stats = defaultdict(lambda: {"total": 0, "success": 0})
        for entry in history:
            weekday = WEEKDAY_NAMES[entry.date.weekday()]
            day_stats[weekday]["total"] += 1
            if entry.completed:
                day_stats[weekday]["success"] += 1
        underperforming_days = [
            day
            for day, stats in day_stats.items()
            if stats["total"] >= 2 and stats["success"] / stats["total"] < 0.4
        ]

        # Stressors detection
        stress_counts: Counter[str] = Counter()
        for entry in failures:
            tokens = _tokenise(entry.note)
            for token in tokens:
                for stress in STRESS_KEYWORDS:
                    if stress in token:
                        stress_counts[stress] += 1
        stressors = [token for token, _ in stress_counts.most_common(3)]

        if success_rate >= 0.75:
            momentum = "保持势头！这个习惯已经成为你的优势，我们可以加上一点升级版挑战。"
        elif success_rate >= 0.5:
            momentum = "你已经找到节奏，接下来我们来优化容易被打断的时段。"
        else:
            momentum = "我们先降低门槛，专注于创造成功条件，而不是追求完美。"

        suggestions: list[str] = []
        if best_windows:
            window_text = "、".join(best_windows)
            suggestions.append(f"尽量把关键练习安排在{window_text}，这是你最容易坚持的时段。")
        if stressors:
            stress_text = "、".join(stressors)
            suggestions.append(f"当{stress_text}出现时，可以准备一个轻量版本，例如只做5分钟。")
        if underperforming_days:
            day_text = "、".join(underperforming_days)
            suggestions.append(f"{day_text}的成功率偏低，考虑把目标改成更轻松的替代动作。")
        if not suggestions:
            suggestions.append("继续记录成功与阻力，我们每周复盘一次并调整策略。")

        reflection_prompt = "今天做到了吗？成功/未完成分别是什么触发和阻碍？"
        return HabitInsight(
            name=habit_name,
            success_rate=success_rate,
            best_windows=best_windows,
            stressors=stressors,
            momentum_message=momentum,
            suggestions=suggestions,
            reflection_prompt=reflection_prompt,
        )

    # ------------------------------------------------------------------
    # Decision support
    def decision_support(self, question: str, options: Sequence[str]) -> DecisionGuide:
        reflections = self.memory.reflections[-6:]
        moods = [entry.mood for entry in reflections if entry.mood is not None]
        average_mood = sum(moods) / len(moods) if moods else None
        average_energy = [entry.energy for entry in reflections if entry.energy is not None]
        energy_score = sum(average_energy) / len(average_energy) if average_energy else None

        keywords_counter: Counter[str] = Counter()
        for entry in reflections:
            keywords_counter.update(_tokenise(entry.content))
        dominant_keywords = [kw for kw, _ in keywords_counter.most_common(5)]

        clarifying_questions = [
            "上次遇到类似选择时，你的状态如何？现在有什么不同？",
            "哪一个选项更贴近你今年的核心主题？",
        ]
        if average_mood is not None and average_mood <= 5:
            clarifying_questions.append("在情绪低落的日子里，你通常更需要补充能量还是寻找连接？")
        else:
            clarifying_questions.append("如果精力充足，你会如何定义这次行动的成功？")

        pattern_parts = []
        if average_mood is not None:
            pattern_parts.append(f"最近的情绪均值在{average_mood:.1f}分")
        if energy_score is not None:
            pattern_parts.append(f"体感能量大约{energy_score:.0f}/100")
        if dominant_keywords:
            joined = "、".join(dominant_keywords[:3])
            pattern_parts.append(f"反复提到：{joined}")
        pattern_summary = "；".join(pattern_parts) if pattern_parts else "暂时缺少历史数据。"

        rationale = []
        if average_mood is not None and average_mood < 5:
            rationale.append("在低情绪时期，社交类活动后你往往更疲惫。")
        if "进展" in dominant_keywords or "progress" in dominant_keywords:
            rationale.append("当你看到实质进展时，满意度提升最快。")
        if not rationale:
            rationale.append("依据过往记录，保持节奏比一次性的高强度更有效。")

        chosen_option = options[0] if options else ""
        if options:
            if average_mood is not None and average_mood < 5 and len(options) > 1:
                chosen_option = options[1]
            elif "rest" in options or "休息" in options:
                chosen_option = "休息"

        decision_path = [
            "1. 先确认本周的能量预算，避免超负荷。",
            "2. 根据最重要的价值排序备选方案。",
            "3. 提前设定退出或复盘的时间点。",
        ]

        recommendation = (
            f"倾向选择『{chosen_option}』，并设定一个缓冲点：如果能量下降到40%，"
            "就允许自己提前结束。"
            if chosen_option
            else "本周先观察能量，再决定。"
        )

        return DecisionGuide(
            clarifying_questions=clarifying_questions,
            pattern_summary=pattern_summary,
            recommendation=recommendation,
            rationale=rationale,
            decision_path=decision_path,
        )

    # ------------------------------------------------------------------
    # Daily brief
    def daily_brief(self, target_date: date | None = None) -> DailyBrief:
        target_date = target_date or date.today()
        reflections = self.memory.reflections[-10:]
        mood_values = [entry.mood for entry in reflections if entry.mood is not None]
        energy_values = [entry.energy for entry in reflections if entry.energy is not None]

        base_energy = 72
        if energy_values:
            base_energy = max(50, min(90, sum(energy_values) // len(energy_values)))
        elif mood_values:
            base_energy = int(55 + sum(mood_values) / len(mood_values) * 4)

        weekday = WEEKDAY_NAMES[target_date.weekday()]
        productive_days = self.memory.insights.get("productiveDays")
        if isinstance(productive_days, (list, tuple)) and weekday in productive_days:
            base_energy = min(95, base_energy + 6)

        priorities: list[dict[str, str]] = []
        for habit_name, history in self.memory.habits.items():
            insight = self.habit_coaching(habit_name, history)
            if insight.success_rate < 0.6:
                preferred_window = insight.best_windows[0] if insight.best_windows else "你最放松的时段"
                priorities.append(
                    {
                        "task": f"维持『{habit_name}』的轻量版本",
                        "reason": "成功率暂时不稳，我们专注于创造成功条件",
                        "bestTime": preferred_window,
                    }
                )
        if not priorities and self.profile.focus_areas:
            focus = self.profile.focus_areas[0]
            priorities.append(
                {
                    "task": f"推进{focus}领域的关键一步",
                    "reason": "保持长期复利，让这周有明确进展",
                    "bestTime": "上午高能时段",
                }
            )

        risks: list[str] = []
        stress_triggers = self.memory.insights.get("stressTriggers")
        if isinstance(stress_triggers, (list, tuple)) and stress_triggers:
            risk_text = "、".join(stress_triggers[:3])
            risks.append(f"留意 {risk_text} 可能带来的能量消耗。")
        if base_energy < 60:
            risks.append("能量偏低，安排30分钟恢复窗口，避免连续会议。")

        encouragement = (
            f"今天的能量估值约{base_energy}分，记得用在真正重要的事情上。"
        )
        narrative = (
            f"{self.profile.name}，这是{weekday}。" \
            f" 最近你反复提到想提升{self.profile.focus_areas[0] if self.profile.focus_areas else '核心项目'}，" \
            "今天的策略是：选定一段高质量时间，完成一个可量化的小进展。"
        )

        return DailyBrief(
            date=target_date,
            energy_prediction=base_energy,
            priorities=priorities,
            risks=risks,
            encouragement=encouragement,
            narrative=narrative,
        )

    # ------------------------------------------------------------------
    # Reflection dialogue
    def reflection_dialogue(self, message: str) -> ReflectionResponse:
        tokens = _tokenise(message)
        detected: list[str] = []
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(
                keyword in token or token in keywords
                for token in tokens
                for keyword in keywords
            ):
                detected.append(emotion)

        opening = "听起来你今天经历了不少，想先描述一下最让你印象深刻的瞬间吗？"
        follow_up = [
            "当时你身体的反应是什么？比如心率、呼吸或者肩膀的紧张度。",
            "这个瞬间和你最近提到的主题之间有什么联系？",
        ]
        if "疲惫" in detected:
            follow_up.append("如果把今天的能量比作电量百分比，现在剩多少？")
        if "挫败" in detected:
            follow_up.append("当你感到无力时，有没有某个可以掌控的1分？")

        # Look for repeating keywords in history
        history_tokens = Counter()
        for entry in self.memory.reflections[-10:]:
            history_tokens.update(_tokenise(entry.content))
        recurring_pattern = None
        for keyword, _ in history_tokens.most_common():
            if keyword in tokens and keyword not in STOP_WORDS:
                recurring_pattern = f"你最近多次提到『{keyword}』，它对能量的影响值得再探一下。"
                break
        if recurring_pattern is None and history_tokens:
            keyword, count = history_tokens.most_common(1)[0]
            if count >= 2 and keyword not in STOP_WORDS:
                recurring_pattern = f"过去几次记录里反复提到『{keyword}』，或许它与当前体验有关。"

        micro_actions = [
            "写下三个让你感到掌控的小动作，挑一个今晚尝试。",
            "给未来的自己留一句鼓励，明天早上打开手机就能看到。",
        ]
        if "焦虑" in detected:
            micro_actions.append("尝试4-7-8呼吸两轮，重置神经系统。")

        return ReflectionResponse(
            opening=opening,
            follow_up_questions=follow_up,
            detected_emotions=detected,
            recurring_pattern=recurring_pattern,
            micro_actions=micro_actions,
        )

    # ------------------------------------------------------------------
    # Goal decomposition
    def goal_breakdown(
        self,
        goal: str,
        daily_minutes: int,
        weeks: int | None = None,
        focus_area: str | None = None,
    ) -> GoalPlan:
        weeks = weeks or 6
        focus_area = focus_area or (self.profile.focus_areas[0] if self.profile.focus_areas else "核心主题")

        vision = f"通过{weeks}周的结构化练习，让『{goal}』成为你在{focus_area}里的自然能力。"
        milestones = [
            f"第1周：建立仪式感，明确为什么这个目标对你重要。",
            f"第2-3周：搭建基础技能，记录每天的练习反馈。",
            f"第4-5周：在真实情境中应用『{goal}』，收集外部反馈。",
            "第6周：回顾数据，决定是迭代、升级还是庆祝。",
        ]
        weekly_focus = [
            "周一：设定本周最重要的场景与衡量指标。",
            "周三：中途检查，识别阻力并调整计划。",
            "周五：总结亮点，写下下一步的假设。",
        ]
        daily_actions = [
            f"每天投入{daily_minutes}分钟，分成两段：15分钟输入 + {daily_minutes - 15 if daily_minutes > 30 else 10}分钟输出练习。",
            "完成后记录1句“今天顺利的原因”和1句“下次可以更容易”。",
            "每周至少一次邀请朋友或同事进行模拟或反馈。",
        ]
        first_step = "现在就花1分钟写下你最想解决的具体场景，这是行动的开端。"
        tracking_metrics = [
            "完成天数 / 计划天数",
            "能量/心情打分的变化趋势",
            "来自真实场景的正向反馈次数",
        ]

        return GoalPlan(
            goal=goal,
            vision=vision,
            milestones=milestones,
            weekly_focus=weekly_focus,
            daily_actions=daily_actions,
            first_step=first_step,
            tracking_metrics=tracking_metrics,
        )

    # Convenience helpers -------------------------------------------------
    def habit_names(self) -> Iterable[str]:
        return self.memory.habits.keys()

    def add_habit_history(self, name: str, entries: Sequence[HabitEntry]) -> None:
        self.memory.habits[name] = list(entries)

    def add_reflection(self, entry: ReflectionEntry) -> None:
        self.memory.reflections.append(entry)

    def add_decision(self, entry: DecisionRecord) -> None:
        self.memory.decisions.append(entry)
