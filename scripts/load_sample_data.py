"""
加载示例数据到数据库
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Database
from configs.settings import get_settings


def load_sample_data():
    """加载示例数据"""
    settings = get_settings()
    db = Database(settings.DB_PATH)
    
    # 读取示例数据
    sample_file = project_root / "data" / "samples" / "demo_data.json"
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📁 Loading sample data from: {sample_file}")
    
    # 创建用户
    print("\n👤 Creating users...")
    user_ids = {}
    for user_data in data.get('users', []):
        try:
            user_id = db.create_user(
                username=user_data['username'],
                timezone=user_data.get('timezone', 'Asia/Shanghai')
            )
            user_ids[user_data['username']] = user_id
            print(f"  ✅ Created user: {user_data['username']} (ID: {user_id})")
        except Exception as e:
            # 用户可能已存在
            print(f"  ⚠️  User {user_data['username']} might already exist: {e}")
            # 假设第一个用户 ID 是 1
            user_ids[user_data['username']] = 1
    
    # 默认用户
    default_user_id = list(user_ids.values())[0] if user_ids else 1
    
    # 创建习惯
    print("\n🎯 Creating habits...")
    habit_ids = {}
    for habit_data in data.get('habits', []):
        habit_id = db.create_habit(
            user_id=default_user_id,
            name=habit_data['name'],
            description=habit_data.get('description'),
            target_frequency=habit_data.get('target_frequency', 'daily')
        )
        habit_ids[habit_data['name']] = habit_id
        print(f"  ✅ Created habit: {habit_data['name']} (ID: {habit_id})")
    
    # 添加习惯记录
    print("\n📊 Adding habit records...")
    for record_data in data.get('habit_records', []):
        habit_id = habit_ids.get(record_data['habit_name'])
        if habit_id:
            date = datetime.fromisoformat(record_data['date'])
            db.add_habit_record(
                habit_id=habit_id,
                user_id=default_user_id,
                date=date,
                status=record_data['status'],
                context=record_data.get('context')
            )
            print(f"  ✅ Added record for {record_data['habit_name']} on {record_data['date']}")
    
    # 保存反思
    print("\n💭 Saving reflections...")
    for reflection_data in data.get('reflections', []):
        date = datetime.fromisoformat(reflection_data['date'])
        db.save_reflection(
            user_id=default_user_id,
            date=date,
            conversation=reflection_data['conversation'],
            insights=reflection_data.get('insights')
        )
        print(f"  ✅ Saved reflection for {reflection_data['date']}")
    
    # 创建目标
    print("\n🎓 Creating goals...")
    for goal_data in data.get('goals', []):
        deadline = datetime.fromisoformat(goal_data['deadline']) if goal_data.get('deadline') else None
        goal_id = db.create_goal(
            user_id=default_user_id,
            title=goal_data['title'],
            description=goal_data['description'],
            deadline=deadline,
            milestones=goal_data.get('milestones', []),
            daily_tasks=goal_data.get('daily_tasks', [])
        )
        print(f"  ✅ Created goal: {goal_data['title']} (ID: {goal_id})")
    
    # 保存决策
    print("\n🔮 Saving decisions...")
    for decision_data in data.get('decisions', []):
        decision_id = db.save_decision(
            user_id=default_user_id,
            question=decision_data['question'],
            factors=decision_data.get('factors', []),
            recommendation=decision_data.get('recommendation')
        )
        print(f"  ✅ Saved decision: {decision_data['question'][:50]}... (ID: {decision_id})")
    
    print("\n🎉 Sample data loaded successfully!")
    print(f"\n📊 Summary:")
    print(f"  - Users: {len(user_ids)}")
    print(f"  - Habits: {len(habit_ids)}")
    print(f"  - Habit Records: {len(data.get('habit_records', []))}")
    print(f"  - Reflections: {len(data.get('reflections', []))}")
    print(f"  - Goals: {len(data.get('goals', []))}")
    print(f"  - Decisions: {len(data.get('decisions', []))}")
    print(f"\n💡 You can now start the server and test with user ID: {default_user_id}")


if __name__ == "__main__":
    load_sample_data()
