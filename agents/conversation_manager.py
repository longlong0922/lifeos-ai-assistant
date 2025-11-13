"""
多轮对话管理系统
负责保存和检索对话历史，支持上下文理解
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class ConversationManager:
    """
    对话管理器 - 支持多轮对话和上下文记忆
    """
    
    def __init__(self, db_path: str = "lifeos_data.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                turn_number INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT,
                intent TEXT,
                intent_confidence REAL,
                extracted_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, turn_number)
            )
        """)
        
        # 会话元数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_turns INTEGER DEFAULT 0,
                session_summary TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_session 
            ON conversations(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user 
            ON conversations(user_id)
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: str, session_id: Optional[str] = None) -> str:
        """创建新会话"""
        if not session_id:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO sessions (session_id, user_id)
            VALUES (?, ?)
        """, (session_id, user_id))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def add_turn(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        assistant_message: str,
        intent: str,
        intent_confidence: float,
        extracted_data: Optional[Dict[str, Any]] = None
    ) -> int:
        """添加一轮对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取当前轮次
        cursor.execute("""
            SELECT COALESCE(MAX(turn_number), 0) + 1
            FROM conversations
            WHERE session_id = ?
        """, (session_id,))
        turn_number = cursor.fetchone()[0]
        
        # 插入对话
        cursor.execute("""
            INSERT INTO conversations 
            (session_id, user_id, turn_number, user_message, assistant_message, 
             intent, intent_confidence, extracted_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, user_id, turn_number, user_message, assistant_message,
            intent, intent_confidence, 
            json.dumps(extracted_data, ensure_ascii=False) if extracted_data else None
        ))
        
        # 更新会话元数据
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, user_id, last_active_at, total_turns)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
        """, (session_id, user_id, turn_number))
        
        conn.commit()
        conn.close()
        
        return turn_number
    
    def get_conversation_history(
        self, 
        session_id: str, 
        last_n_turns: int = 5
    ) -> List[Dict[str, Any]]:
        """获取对话历史"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT turn_number, user_message, assistant_message, intent, 
                   intent_confidence, extracted_data, created_at
            FROM conversations
            WHERE session_id = ?
            ORDER BY turn_number DESC
            LIMIT ?
        """, (session_id, last_n_turns))
        
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为列表并反转（最早的在前）
        history = []
        for row in reversed(rows):
            history.append({
                "turn_number": row["turn_number"],
                "user_message": row["user_message"],
                "assistant_message": row["assistant_message"],
                "intent": row["intent"],
                "intent_confidence": row["intent_confidence"],
                "extracted_data": json.loads(row["extracted_data"]) if row["extracted_data"] else None,
                "created_at": row["created_at"]
            })
        
        return history
    
    def build_context_summary(self, history: List[Dict[str, Any]]) -> str:
        """构建对话上下文摘要"""
        if not history:
            return "这是新对话的开始。"
        
        summary_parts = [f"历史对话共 {len(history)} 轮："]
        
        for turn in history[-3:]:  # 最近3轮
            summary_parts.append(
                f"- 用户: {turn['user_message'][:50]}... -> "
                f"意图: {turn['intent']}"
            )
        
        return "\n".join(summary_parts)
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT total_turns, started_at, last_active_at
            FROM sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {}
        
        # 统计意图分布
        cursor.execute("""
            SELECT intent, COUNT(*) as count
            FROM conversations
            WHERE session_id = ?
            GROUP BY intent
        """, (session_id,))
        
        intent_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_turns": row["total_turns"],
            "started_at": row["started_at"],
            "last_active_at": row["last_active_at"],
            "intent_distribution": intent_distribution
        }
    
    def search_similar_conversations(
        self, 
        user_id: str, 
        intent: str, 
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """搜索相似对话（用于个性化推荐）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, user_message, assistant_message, created_at
            FROM conversations
            WHERE user_id = ? AND intent = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, intent, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
