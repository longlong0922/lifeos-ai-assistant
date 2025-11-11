"""
数据库操作封装 - SQLite
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/lifeos.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    email TEXT UNIQUE,
                    is_new_user BOOLEAN DEFAULT 1,
                    onboarding_completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    timezone TEXT DEFAULT 'Asia/Shanghai',
                    preferences TEXT DEFAULT '{}'
                )
            """)
            
            # 习惯表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    target_frequency TEXT DEFAULT 'daily',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 习惯记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habit_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    date TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    context TEXT,
                    ai_feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (habit_id) REFERENCES habits(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 反思记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TIMESTAMP NOT NULL,
                    conversation TEXT NOT NULL,
                    insights TEXT,
                    patterns TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 决策记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    factors TEXT NOT NULL,
                    recommendation TEXT,
                    user_choice TEXT,
                    outcome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 目标表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    deadline TIMESTAMP,
                    milestones TEXT DEFAULT '[]',
                    daily_tasks TEXT DEFAULT '[]',
                    progress REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 每日简报表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_briefs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TIMESTAMP NOT NULL,
                    energy_prediction REAL,
                    key_focuses TEXT NOT NULL,
                    risk_alerts TEXT NOT NULL,
                    encouragement TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # 聊天历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
    
    # ==================== 用户相关 ====================
    
    def create_user(self, username: str, timezone: str = "Asia/Shanghai") -> int:
        """创建用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, timezone) VALUES (?, ?)",
                (username, timezone)
            )
            return cursor.lastrowid
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    # ==================== 习惯相关 ====================
    
    def create_habit(self, user_id: int, name: str, description: str = None, 
                     target_frequency: str = "daily") -> int:
        """创建习惯"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO habits (user_id, name, description, target_frequency) VALUES (?, ?, ?, ?)",
                (user_id, name, description, target_frequency)
            )
            return cursor.lastrowid
    
    def get_user_habits(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """获取用户的习惯列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM habits WHERE user_id = ?"
            if active_only:
                query += " AND is_active = 1"
            cursor.execute(query, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_habit_record(self, habit_id: int, user_id: int, date: datetime, 
                        status: str, context: str = None) -> int:
        """添加习惯记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO habit_records (habit_id, user_id, date, status, context) VALUES (?, ?, ?, ?, ?)",
                (habit_id, user_id, date, status, context)
            )
            return cursor.lastrowid
    
    def get_habit_records(self, habit_id: int, limit: int = 30) -> List[Dict]:
        """获取习惯记录（最近N天）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM habit_records WHERE habit_id = ? ORDER BY date DESC LIMIT ?",
                (habit_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_habit_record_feedback(self, record_id: int, ai_feedback: str):
        """更新习惯记录的 AI 反馈"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE habit_records SET ai_feedback = ? WHERE id = ?",
                (ai_feedback, record_id)
            )
    
    def update_habit(self, habit_id: int, name: str = None, description: str = None, 
                     target_frequency: str = None) -> bool:
        """更新习惯信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if target_frequency is not None:
                updates.append("target_frequency = ?")
                params.append(target_frequency)
            
            if not updates:
                return False
            
            params.append(habit_id)
            query = f"UPDATE habits SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_habit(self, habit_id: int, soft_delete: bool = True) -> bool:
        """删除习惯（支持软删除和硬删除）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if soft_delete:
                # 软删除：标记为不活跃
                cursor.execute("UPDATE habits SET is_active = 0 WHERE id = ?", (habit_id,))
            else:
                # 硬删除：物理删除记录
                cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            return cursor.rowcount > 0
    
    # ==================== 反思相关 ====================
    
    def save_reflection(self, user_id: int, date: datetime, conversation: List[Dict],
                       insights: str = None, patterns: List[str] = None) -> int:
        """保存反思记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reflections (user_id, date, conversation, insights, patterns) VALUES (?, ?, ?, ?, ?)",
                (user_id, date, json.dumps(conversation, ensure_ascii=False), 
                 insights, json.dumps(patterns or [], ensure_ascii=False))
            )
            return cursor.lastrowid
    
    def get_recent_reflections(self, user_id: int, limit: int = 10) -> List[Dict]:
        """获取最近的反思记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM reflections WHERE user_id = ? ORDER BY date DESC LIMIT ?",
                (user_id, limit)
            )
            rows = [dict(row) for row in cursor.fetchall()]
            for row in rows:
                row['conversation'] = json.loads(row['conversation'])
                if row['patterns']:
                    row['patterns'] = json.loads(row['patterns'])
            return rows
    
    # ==================== 决策相关 ====================
    
    def save_decision(self, user_id: int, question: str, factors: List[Dict],
                     recommendation: str = None) -> int:
        """保存决策记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO decisions (user_id, question, factors, recommendation) VALUES (?, ?, ?, ?)",
                (user_id, question, json.dumps(factors, ensure_ascii=False), recommendation)
            )
            return cursor.lastrowid
    
    # ==================== 目标相关 ====================
    
    def create_goal(self, user_id: int, title: str, description: str,
                   deadline: datetime = None, milestones: List[Dict] = None,
                   daily_tasks: List[str] = None) -> int:
        """创建目标"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO goals (user_id, title, description, deadline, milestones, daily_tasks) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, title, description, deadline,
                 json.dumps(milestones or [], ensure_ascii=False),
                 json.dumps(daily_tasks or [], ensure_ascii=False))
            )
            return cursor.lastrowid
    
    def get_user_goals(self, user_id: int, status: str = "active") -> List[Dict]:
        """获取用户目标"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM goals WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                (user_id, status)
            )
            rows = [dict(row) for row in cursor.fetchall()]
            for row in rows:
                row['milestones'] = json.loads(row['milestones'])
                row['daily_tasks'] = json.loads(row['daily_tasks'])
            return rows
    
    # ==================== 每日简报相关 ====================
    
    def save_daily_brief(self, user_id: int, date: datetime, energy_prediction: float,
                        key_focuses: List[Dict], risk_alerts: List[str], encouragement: str) -> int:
        """保存每日简报"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO daily_briefs (user_id, date, energy_prediction, key_focuses, risk_alerts, encouragement) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, date, energy_prediction,
                 json.dumps(key_focuses, ensure_ascii=False),
                 json.dumps(risk_alerts, ensure_ascii=False),
                 encouragement)
            )
            return cursor.lastrowid
    
    def get_daily_brief(self, user_id: int, date: datetime) -> Optional[Dict]:
        """获取指定日期的简报"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM daily_briefs WHERE user_id = ? AND DATE(date) = DATE(?) ORDER BY created_at DESC LIMIT 1",
                (user_id, date)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['key_focuses'] = json.loads(result['key_focuses'])
                result['risk_alerts'] = json.loads(result['risk_alerts'])
                return result
            return None
    
    # ==================== 聊天历史相关 ====================
    
    def save_chat_message(self, user_id: int, role: str, content: str,
                         session_id: str = None, metadata: Dict = None) -> int:
        """保存聊天消息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, session_id, role, content, metadata) VALUES (?, ?, ?, ?, ?)",
                (user_id, session_id, role, content, 
                 json.dumps(metadata or {}, ensure_ascii=False))
            )
            return cursor.lastrowid
    
    def get_chat_history(self, user_id: int, session_id: str = None, limit: int = 50) -> List[Dict]:
        """获取聊天历史"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute(
                    "SELECT * FROM chat_history WHERE user_id = ? AND session_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (user_id, session_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (user_id, limit)
                )
            rows = [dict(row) for row in cursor.fetchall()]
            for row in rows:
                if row['metadata']:
                    row['metadata'] = json.loads(row['metadata'])
            return list(reversed(rows))  # 时间正序

    # ==================== 用户认证相关方法 ====================
    
    def create_user_with_password(self, username: str, password_hash: str, email: str = None, timezone: str = 'Asia/Shanghai') -> int:
        """创建用户(带密码)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (username, password_hash, email, timezone, is_new_user) VALUES (?, ?, ?, ?, 1)''',
                (username, password_hash, email, timezone)
            )
            return cursor.lastrowid
    
    def get_user_by_username(self, username: str):
        """通过用户名获取用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_email(self, email: str):
        """通过邮箱获取用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_last_login(self, user_id: int):
        """更新最后登录时间"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
    
    def mark_onboarding_completed(self, user_id: int):
        """标记新手引导完成"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_new_user = 0, onboarding_completed = 1 WHERE id = ?', (user_id,))
    
    def is_new_user(self, user_id: int) -> bool:
        """检查是否为新用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT is_new_user FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return bool(row['is_new_user']) if row else False
