"""
查看数据库中的所有数据
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.database import Database

def show_database_content():
    """显示数据库内容"""
    settings = get_settings()
    db = Database(settings.DB_PATH)
    
    print("=" * 60)
    print("📊 LifeOS 数据库内容")
    print("=" * 60)
    
    # 查看用户
    print("\n👥 用户列表:")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if users:
            for user in users:
                user_dict = dict(user)
                print(f"  ID: {user_dict['id']}, 用户名: {user_dict['username']}")
        else:
            print("  暂无用户")
    
    # 默认用户 ID
    user_id = 1
    
    # 查看习惯
    print("\n🎯 习惯列表:")
    habits = db.get_user_habits(user_id)
    if habits:
        for habit in habits:
            print(f"  • {habit['name']}")
            print(f"    描述: {habit['description']}")
            print(f"    频率: {habit['target_frequency']}")
            
            # 获取最近的记录
            records = db.get_habit_records(habit['id'], limit=5)
            if records:
                print(f"    最近记录:")
                for record in records:
                    status_emoji = {
                        'completed': '✅',
                        'missed': '❌',
                        'partial': '⚠️'
                    }.get(record['status'], '❓')
                    print(f"      {status_emoji} {record['date']}: {record['status']}")
                    if record['context']:
                        print(f"         情境: {record['context']}")
            print()
    else:
        print("  暂无习惯")
        print("  💡 运行 'python scripts/load_sample_data.py' 加载示例数据")
    
    # 查看目标
    print("\n🎓 目标列表:")
    goals = db.get_user_goals(user_id)
    if goals:
        for goal in goals:
            print(f"  • {goal['title']}")
            print(f"    描述: {goal['description']}")
            if goal['deadline']:
                print(f"    截止日期: {goal['deadline']}")
            print()
    else:
        print("  暂无目标")
    
    # 查看反思记录
    print("\n💭 反思记录:")
    reflections = db.get_recent_reflections(user_id, limit=5)
    if reflections:
        for reflection in reflections:
            print(f"  • 日期: {reflection['date']}")
            if reflection['insights']:
                print(f"    洞察: {reflection['insights']}")
            print()
    else:
        print("  暂无反思记录")
    
    # 查看聊天历史
    print("\n💬 最近聊天:")
    history = db.get_chat_history(user_id, limit=10)
    if history:
        for msg in history[-5:]:  # 显示最后5条
            role_emoji = "😊" if msg['role'] == 'user' else "🤖"
            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            print(f"  {role_emoji} {content}")
    else:
        print("  暂无聊天记录")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("📈 统计总览")
    print("=" * 60)
    print(f"  习惯数量: {len(habits)}")
    print(f"  目标数量: {len(goals)}")
    print(f"  反思记录: {len(reflections)}")
    print(f"  聊天记录: {len(history)}")
    
    # 习惯记录统计
    if habits:
        total_records = 0
        completed_records = 0
        for habit in habits:
            records = db.get_habit_records(habit['id'])
            total_records += len(records)
            completed_records += len([r for r in records if r['status'] == 'completed'])
        
        print(f"  习惯总记录: {total_records}")
        if total_records > 0:
            completion_rate = (completed_records / total_records * 100)
            print(f"  完成率: {completion_rate:.1f}%")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    show_database_content()
