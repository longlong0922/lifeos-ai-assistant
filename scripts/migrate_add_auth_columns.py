"""
数据库迁移脚本 - 添加认证相关字段
"""
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings

settings = get_settings()
db_path = settings.DB_PATH

def migrate_database():
    """添加认证相关字段到 users 表"""
    print(f"开始迁移数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前 users 表的列: {columns}")
        
        # 添加缺失的列
        migrations = []
        
        if 'password_hash' not in columns:
            migrations.append(("password_hash", "ALTER TABLE users ADD COLUMN password_hash TEXT"))
        
        if 'email' not in columns:
            migrations.append(("email", "ALTER TABLE users ADD COLUMN email TEXT"))
        
        if 'is_new_user' not in columns:
            migrations.append(("is_new_user", "ALTER TABLE users ADD COLUMN is_new_user BOOLEAN DEFAULT 1"))
        
        if 'onboarding_completed' not in columns:
            migrations.append(("onboarding_completed", "ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0"))
        
        if 'last_login' not in columns:
            migrations.append(("last_login", "ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))
        
        # 执行迁移
        if migrations:
            print(f"\n需要添加 {len(migrations)} 个列:")
            for col_name, sql in migrations:
                print(f"  - 添加列: {col_name}")
                cursor.execute(sql)
            
            conn.commit()
            print("\n✅ 数据库迁移完成!")
        else:
            print("\n✅ 数据库已是最新版本,无需迁移")
        
        # 显示更新后的列
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\n更新后的 users 表列: {columns}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
