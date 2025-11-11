"""
API 端点测试
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data


def test_health_check():
    """测试健康检查"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_chat_endpoint():
    """测试聊天端点"""
    response = client.post(
        "/api/chat",
        json={
            "user_id": 1,
            "message": "你好",
            "session_id": "test_session"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0


def test_create_habit():
    """测试创建习惯"""
    response = client.post(
        "/api/habit",
        json={
            "user_id": 1,
            "name": "测试习惯",
            "description": "这是一个测试习惯"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "habit_id" in data


def test_get_user_habits():
    """测试获取用户习惯"""
    response = client.get("/api/habit/1")
    assert response.status_code == 200
    data = response.json()
    assert "habits" in data


def test_get_stats():
    """测试获取统计"""
    response = client.get("/api/stats/1")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "habits" in data


if __name__ == "__main__":
    print("Running API tests...\n")
    test_root()
    print("✅ Root endpoint test passed")
    
    test_health_check()
    print("✅ Health check test passed")
    
    test_chat_endpoint()
    print("✅ Chat endpoint test passed")
    
    test_create_habit()
    print("✅ Create habit test passed")
    
    test_get_user_habits()
    print("✅ Get habits test passed")
    
    test_get_stats()
    print("✅ Get stats test passed")
    
    print("\n🎉 All API tests passed!")
