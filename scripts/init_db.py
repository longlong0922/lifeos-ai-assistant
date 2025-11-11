"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Database
from configs.settings import get_settings


def init_database():
    """初始化数据库"""
    settings = get_settings()
    print(f"Initializing database at: {settings.DB_PATH}")
    
    # 创建数据库实例（会自动初始化表）
    db = Database(settings.DB_PATH)
    print("✅ Database initialized successfully!")
    
    # 创建测试用户
    try:
        user_id = db.create_user(username="test_user", timezone="Asia/Shanghai")
        print(f"✅ Created test user with ID: {user_id}")
        
        # 创建示例习惯
        habit_id = db.create_habit(
            user_id=user_id,
            name="每天跑步30分钟",
            description="保持健康的身体",
            target_frequency="daily"
        )
        print(f"✅ Created sample habit with ID: {habit_id}")
        
    except Exception as e:
        print(f"⚠️  Test user might already exist: {e}")
    
    print("\n🎉 Database setup complete!")
    print(f"Database location: {settings.DB_PATH}")
    print("\nYou can now start the server with:")
    print("  python app/main.py")


if __name__ == "__main__":
    init_database()
