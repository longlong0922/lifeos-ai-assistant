"""Implementation of the LifeOS lightweight personal AI assistant.

The module focuses on providing a compact, offline friendly toolkit that can
help users plan their day, build habits, manage learning goals and reflect on
emotions.  The implementation deliberately avoids external dependencies so that
it can run in constrained environments such as hackathon demos or edge devices.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Iterable, List, Sequence

ENERGY_LEVELS = ("low", "medium", "high")
POSITIVE_WORDS = {
    "calm",
    "cheerful",
    "confident",
    "energised",
    "excited",
    "focused",
    "grateful",
    "happy",
    "hopeful",
    "joyful",
    "optimistic",
    "proud",
    "relaxed",
}
NEGATIVE_WORDS = {
    "anxious",
    "angry",
    "drained",
    "exhausted",
    "frustrated",
    "guilty",
    "lonely",
    "overwhelmed",
    "sad",
    "stressed",
    "tired",
    "worried",
}


def _parse_time(value: str | time) -> time:
    if isinstance(value, time):
        return value
    hour, minute = [int(part) for part in value.split(":", maxsplit=1)]
    return time(hour=hour, minute=minute)


def _format_time(value: time) -> str:
    return value.strftime("%H:%M")


@dataclass(slots=True)
class UserProfile:
    """Minimal information required to personalise responses."""

    name: str
    focus_areas: Sequence[str] = field(default_factory=tuple)
    wake_time: time | str = "07:30"
    sleep_time: time | str = "23:00"
    preferred_break_minutes: int = 10
    energy_peaks: Sequence[str] = field(
        default_factory=lambda: ("08:00", "11:00", "15:00")
    )

    def __post_init__(self) -> None:
        self.wake_time = _parse_time(self.wake_time)
        self.sleep_time = _parse_time(self.sleep_time)
        self.energy_peaks = tuple(_parse_time(peak) for peak in self.energy_peaks)


@dataclass(slots=True)
class ScheduleBlock:
    start: time
    end: time
    label: str
    category: str = "task"

    def as_dict(self) -> dict[str, str]:
        return {
            "start": _format_time(self.start),
            "end": _format_time(self.end),
            "label": self.label,
            "category": self.category,
        }


@dataclass(slots=True)
class HabitPlan:
    habit: str
    trigger: str
    action_steps: List[str]
    rewards: List[str]
    accountability: str


@dataclass(slots=True)
class LearningRecommendation:
    topic: str
    duration_weeks: int
    milestones: List[str]
    daily_focus_minutes: int
    practice_ideas: List[str]


@dataclass(slots=True)
class MoodInsight:
    summary: str
    dominant_tone: str
    energy_score: float
    encouragement: str


@dataclass(slots=True)
class Task:
    """Representation of a task that should be scheduled."""

    title: str
    duration_minutes: int
    priority: int = 2
    energy: str = "medium"

    def __post_init__(self) -> None:
        if self.priority < 1:
            raise ValueError("priority must be a positive integer")
        energy = self.energy.lower()
        if energy not in ENERGY_LEVELS:
            raise ValueError(f"energy must be one of {ENERGY_LEVELS}")
        self.energy = energy


class LifeOSAssistant:
    """Lightweight reasoning engine that generates personalised suggestions."""

    def __init__(self, profile: UserProfile) -> None:
        self.profile = profile

    def plan_day(self, tasks: Iterable[Task]) -> tuple[List[ScheduleBlock], List[str]]:
        """Generate a day plan containing tasks and restorative breaks.

        The method sorts tasks by priority, distributes them across the day and
        inserts breaks following a simple 90-20 focus rhythm.  A list of
        qualitative insights is returned alongside the schedule to help the user
        stay mindful about their energy and priorities.
        """

        sorted_tasks = sorted(tasks, key=lambda t: (t.priority, -t.duration_minutes))
        schedule: List[ScheduleBlock] = []
        insights: List[str] = []

        current = datetime.combine(datetime.today(), self.profile.wake_time)
        last_break = current
        total_focus_minutes = 0

        for task in sorted_tasks:
            if current.time() >= self.profile.sleep_time:
                insights.append(
                    "Some tasks spill over your sleep time. Consider rescheduling or"
                    " delegating the lower priority ones."
                )
                break

            if (current - last_break).total_seconds() / 60 >= 90:
                break_start = current
                current += timedelta(minutes=self.profile.preferred_break_minutes)
                schedule.append(
                    ScheduleBlock(
                        start=break_start.time(),
                        end=current.time(),
                        label="Recharge break",
                        category="break",
                    )
                )
                last_break = current

            start_time = current
            current += timedelta(minutes=task.duration_minutes)
            total_focus_minutes += task.duration_minutes

            schedule.append(
                ScheduleBlock(
                    start=start_time.time(),
                    end=current.time(),
                    label=task.title,
                    category="focus" if task.priority == 1 else "task",
                )
            )

            if task.priority == 1:
                insights.append(f"Protect '{task.title}' — it advances your key goals.")

        if total_focus_minutes < 240:
            insights.append("Your day has ample buffer. Use it for reflection or learning.")
        elif total_focus_minutes > 420:
            insights.append(
                "The day is dense with focus work. Build in extra recovery rituals"
                " tonight."
            )

        return schedule, insights

    def design_habit(self, habit_name: str, trigger: str, rewards: Sequence[str]) -> HabitPlan:
        steps = [
            f"Define your why: connect '{habit_name}' with one focus area",
            f"Start tiny: dedicate 2 minutes to '{habit_name}' after '{trigger}'",
            "Track completions in a visible streak calendar",
        ]
        accountability = (
            "Share your streak with a trusted friend every Friday to stay accountable."
        )
        return HabitPlan(
            habit=habit_name,
            trigger=trigger,
            action_steps=steps,
            rewards=list(rewards),
            accountability=accountability,
        )

    def recommend_learning_path(
        self, topic: str, available_minutes_per_day: int
    ) -> LearningRecommendation:
        duration_weeks = max(4, min(12, available_minutes_per_day // 10 + 4))
        milestones = [
            f"Week 1-2: map existing strengths related to {topic}",
            f"Week 3-4: follow a curated micro-course or book chapter on {topic}",
            f"Week 5-6: build a practical mini-project applying {topic}",
            "Week 7+: collect feedback and iterate on the project",
        ]
        practice_ideas = [
            f"Teach a friend one concept about {topic} each week",
            f"Apply {topic} to a real scenario from your focus areas",
            "Keep a learning diary capturing insights and open questions",
        ]
        return LearningRecommendation(
            topic=topic,
            duration_weeks=duration_weeks,
            milestones=milestones,
            daily_focus_minutes=available_minutes_per_day,
            practice_ideas=practice_ideas,
        )

    def analyse_mood(self, journal_entries: Sequence[str]) -> MoodInsight:
        if not journal_entries:
            return MoodInsight(
                summary="No entries provided.",
                dominant_tone="neutral",
                energy_score=0.0,
                encouragement="Start jotting a few words daily to spot patterns.",
            )

        words = " ".join(journal_entries).lower().split()
        positive_hits = sum(1 for word in words if word.strip(".,!") in POSITIVE_WORDS)
        negative_hits = sum(1 for word in words if word.strip(".,!") in NEGATIVE_WORDS)
        total = max(1, positive_hits + negative_hits)
        balance = (positive_hits - negative_hits) / total

        if balance > 0.25:
            tone = "uplifting"
            encouragement = "Channel the positive energy into a meaningful challenge."
        elif balance < -0.25:
            tone = "heavy"
            encouragement = "Be gentle with yourself; prioritise rest and support."
        else:
            tone = "mixed"
            encouragement = "Ground yourself with a short walk and gratitude note."

        energy_score = min(1.0, max(-1.0, balance))
        summary = (
            f"Across {len(journal_entries)} entries you mentioned {positive_hits} positive"
            f" and {negative_hits} draining emotions."
        )
        return MoodInsight(
            summary=summary,
            dominant_tone=tone,
            energy_score=energy_score,
            encouragement=encouragement,
        )

    def reflect(self) -> str:
        focus_list = ", ".join(self.profile.focus_areas) or "your priorities"
        return (
            f"{self.profile.name}, remember that progress compounds when you honour"
            f" {focus_list}. Check in with your energy before committing to new"
            " obligations today."
        )
