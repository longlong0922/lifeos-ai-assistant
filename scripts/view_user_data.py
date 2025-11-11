#!/usr/bin/env python3
"""
查看用户数据工具
用于查看数据库中所有用户的详细数据
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Database
from datetime import datetime
import json


def print_header(title: str):
    """打印美化的标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print("─" * 70)


def format_timestamp(ts):
    """格式化时间戳"""
    if not ts:
        return "无"
    try:
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts)
        else:
            dt = ts
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(ts)


def view_all_users(db: Database):
    """查看所有用户列表"""
    print_header("👥 所有用户列表")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, created_at, timezone, preferences
            FROM users
            ORDER BY id
        """)
        users = cursor.fetchall()
    
    if not users:
        print("\n⚠️  数据库中没有用户")
        return []
    
    print(f"\n共找到 {len(users)} 个用户：\n")
    
    user_list = []
    for user in users:
        user_id = user['id']
        username = user['username']
        created_at = format_timestamp(user['created_at'])
        timezone = user['timezone']
        
        print(f"  [{user_id}] {username}")
        print(f"      创建时间: {created_at}")
        print(f"      时区: {timezone}")
        
        # 获取用户统计
        stats = get_user_stats(db, user_id)
        print(f"      数据统计: {stats['habits']}个习惯, {stats['goals']}个目标, "
              f"{stats['reflections']}条反思, {stats['decisions']}个决策")
        print()
        
        user_list.append(user_id)
    
    return user_list


def get_user_stats(db: Database, user_id: int) -> dict:
    """获取用户统计数据"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # 习惯数
        cursor.execute("SELECT COUNT(*) as cnt FROM habits WHERE user_id = ?", (user_id,))
        habits_count = cursor.fetchone()['cnt']
        
        # 目标数
        cursor.execute("SELECT COUNT(*) as cnt FROM goals WHERE user_id = ?", (user_id,))
        goals_count = cursor.fetchone()['cnt']
        
        # 反思数
        cursor.execute("SELECT COUNT(*) as cnt FROM reflections WHERE user_id = ?", (user_id,))
        reflections_count = cursor.fetchone()['cnt']
        
        # 决策数
        cursor.execute("SELECT COUNT(*) as cnt FROM decisions WHERE user_id = ?", (user_id,))
        decisions_count = cursor.fetchone()['cnt']
        
        # 聊天记录数
        cursor.execute("SELECT COUNT(*) as cnt FROM chat_history WHERE user_id = ?", (user_id,))
        chat_count = cursor.fetchone()['cnt']
    
    return {
        'habits': habits_count,
        'goals': goals_count,
        'reflections': reflections_count,
        'decisions': decisions_count,
        'chats': chat_count
    }


def view_user_habits(db: Database, user_id: int):
    """查看用户的习惯"""
    print_section("🏃 习惯列表")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.*, COUNT(hr.id) as record_count
            FROM habits h
            LEFT JOIN habit_records hr ON h.id = hr.habit_id
            WHERE h.user_id = ?
            GROUP BY h.id
            ORDER BY h.created_at DESC
        """, (user_id,))
        habits = cursor.fetchall()
        
        if not habits:
            print("  暂无习惯数据")
            return
        
        for habit in habits:
            status = "✅ 活跃" if habit['is_active'] else "❌ 已停用"
            print(f"\n  [{habit['id']}] {habit['name']} ({status})")
            if habit['description']:
                print(f"      描述: {habit['description']}")
            print(f"      频率: {habit['target_frequency']}")
            print(f"      创建时间: {format_timestamp(habit['created_at'])}")
            print(f"      打卡次数: {habit['record_count']}")
            
            # 获取最近的记录
            cursor.execute("""
                SELECT date, status, context
                FROM habit_records
                WHERE habit_id = ?
                ORDER BY date DESC
                LIMIT 3
            """, (habit['id'],))
            records = cursor.fetchall()
            
            if records:
                print(f"      最近打卡:")
                for record in records:
                    date = format_timestamp(record['date'])
                    status_emoji = "✅" if record['status'] == 'completed' else "❌"
                    print(f"        {status_emoji} {date}")
                    if record['context']:
                        context = record['context'][:50] + "..." if len(record['context']) > 50 else record['context']
                        print(f"           {context}")


def view_user_goals(db: Database, user_id: int):
    """查看用户的目标"""
    print_section("🎯 目标列表")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM goals
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        goals = cursor.fetchall()
    
    if not goals:
        print("  暂无目标数据")
        return
    
    for goal in goals:
        status_emoji = {"active": "🟢", "completed": "✅", "paused": "⏸️", "cancelled": "❌"}.get(goal['status'], "⚪")
        print(f"\n  [{goal['id']}] {goal['title']} {status_emoji} {goal['status']}")
        print(f"      {goal['description']}")
        print(f"      进度: {goal['progress']:.1f}%")
        if goal['deadline']:
            print(f"      截止: {format_timestamp(goal['deadline'])}")
        print(f"      创建: {format_timestamp(goal['created_at'])}")
        
        # 解析里程碑
        try:
            milestones = json.loads(goal['milestones']) if goal['milestones'] else []
            if milestones:
                print(f"      里程碑: {len(milestones)}个")
                for i, milestone in enumerate(milestones[:3], 1):
                    print(f"        {i}. {milestone}")
        except:
            pass


def view_user_reflections(db: Database, user_id: int):
    """查看用户的反思"""
    print_section("💭 反思记录")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM reflections
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 5
        """, (user_id,))
        reflections = cursor.fetchall()
    
    if not reflections:
        print("  暂无反思数据")
        return
    
    for reflection in reflections:
        print(f"\n  [{reflection['id']}] {format_timestamp(reflection['date'])}")
        
        # 显示对话摘要
        conversation = reflection['conversation']
        if len(conversation) > 100:
            conversation = conversation[:100] + "..."
        print(f"      对话: {conversation}")
        
        if reflection['insights']:
            insights = reflection['insights']
            if len(insights) > 100:
                insights = insights[:100] + "..."
            print(f"      洞察: {insights}")


def view_user_decisions(db: Database, user_id: int):
    """查看用户的决策"""
    print_section("🔮 决策记录")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM decisions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id,))
        decisions = cursor.fetchall()
    
    if not decisions:
        print("  暂无决策数据")
        return
    
    for decision in decisions:
        print(f"\n  [{decision['id']}] {format_timestamp(decision['created_at'])}")
        print(f"      问题: {decision['question']}")
        
        # 解析因素
        try:
            factors = json.loads(decision['factors']) if decision['factors'] else []
            if factors:
                print(f"      考虑因素:")
                for factor in factors[:3]:
                    print(f"        • {factor}")
        except:
            pass
        
        if decision['user_choice']:
            print(f"      用户选择: {decision['user_choice']}")
        
        if decision['outcome']:
            outcome = decision['outcome']
            if len(outcome) > 80:
                outcome = outcome[:80] + "..."
            print(f"      结果: {outcome}")


def view_user_chats(db: Database, user_id: int, limit: int = 10):
    """查看用户的聊天历史"""
    print_section(f"💬 最近聊天记录 (最多{limit}条)")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content, timestamp, session_id
            FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        chats = cursor.fetchall()
    
    if not chats:
        print("  暂无聊天记录")
        return
    
    current_session = None
    for chat in reversed(chats):  # 按时间正序显示
        # 如果是新会话，显示分隔符
        if chat['session_id'] != current_session:
            if current_session is not None:
                print()
            current_session = chat['session_id']
            print(f"\n  ─── 会话 {chat['session_id'][:8]}... ───")
        
        timestamp = format_timestamp(chat['timestamp'])
        role_emoji = "👤" if chat['role'] == 'user' else "🤖"
        role_name = "用户" if chat['role'] == 'user' else "AI"
        
        content = chat['content']
        if len(content) > 150:
            content = content[:150] + "..."
        
        print(f"  {role_emoji} {role_name} [{timestamp}]:")
        print(f"     {content}")


def view_user_detail(db: Database, user_id: int):
    """查看单个用户的详细数据"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
    
    if not user:
        print(f"\n❌ 找不到用户 ID: {user_id}")
        return
    
    print_header(f"👤 用户详情: {user['username']} (ID: {user_id})")
    
    print(f"\n基本信息:")
    print(f"  用户名: {user['username']}")
    print(f"  用户ID: {user['id']}")
    print(f"  创建时间: {format_timestamp(user['created_at'])}")
    print(f"  时区: {user['timezone']}")
    
    # 解析偏好设置
    try:
        preferences = json.loads(user['preferences']) if user['preferences'] else {}
        if preferences:
            print(f"  偏好设置: {json.dumps(preferences, ensure_ascii=False, indent=4)}")
    except:
        pass
    
    # 显示统计
    stats = get_user_stats(db, user_id)
    print(f"\n数据统计:")
    print(f"  📊 习惯数量: {stats['habits']}")
    print(f"  🎯 目标数量: {stats['goals']}")
    print(f"  💭 反思数量: {stats['reflections']}")
    print(f"  🔮 决策数量: {stats['decisions']}")
    print(f"  💬 聊天记录: {stats['chats']}")
    
    # 显示详细数据
    view_user_habits(db, user_id)
    view_user_goals(db, user_id)
    view_user_reflections(db, user_id)
    view_user_decisions(db, user_id)
    view_user_chats(db, user_id)


def interactive_mode(db: Database):
    """交互式查看模式"""
    while True:
        print_header("🔍 用户数据查看器")
        print("\n请选择操作：")
        print("  1. 查看所有用户列表")
        print("  2. 查看指定用户详情")
        print("  3. 比较多个用户数据")
        print("  0. 退出")
        
        choice = input("\n请输入选项 (0-3): ").strip()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        
        elif choice == '1':
            view_all_users(db)
            input("\n按回车继续...")
        
        elif choice == '2':
            user_list = view_all_users(db)
            if user_list:
                user_id = input("\n请输入要查看的用户 ID: ").strip()
                try:
                    user_id = int(user_id)
                    view_user_detail(db, user_id)
                except ValueError:
                    print("❌ 无效的用户 ID")
            input("\n按回车继续...")
        
        elif choice == '3':
            user_list = view_all_users(db)
            if user_list:
                ids = input("\n请输入要比较的用户 ID（用逗号分隔，如 1,2,3）: ").strip()
                try:
                    user_ids = [int(x.strip()) for x in ids.split(',')]
                    compare_users(db, user_ids)
                except ValueError:
                    print("❌ 无效的用户 ID")
            input("\n按回车继续...")
        
        else:
            print("❌ 无效的选项")


def compare_users(db: Database, user_ids: list):
    """比较多个用户的数据"""
    print_header(f"📊 用户数据对比 (共{len(user_ids)}个用户)")
    
    print(f"\n{'用户ID':<10} {'用户名':<15} {'习惯':<8} {'目标':<8} {'反思':<8} {'决策':<8} {'聊天':<8}")
    print("─" * 70)
    
    for user_id in user_ids:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
        
        if not user:
            print(f"{user_id:<10} {'(不存在)':<15} {'-':<8} {'-':<8} {'-':<8} {'-':<8} {'-':<8}")
            continue
        
        stats = get_user_stats(db, user_id)
        print(f"{user_id:<10} {user['username']:<15} {stats['habits']:<8} {stats['goals']:<8} "
              f"{stats['reflections']:<8} {stats['decisions']:<8} {stats['chats']:<8}")


def main():
    """主函数"""
    db = Database()
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            # 列出所有用户
            view_all_users(db)
        elif sys.argv[1] == 'view' and len(sys.argv) > 2:
            # 查看指定用户
            try:
                user_id = int(sys.argv[2])
                view_user_detail(db, user_id)
            except ValueError:
                print("❌ 无效的用户 ID")
        elif sys.argv[1] == 'compare' and len(sys.argv) > 2:
            # 比较多个用户
            try:
                user_ids = [int(x) for x in sys.argv[2:]]
                compare_users(db, user_ids)
            except ValueError:
                print("❌ 无效的用户 ID")
        else:
            print("用法:")
            print("  python view_user_data.py           # 交互式模式")
            print("  python view_user_data.py list      # 列出所有用户")
            print("  python view_user_data.py view <id> # 查看指定用户")
            print("  python view_user_data.py compare <id1> <id2> ...  # 比较多个用户")
    else:
        # 交互式模式
        interactive_mode(db)


if __name__ == "__main__":
    main()
