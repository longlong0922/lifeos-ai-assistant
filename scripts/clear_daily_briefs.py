"""
清除已保存的每日简报，让系统重新生成
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

def clear_daily_briefs():
    """清除所有每日简报记录"""
    print(f"连接数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询当前记录数
        cursor.execute("SELECT COUNT(*) FROM daily_briefs")
        count = cursor.fetchone()[0]
        print(f"当前有 {count} 条每日简报记录")
        
        if count > 0:
            # 清空表
            cursor.execute("DELETE FROM daily_briefs")
            conn.commit()
            print(f"✅ 已清除所有每日简报记录")
        else:
            print("✅ 表中没有记录，无需清除")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("准备清除每日简报数据...")
    confirm = input("确认清除? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_daily_briefs()
        print("\n下次请求每日简报时，系统会基于你的实际习惯重新生成！")
    else:
        print("已取消")
