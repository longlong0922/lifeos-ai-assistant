import unittest
from datetime import date, timedelta

from lifeos_ai_assistant.assistant import (
    UserProfile,
    LifeOSMemory,
    HabitEntry,
    ReflectionEntry,
    LifeOSAssistant,
)


class CoreBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = UserProfile(name="测试用户", focus_areas=("阅读",))
        self.memory = LifeOSMemory()
        today = date.today()
        # habit history
        self.memory.habits["跑步"] = [
            HabitEntry(date=today - timedelta(days=2), completed=True, note="下午 4 点"),
            HabitEntry(date=today - timedelta(days=1), completed=False, note="加班"),
        ]
        # reflections
        self.memory.reflections = [
            ReflectionEntry(date=today - timedelta(days=2), mood=7, energy=70, content="不错"),
            ReflectionEntry(date=today - timedelta(days=1), mood=4, energy=40, content="太累了"),
        ]
        self.assistant = LifeOSAssistant(self.profile, self.memory)

    def test_habit_coaching_returns_insight(self):
        insight = self.assistant.habit_coaching("跑步")
        self.assertIsNotNone(insight)
        self.assertEqual(insight.name, "跑步")
        self.assertIsInstance(insight.success_rate, float)

    def test_decision_support_returns_guide(self):
        guide = self.assistant.decision_support("聚会？", ["去", "不去"]) 
        self.assertTrue(hasattr(guide, "recommendation"))
        self.assertTrue(isinstance(guide.clarifying_questions, list))

    def test_daily_brief_produces_fields(self):
        brief = self.assistant.daily_brief()
        self.assertIn("energyPrediction", brief.as_dict())

    def test_reflection_dialogue_detects_emotion(self):
        resp = self.assistant.reflection_dialogue("我今天很累，工作太多")
        self.assertIsInstance(resp.detected_emotions, list)

    def test_goal_breakdown_plan_structure(self):
        plan = self.assistant.goal_breakdown("学英语", daily_minutes=20, weeks=3)
        self.assertIn("goal", plan.as_dict())


if __name__ == "__main__":
    unittest.main()
from datetime import date, timedelta

import pytest

from lifeos_ai_assistant import (
    HabitEntry,
    LifeOSAssistant,
    LifeOSMemory,
    ReflectionEntry,
    UserProfile,
)


@pytest.fixture()
def profile() -> UserProfile:
    return UserProfile(name="小明", focus_areas=("健康", "成长"))


def test_habit_coaching_spots_windows_and_obstacles(profile: UserProfile) -> None:
    today = date.today()
    history = [
        HabitEntry(date=today - timedelta(days=3), completed=True, note="下午4-6点 天气好"),
        HabitEntry(date=today - timedelta(days=2), completed=False, note="加班到九点 太累"),
        HabitEntry(date=today - timedelta(days=1), completed=True, note="下午 和朋友约跑"),
    ]
    assistant = LifeOSAssistant(profile)
    insight = assistant.habit_coaching("晨跑", history)

    assert 0 < insight.success_rate < 1
    assert any("下午" in window for window in insight.best_windows)
    assert any("加班" in stress for stress in insight.stressors)
    assert insight.suggestions


def test_decision_support_adapts_to_low_mood(profile: UserProfile) -> None:
    today = date.today()
    memory = LifeOSMemory(
        reflections=[
            ReflectionEntry(date=today - timedelta(days=i), mood=4, energy=58, content="会议太多")
            for i in range(1, 4)
        ]
    )
    assistant = LifeOSAssistant(profile, memory)
    guide = assistant.decision_support("周末要不要去聚会", ["参加", "休息"])

    assert len(guide.clarifying_questions) >= 3
    assert "情绪" in guide.clarifying_questions[2]
    assert "倾向" in guide.recommendation
    assert guide.pattern_summary


def test_daily_brief_uses_memory_for_priorities(profile: UserProfile) -> None:
    today = date.today()
    memory = LifeOSMemory.from_dict(
        {
            "habits": [
                {
                    "name": "晨跑",
                    "history": [
                        {"date": (today - timedelta(days=i)).isoformat(), "completed": i % 2 == 0, "note": "下午"}
                        for i in range(1, 6)
                    ],
                }
            ],
            "reflections": [
                {"date": (today - timedelta(days=i)).isoformat(), "mood": 6 + (i % 2), "energy": 65 + i}
                for i in range(1, 4)
            ],
            "insights": {"stressTriggers": ["会议多"], "productiveDays": ["周二"]},
        }
    )
    assistant = LifeOSAssistant(profile, memory)
    brief = assistant.daily_brief(today)

    assert 50 <= brief.energy_prediction <= 95
    assert brief.priorities, "Expect at least one priority entry"
    assert any("会议" in risk for risk in brief.risks)


def test_reflection_dialogue_flags_emotions(profile: UserProfile) -> None:
    memory = LifeOSMemory(
        reflections=[
            ReflectionEntry(date=date.today() - timedelta(days=1), content="会议拖延，让人累"),
            ReflectionEntry(date=date.today() - timedelta(days=2), content="会议拖延 真的累"),
        ]
    )
    assistant = LifeOSAssistant(profile, memory)
    response = assistant.reflection_dialogue("今天真的好累，感觉无力")

    assert "疲惫" in response.detected_emotions
    assert any("能量" in question for question in response.follow_up_questions)
    assert response.recurring_pattern is not None


def test_goal_breakdown_creates_actionable_steps(profile: UserProfile) -> None:
    assistant = LifeOSAssistant(profile)
    plan = assistant.goal_breakdown("提升英语口语", daily_minutes=30, weeks=6, focus_area="学习")

    assert "提升英语口语" in plan.vision
    assert len(plan.milestones) == 4
    assert any("1分钟" in plan.first_step for _ in range(1))
    assert any("完成天数" in metric for metric in plan.tracking_metrics)
