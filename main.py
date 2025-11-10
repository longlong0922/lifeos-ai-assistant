"""Command line interface for the LifeOS AI assistant prototype."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lifeos_ai_assistant import LifeOSAssistant, Task, UserProfile


def _load_tasks(path: Path) -> list[Task]:
    if not path.exists():
        raise FileNotFoundError(f"Task file '{path}' does not exist")
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    tasks = [
        Task(
            title=item["title"],
            duration_minutes=item.get("duration", 30),
            priority=item.get("priority", 2),
            energy=item.get("energy", "medium"),
        )
        for item in raw
    ]
    return tasks


def plan_day(args: argparse.Namespace) -> None:
    profile = UserProfile(
        name=args.name,
        focus_areas=tuple(args.focus or []),
        wake_time=args.wake,
        sleep_time=args.sleep,
    )
    assistant = LifeOSAssistant(profile)
    tasks = _load_tasks(Path(args.tasks))
    schedule, insights = assistant.plan_day(tasks)

    print("Daily schedule:")
    for block in schedule:
        print(f"- {block.start.strftime('%H:%M')} -> {block.end.strftime('%H:%M')}: {block.label}")
    if insights:
        print("\nInsights:")
        for note in insights:
            print(f"* {note}")


def reflect(args: argparse.Namespace) -> None:
    profile = UserProfile(name=args.name, focus_areas=tuple(args.focus or ()))
    assistant = LifeOSAssistant(profile)
    print(assistant.reflect())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    plan_parser = sub.add_parser("plan", help="Generate a personalised schedule")
    plan_parser.add_argument("--name", required=True)
    plan_parser.add_argument("--tasks", required=True, help="Path to JSON task list")
    plan_parser.add_argument("--wake", default="07:30")
    plan_parser.add_argument("--sleep", default="23:00")
    plan_parser.add_argument("--focus", nargs="*", help="Focus areas to highlight")
    plan_parser.set_defaults(func=plan_day)

    reflect_parser = sub.add_parser(
        "reflect", help="Receive a short daily reflection reminder"
    )
    reflect_parser.add_argument("--name", required=True)
    reflect_parser.add_argument("--focus", nargs="*", help="Focus areas to highlight")
    reflect_parser.set_defaults(func=reflect)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
