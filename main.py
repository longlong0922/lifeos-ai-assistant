"""Command line helper demonstrating the LifeOS coaching flows."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from lifeos_ai_assistant import (
    HabitEntry,
    LifeOSAssistant,
    LifeOSMemory,
    UserProfile,
)


def _load_memory(path: str | None) -> LifeOSMemory:
    if not path:
        return LifeOSMemory()
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Memory file '{path}' does not exist")
    with file_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return LifeOSMemory.from_dict(raw)


def _build_assistant(args: argparse.Namespace) -> LifeOSAssistant:
    memory = _load_memory(getattr(args, "memory", None))
    focus = tuple(getattr(args, "focus", ()) or ())
    profile = UserProfile(name=args.name, focus_areas=focus)
    return LifeOSAssistant(profile, memory)


def run_habit(args: argparse.Namespace) -> None:
    assistant = _build_assistant(args)
    history = assistant.memory.habits.get(args.habit, [])
    if args.history:
        with Path(args.history).open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        history = [HabitEntry.from_dict(item) for item in raw]
    insight = assistant.habit_coaching(args.habit, history)
    print(json.dumps(insight.as_dict(), ensure_ascii=False, indent=2))


def run_decision(args: argparse.Namespace) -> None:
    assistant = _build_assistant(args)
    guide = assistant.decision_support(args.question, args.options)
    print(json.dumps(guide.as_dict(), ensure_ascii=False, indent=2))


def run_brief(args: argparse.Namespace) -> None:
    assistant = _build_assistant(args)
    brief = assistant.daily_brief(date.fromisoformat(args.date) if args.date else None)
    print(json.dumps(brief.as_dict(), ensure_ascii=False, indent=2))


def run_reflection(args: argparse.Namespace) -> None:
    assistant = _build_assistant(args)
    response = assistant.reflection_dialogue(args.message)
    print(json.dumps(response.as_dict(), ensure_ascii=False, indent=2))


def run_goal(args: argparse.Namespace) -> None:
    assistant = _build_assistant(args)
    plan = assistant.goal_breakdown(
        goal=args.goal,
        daily_minutes=args.minutes,
        weeks=args.weeks,
        focus_area=args.focus_area,
    )
    print(json.dumps(plan.as_dict(), ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="用户昵称")
    parser.add_argument("--focus", nargs="*", help="关注主题，例如成长、健康")
    parser.add_argument("--memory", help="包含历史数据的JSON文件")

    sub = parser.add_subparsers(dest="command", required=True)

    habit_parser = sub.add_parser("habit", help="生成习惯洞察和教练建议")
    habit_parser.add_argument("--habit", required=True, help="习惯名称")
    habit_parser.add_argument("--history", help="独立的习惯历史数据JSON文件")
    habit_parser.set_defaults(func=run_habit)

    decision_parser = sub.add_parser("decision", help="获得决策辅导")
    decision_parser.add_argument("--question", required=True)
    decision_parser.add_argument("--options", nargs="+", required=True)
    decision_parser.set_defaults(func=run_decision)

    brief_parser = sub.add_parser("brief", help="生成今日策略简报")
    brief_parser.add_argument("--date", help="指定日期，默认今天")
    brief_parser.set_defaults(func=run_brief)

    reflection_parser = sub.add_parser("reflect", help="开启深度反思对话")
    reflection_parser.add_argument("--message", required=True)
    reflection_parser.set_defaults(func=run_reflection)

    goal_parser = sub.add_parser("goal", help="把愿望拆解成可执行路径")
    goal_parser.add_argument("--goal", required=True)
    goal_parser.add_argument("--minutes", type=int, required=True)
    goal_parser.add_argument("--weeks", type=int)
    goal_parser.add_argument("--focus-area")
    goal_parser.set_defaults(func=run_goal)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
