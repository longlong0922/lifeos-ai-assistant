"""
个性化记忆模块 (Personalized Memory Module)
轻量级用户偏好与行为习惯存储

核心功能：
1. 用户画像存储（偏好、节奏、习惯）
2. 记忆类型管理（长期/短期/偏好/例行）
3. TTL 与过期策略
4. 隐私保护与删除
5. 记忆检索与应用
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path


class MemoryType(Enum):
    """记忆类型"""
    PREFERENCE = "preference"      # 用户偏好（如：早上效率高）
    ROUTINE = "routine"           # 例行习惯（如：每天9点开始工作）
    FACT = "fact"                 # 事实信息（如：住在北京）
    GOAL = "goal"                 # 目标（如：学习Python）
    PATTERN = "pattern"           # 行为模式（如：容易被社交媒体分心）
    CONSTRAINT = "constraint"     # 限制条件（如：晚上10点后不工作）


@dataclass
class Memory:
    """记忆条目"""
    memory_id: str
    user_id: str
    type: MemoryType
    key: str
    value: Any
    created_at: str
    last_used: str
    ttl_days: Optional[int] = None  # None 表示永久
    confidence: float = 1.0
    source: str = "user_input"  # user_input | inferred | system
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.type, str):
            self.type = MemoryType(self.type)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl_days is None:
            return False
        
        created = datetime.fromisoformat(self.created_at)
        now = datetime.now()
        return (now - created).days > self.ttl_days
    
    def should_archive(self, unused_days: int = 180) -> bool:
        """检查是否应该归档（长期未使用）"""
        last_used = datetime.fromisoformat(self.last_used)
        now = datetime.now()
        return (now - last_used).days > unused_days


# ============================================================================
# 用户画像 Schema
# ============================================================================

@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    
    # 时间偏好
    morning_productivity: bool = False  # 早上效率高
    evening_productivity: bool = False  # 晚上效率高
    preferred_work_hours: tuple = (9, 18)
    
    # 任务偏好
    prefers_short_tasks: bool = True
    planning_style: str = "simple"  # simple | detailed | visual
    needs_frequent_breaks: bool = False
    
    # 分心模式
    distracted_by_social: bool = False
    distracted_by_phone: bool = False
    
    # 目标
    long_term_goals: List[str] = None
    weekly_focus: str = ""
    
    # 沟通风格
    preferred_tone: str = "friendly"  # friendly | professional | casual
    language: str = "zh-CN"
    
    def __post_init__(self):
        if self.long_term_goals is None:
            self.long_term_goals = []
    
    @classmethod
    def from_memories(cls, user_id: str, memories: List[Memory]) -> 'UserProfile':
        """从记忆列表构建用户画像"""
        profile = cls(user_id=user_id)
        
        for mem in memories:
            if mem.type == MemoryType.PREFERENCE:
                if mem.key == "morning_productivity":
                    profile.morning_productivity = bool(mem.value)
                elif mem.key == "evening_productivity":
                    profile.evening_productivity = bool(mem.value)
                elif mem.key == "prefers_short_tasks":
                    profile.prefers_short_tasks = bool(mem.value)
                elif mem.key == "planning_style":
                    profile.planning_style = str(mem.value)
                elif mem.key == "preferred_tone":
                    profile.preferred_tone = str(mem.value)
            
            elif mem.type == MemoryType.PATTERN:
                if mem.key == "distracted_by_social":
                    profile.distracted_by_social = bool(mem.value)
                elif mem.key == "distracted_by_phone":
                    profile.distracted_by_phone = bool(mem.value)
            
            elif mem.type == MemoryType.GOAL:
                profile.long_term_goals.append(str(mem.value))
        
        return profile


# ============================================================================
# Memory Store (SQLite Implementation)
# ============================================================================

class MemoryStore:
    """记忆存储（基于 SQLite）"""
    
    def __init__(self, db_path: str = "lifeos_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used TEXT NOT NULL,
                    ttl_days INTEGER,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'user_input',
                    metadata TEXT,
                    UNIQUE(user_id, type, key)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON memories(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_used ON memories(last_used)")
    
    def add_memory(self, memory: Memory) -> bool:
        """添加或更新记忆"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (memory_id, user_id, type, key, value, created_at, last_used, 
                     ttl_days, confidence, source, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.memory_id,
                    memory.user_id,
                    memory.type.value,
                    memory.key,
                    json.dumps(memory.value, ensure_ascii=False),
                    memory.created_at,
                    memory.last_used,
                    memory.ttl_days,
                    memory.confidence,
                    memory.source,
                    json.dumps(memory.metadata, ensure_ascii=False)
                ))
            return True
        except Exception as e:
            print(f"添加记忆失败: {e}")
            return False
    
    def get_memory(self, user_id: str, key: str) -> Optional[Memory]:
        """获取特定记忆"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM memories WHERE user_id = ? AND key = ?",
                (user_id, key)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_memory(row)
        return None
    
    def get_memories(
        self, 
        user_id: str, 
        memory_type: Optional[MemoryType] = None,
        limit: int = 100
    ) -> List[Memory]:
        """获取用户的记忆列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if memory_type:
                cursor = conn.execute(
                    """SELECT * FROM memories 
                       WHERE user_id = ? AND type = ? 
                       ORDER BY last_used DESC LIMIT ?""",
                    (user_id, memory_type.value, limit)
                )
            else:
                cursor = conn.execute(
                    """SELECT * FROM memories 
                       WHERE user_id = ? 
                       ORDER BY last_used DESC LIMIT ?""",
                    (user_id, limit)
                )
            
            return [self._row_to_memory(row) for row in cursor.fetchall()]
    
    def update_last_used(self, memory_id: str):
        """更新最后使用时间"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE memories SET last_used = ? WHERE memory_id = ?",
                (datetime.now().isoformat(), memory_id)
            )
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
            return True
        except Exception as e:
            print(f"删除记忆失败: {e}")
            return False
    
    def delete_all_user_memories(self, user_id: str) -> bool:
        """删除用户所有记忆（"忘记我"功能）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            print(f"删除用户记忆失败: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """清理过期记忆"""
        count = 0
        memories = self.get_all_memories()
        
        for mem in memories:
            if mem.is_expired():
                if self.delete_memory(mem.memory_id):
                    count += 1
        
        return count
    
    def archive_unused(self, unused_days: int = 180) -> int:
        """归档长期未使用的记忆"""
        count = 0
        memories = self.get_all_memories()
        
        for mem in memories:
            if mem.should_archive(unused_days):
                # 可以移到归档表或直接删除
                if self.delete_memory(mem.memory_id):
                    count += 1
        
        return count
    
    def get_all_memories(self) -> List[Memory]:
        """获取所有记忆（用于维护任务）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM memories")
            return [self._row_to_memory(row) for row in cursor.fetchall()]
    
    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        """将数据库行转换为 Memory 对象"""
        return Memory(
            memory_id=row['memory_id'],
            user_id=row['user_id'],
            type=MemoryType(row['type']),
            key=row['key'],
            value=json.loads(row['value']),
            created_at=row['created_at'],
            last_used=row['last_used'],
            ttl_days=row['ttl_days'],
            confidence=row['confidence'],
            source=row['source'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )


# ============================================================================
# Memory Manager (High-level API)
# ============================================================================

class MemoryManager:
    """记忆管理器（高级 API）"""
    
    def __init__(self, store: MemoryStore):
        self.store = store
    
    def remember(
        self, 
        user_id: str, 
        key: str, 
        value: Any,
        memory_type: MemoryType = MemoryType.PREFERENCE,
        ttl_days: Optional[int] = None,
        source: str = "user_input"
    ) -> Memory:
        """记住一个信息"""
        import uuid
        
        memory = Memory(
            memory_id=str(uuid.uuid4()),
            user_id=user_id,
            type=memory_type,
            key=key,
            value=value,
            created_at=datetime.now().isoformat(),
            last_used=datetime.now().isoformat(),
            ttl_days=ttl_days,
            source=source
        )
        
        self.store.add_memory(memory)
        return memory
    
    def recall(self, user_id: str, key: str) -> Optional[Any]:
        """回忆一个信息"""
        memory = self.store.get_memory(user_id, key)
        if memory:
            self.store.update_last_used(memory.memory_id)
            return memory.value
        return None
    
    def forget(self, user_id: str, key: str) -> bool:
        """忘记一个信息"""
        memory = self.store.get_memory(user_id, key)
        if memory:
            return self.store.delete_memory(memory.memory_id)
        return False
    
    def forget_all(self, user_id: str) -> bool:
        """忘记用户所有信息"""
        return self.store.delete_all_user_memories(user_id)
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """获取用户画像"""
        memories = self.store.get_memories(user_id)
        return UserProfile.from_memories(user_id, memories)
    
    def infer_and_remember(
        self, 
        user_id: str, 
        key: str, 
        value: Any,
        confidence: float = 0.7
    ) -> Memory:
        """推断并记住（低置信度，可被用户纠正）"""
        import uuid
        
        memory = Memory(
            memory_id=str(uuid.uuid4()),
            user_id=user_id,
            type=MemoryType.PATTERN,
            key=key,
            value=value,
            created_at=datetime.now().isoformat(),
            last_used=datetime.now().isoformat(),
            ttl_days=90,  # 推断的记忆 90 天后过期
            confidence=confidence,
            source="inferred"
        )
        
        self.store.add_memory(memory)
        return memory
    
    def get_relevant_memories(
        self, 
        user_id: str, 
        context: str,
        limit: int = 5
    ) -> List[Memory]:
        """获取与当前上下文相关的记忆"""
        all_memories = self.store.get_memories(user_id, limit=100)
        
        # 简单的相关性过滤（可以用向量搜索优化）
        relevant = []
        context_lower = context.lower()
        
        for mem in all_memories:
            # 检查 key 或 value 是否包含上下文关键词
            if (context_lower in mem.key.lower() or 
                context_lower in str(mem.value).lower()):
                self.store.update_last_used(mem.memory_id)
                relevant.append(mem)
                if len(relevant) >= limit:
                    break
        
        return relevant


# ============================================================================
# 常用记忆模板
# ============================================================================

COMMON_MEMORY_TEMPLATES = {
    "morning_productivity": {
        "type": MemoryType.PREFERENCE,
        "description": "用户早上效率高",
        "example_values": [True, False]
    },
    "evening_productivity": {
        "type": MemoryType.PREFERENCE,
        "description": "用户晚上效率高",
        "example_values": [True, False]
    },
    "prefers_short_tasks": {
        "type": MemoryType.PREFERENCE,
        "description": "偏好短任务",
        "example_values": [True, False]
    },
    "planning_style": {
        "type": MemoryType.PREFERENCE,
        "description": "计划风格",
        "example_values": ["simple", "detailed", "visual"]
    },
    "distracted_by_social": {
        "type": MemoryType.PATTERN,
        "description": "容易被社交媒体分心",
        "example_values": [True, False]
    },
    "work_location": {
        "type": MemoryType.FACT,
        "description": "工作地点",
        "example_values": ["home", "office", "hybrid"]
    }
}


# ============================================================================
# 隐私与合规
# ============================================================================

@dataclass
class PrivacySettings:
    """隐私设置"""
    user_id: str
    allow_memory_storage: bool = True
    allow_pattern_inference: bool = True
    auto_delete_after_days: Optional[int] = None
    sensitive_topics: List[str] = None  # 不记忆的主题
    
    def __post_init__(self):
        if self.sensitive_topics is None:
            self.sensitive_topics = ["health", "finance", "legal"]


def is_sensitive_memory(memory: Memory, settings: PrivacySettings) -> bool:
    """检查记忆是否敏感"""
    for topic in settings.sensitive_topics:
        if topic.lower() in memory.key.lower():
            return True
    return False


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    import tempfile
    import os
    
    # 使用临时数据库测试
    temp_db = tempfile.mktemp(suffix=".db")
    
    try:
        print("🧪 测试记忆模块\n")
        
        # 初始化
        store = MemoryStore(temp_db)
        manager = MemoryManager(store)
        
        user_id = "test_user_001"
        
        # 1. 添加记忆
        print("1️⃣ 添加用户偏好...")
        manager.remember(user_id, "morning_productivity", True, MemoryType.PREFERENCE)
        manager.remember(user_id, "prefers_short_tasks", True, MemoryType.PREFERENCE)
        manager.remember(user_id, "planning_style", "simple", MemoryType.PREFERENCE)
        print("   ✅ 已添加 3 条偏好\n")
        
        # 2. 添加目标
        print("2️⃣ 添加长期目标...")
        manager.remember(user_id, "learn_python", "学习Python数据分析", MemoryType.GOAL)
        print("   ✅ 已添加目标\n")
        
        # 3. 推断行为模式
        print("3️⃣ 推断行为模式...")
        manager.infer_and_remember(user_id, "distracted_by_social", True, confidence=0.75)
        print("   ✅ 已推断并记录\n")
        
        # 4. 回忆
        print("4️⃣ 回忆用户偏好...")
        morning = manager.recall(user_id, "morning_productivity")
        print(f"   早上效率高: {morning}")
        planning = manager.recall(user_id, "planning_style")
        print(f"   计划风格: {planning}\n")
        
        # 5. 获取用户画像
        print("5️⃣ 生成用户画像...")
        profile = manager.get_user_profile(user_id)
        print(f"   早上效率高: {profile.morning_productivity}")
        print(f"   偏好短任务: {profile.prefers_short_tasks}")
        print(f"   计划风格: {profile.planning_style}")
        print(f"   容易被社交分心: {profile.distracted_by_social}")
        print(f"   长期目标: {profile.long_term_goals}\n")
        
        # 6. 获取所有记忆
        print("6️⃣ 获取所有记忆...")
        all_memories = store.get_memories(user_id)
        print(f"   共 {len(all_memories)} 条记忆:")
        for mem in all_memories:
            print(f"   - [{mem.type.value}] {mem.key}: {mem.value} (置信度: {mem.confidence})")
        print()
        
        # 7. 测试"忘记我"
        print("7️⃣ 测试删除功能...")
        manager.forget(user_id, "distracted_by_social")
        remaining = store.get_memories(user_id)
        print(f"   删除一条后剩余: {len(remaining)} 条\n")
        
        print("✅ 所有测试通过！")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_db):
            os.remove(temp_db)
            print(f"\n🧹 已清理临时数据库")
