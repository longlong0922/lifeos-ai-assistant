from lifeos_ai_assistant import LifeOSAssistant, Task, UserProfile


def build_assistant() -> LifeOSAssistant:
    profile = UserProfile(
        name="Test User",
        focus_areas=("health", "learning"),
        wake_time="07:00",
        sleep_time="22:30",
    )
    return LifeOSAssistant(profile)


def test_plan_day_generates_breaks_and_insights():
    assistant = build_assistant()
    tasks = [
        Task(title="Deep Work", duration_minutes=120, priority=1, energy="high"),
        Task(title="Admin", duration_minutes=45, priority=3, energy="low"),
        Task(title="Workout", duration_minutes=60, priority=2, energy="high"),
    ]

    schedule, insights = assistant.plan_day(tasks)

    labels = [block.label for block in schedule]
    assert "Deep Work" in labels
    assert any(block.category == "break" for block in schedule)
    assert insights, "Expected at least one insight to be generated"


def test_learning_path_duration_adjusts_with_time_commitment():
    assistant = build_assistant()
    recommendation_low = assistant.recommend_learning_path("python", 30)
    recommendation_high = assistant.recommend_learning_path("python", 120)

    assert recommendation_low.duration_weeks <= recommendation_high.duration_weeks
    assert recommendation_low.daily_focus_minutes == 30


def test_mood_analysis_handles_positive_and_negative_words():
    assistant = build_assistant()
    entries = [
        "I felt happy and focused today.",
        "Yesterday I was exhausted but hopeful for tomorrow.",
    ]

    report = assistant.analyse_mood(entries)
    assert report.summary.startswith("Across 2 entries")
    assert report.dominant_tone in {"uplifting", "mixed", "heavy"}
    assert -1.0 <= report.energy_score <= 1.0
