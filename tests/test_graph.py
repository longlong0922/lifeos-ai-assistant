"""
Graph 流程测试
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import tempfile
import os
from app.database import Database
from app.llm_provider import MockLLMProvider
from app.graph import LifeOSGraph


def test_chat_flow():
    """测试基本聊天流程"""
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        llm = MockLLMProvider()
        graph = LifeOSGraph(db, llm)
        
        # 创建测试用户
        user_id = db.create_user("test_user")
        
        # 测试普通聊天
        result = graph.run(user_id, "你好")
        assert result['response'] is not None
        assert len(result['response']) > 0
        
        print(f"✅ Chat response: {result['response'][:50]}...")
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_habit_flow():
    """测试习惯追踪流程"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        llm = MockLLMProvider()
        graph = LifeOSGraph(db, llm)
        
        user_id = db.create_user("test_user")
        db.create_habit(user_id, "跑步", "每天跑步30分钟")
        
        # 测试习惯相关对话
        result = graph.run(user_id, "我今天完成了跑步")
        assert result['response'] is not None
        assert "习惯" in result['response'] or "成功" in result['response']
        
        print(f"✅ Habit response: {result['response'][:50]}...")
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_decision_flow():
    """测试决策支持流程"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        llm = MockLLMProvider()
        graph = LifeOSGraph(db, llm)
        
        user_id = db.create_user("test_user")
        
        # 测试决策相关对话
        result = graph.run(user_id, "我要不要去参加聚会？")
        assert result['response'] is not None
        
        print(f"✅ Decision response: {result['response'][:50]}...")
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    print("Running graph tests...\n")
    test_chat_flow()
    test_habit_flow()
    test_decision_flow()
    print("\n🎉 All tests passed!")
