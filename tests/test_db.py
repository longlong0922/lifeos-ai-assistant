"""
数据库测试
"""
import pytest
import tempfile
import os
from datetime import datetime
from app.database import Database


@pytest.fixture
def temp_db():
    """创建临时数据库"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    # 清理
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_create_user(temp_db):
    """测试创建用户"""
    user_id = temp_db.create_user("test_user")
    assert user_id > 0
    
    user = temp_db.get_user(user_id)
    assert user is not None
    assert user['username'] == "test_user"


def test_create_habit(temp_db):
    """测试创建习惯"""
    user_id = temp_db.create_user("test_user")
    habit_id = temp_db.create_habit(user_id, "跑步", "每天跑步30分钟")
    
    assert habit_id > 0
    
    habits = temp_db.get_user_habits(user_id)
    assert len(habits) == 1
    assert habits[0]['name'] == "跑步"


def test_habit_records(temp_db):
    """测试习惯记录"""
    user_id = temp_db.create_user("test_user")
    habit_id = temp_db.create_habit(user_id, "跑步")
    
    # 添加完成记录
    record_id = temp_db.add_habit_record(
        habit_id=habit_id,
        user_id=user_id,
        date=datetime.now(),
        status="completed",
        context="天气很好"
    )
    
    assert record_id > 0
    
    records = temp_db.get_habit_records(habit_id)
    assert len(records) == 1
    assert records[0]['status'] == "completed"


def test_save_reflection(temp_db):
    """测试保存反思"""
    user_id = temp_db.create_user("test_user")
    
    conversation = [
        {"role": "user", "content": "今天很累"},
        {"role": "assistant", "content": "为什么累呢？"}
    ]
    
    reflection_id = temp_db.save_reflection(
        user_id=user_id,
        date=datetime.now(),
        conversation=conversation,
        insights="用户提到了疲劳"
    )
    
    assert reflection_id > 0
    
    reflections = temp_db.get_recent_reflections(user_id)
    assert len(reflections) == 1


def test_create_goal(temp_db):
    """测试创建目标"""
    user_id = temp_db.create_user("test_user")
    
    goal_id = temp_db.create_goal(
        user_id=user_id,
        title="学好英语",
        description="每天练习30分钟"
    )
    
    assert goal_id > 0
    
    goals = temp_db.get_user_goals(user_id)
    assert len(goals) == 1
    assert goals[0]['title'] == "学好英语"


def test_chat_history(temp_db):
    """测试聊天历史"""
    user_id = temp_db.create_user("test_user")
    
    # 保存几条消息
    temp_db.save_chat_message(user_id, "user", "你好")
    temp_db.save_chat_message(user_id, "assistant", "你好！有什么可以帮你的？")
    
    history = temp_db.get_chat_history(user_id, limit=10)
    assert len(history) == 2
    assert history[0]['role'] == "user"
    assert history[1]['role'] == "assistant"
