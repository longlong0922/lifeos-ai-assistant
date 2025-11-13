"""
完整工具集 - 覆盖 LifeOS 全场景
"""

from typing import Type, List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
import json
from datetime import datetime, timedelta

from modules.memory import MemoryManager, MemoryStore
from agents.conversation_manager import ConversationManager


# =============================================================================
# 输入模型
# =============================================================================

class HabitInput(BaseModel):
    """习惯管理输入"""
    user_id: str = Field(description="用户ID")
    habit_name: str = Field(description="习惯名称")
    action: str = Field(description="操作: create/checkin/query/stats", default="query")
    target_frequency: Optional[str] = Field(description="目标频率，如'每天'、'每周3次'", default=None)


class GoalInput(BaseModel):
    """目标管理输入"""
    user_id: str = Field(description="用户ID")
    goal_title: str = Field(description="目标标题")
    action: str = Field(description="操作: create/update/query/breakdown", default="query")
    deadline: Optional[str] = Field(description="截止日期", default=None)


class ReflectionInput(BaseModel):
    """反思记录输入"""
    user_id: str = Field(description="用户ID")
    period: str = Field(description="反思周期: daily/weekly/monthly")
    content: Optional[str] = Field(description="反思内容", default=None)


class StatsInput(BaseModel):
    """数据统计输入"""
    user_id: str = Field(description="用户ID")
    stat_type: str = Field(description="统计类型: tasks/habits/goals/overall")
    time_range: str = Field(description="时间范围: today/week/month", default="week")


# =============================================================================
# 1. 习惯追踪工具
# =============================================================================

class HabitTrackingTool(BaseTool):
    """习惯追踪和管理工具"""
    name: str = "habit_tracker"
    description: str = """管理用户习惯：
    - create: 创建新习惯
    - checkin: 打卡记录
    - query: 查询习惯状态
    - stats: 统计坚持情况
    
    输入：用户ID、习惯名称、操作类型
    输出：习惯详情或统计数据"""
    
    args_schema: Type[BaseModel] = HabitInput
    db_path: str = "lifeos_data.db"  # 声明字段
    
    def __init__(self, db_path: str = "lifeos_data.db"):
        super().__init__()
        self.db_path = db_path
        self._init_habits_table()
    
    def _init_habits_table(self):
        """初始化习惯表"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                habit_name TEXT NOT NULL,
                target_frequency TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, habit_name)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                checkin_date DATE NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits(id),
                UNIQUE(habit_id, checkin_date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _run(
        self,
        user_id: str,
        habit_name: str,
        action: str = "query",
        target_frequency: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行习惯操作"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if action == "create":
                cursor.execute("""
                    INSERT OR IGNORE INTO habits (user_id, habit_name, target_frequency)
                    VALUES (?, ?, ?)
                """, (user_id, habit_name, target_frequency))
                conn.commit()
                return json.dumps({
                    "status": "success",
                    "message": f"习惯「{habit_name}」创建成功",
                    "target": target_frequency
                }, ensure_ascii=False)
            
            elif action == "checkin":
                # 获取习惯ID
                cursor.execute("""
                    SELECT id FROM habits WHERE user_id = ? AND habit_name = ?
                """, (user_id, habit_name))
                habit = cursor.fetchone()
                
                if not habit:
                    return json.dumps({"error": "习惯不存在"}, ensure_ascii=False)
                
                habit_id = habit[0]
                today = datetime.now().date()
                
                cursor.execute("""
                    INSERT OR IGNORE INTO habit_checkins (habit_id, checkin_date)
                    VALUES (?, ?)
                """, (habit_id, today))
                conn.commit()
                
                # 计算连续天数
                cursor.execute("""
                    SELECT COUNT(*) FROM habit_checkins
                    WHERE habit_id = ? AND checkin_date >= date('now', '-7 days')
                """, (habit_id,))
                last_7_days = cursor.fetchone()[0]
                
                return json.dumps({
                    "status": "success",
                    "message": f"✅ {habit_name} 打卡成功！",
                    "last_7_days": last_7_days,
                    "encouragement": "继续保持！" if last_7_days >= 3 else "加油，坚持下去！"
                }, ensure_ascii=False)
            
            elif action == "stats":
                cursor.execute("""
                    SELECT h.habit_name, h.target_frequency,
                           COUNT(hc.id) as total_checkins,
                           MAX(hc.checkin_date) as last_checkin
                    FROM habits h
                    LEFT JOIN habit_checkins hc ON h.id = hc.habit_id
                    WHERE h.user_id = ? AND h.habit_name = ?
                    GROUP BY h.id
                """, (user_id, habit_name))
                
                row = cursor.fetchone()
                if not row:
                    return json.dumps({"error": "习惯不存在"}, ensure_ascii=False)
                
                return json.dumps({
                    "habit_name": row[0],
                    "target": row[1],
                    "total_checkins": row[2],
                    "last_checkin": row[3],
                    "status": "活跃" if row[3] == str(datetime.now().date()) else "待打卡"
                }, ensure_ascii=False)
            
            else:  # query
                cursor.execute("""
                    SELECT habit_name, target_frequency, created_at
                    FROM habits
                    WHERE user_id = ?
                """, (user_id,))
                
                habits = cursor.fetchall()
                return json.dumps({
                    "total": len(habits),
                    "habits": [
                        {"name": h[0], "target": h[1], "created": h[2]}
                        for h in habits
                    ]
                }, ensure_ascii=False)
        
        finally:
            conn.close()


# =============================================================================
# 2. 目标管理工具
# =============================================================================

class GoalManagementTool(BaseTool):
    """目标设定和追踪工具"""
    name: str = "goal_manager"
    description: str = """管理用户目标：
    - create: 创建新目标
    - update: 更新进度
    - breakdown: 拆解目标为里程碑
    - query: 查询目标状态
    
    输入：用户ID、目标标题、操作类型
    输出：目标详情或拆解计划"""
    
    args_schema: Type[BaseModel] = GoalInput
    db_path: str = "lifeos_data.db"  # 声明字段
    
    def __init__(self, db_path: str = "lifeos_data.db"):
        super().__init__()
        self.db_path = db_path
        self._init_goals_table()
    
    def _init_goals_table(self):
        """初始化目标表"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                deadline DATE,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                milestone_title TEXT NOT NULL,
                deadline DATE,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _run(
        self,
        user_id: str,
        goal_title: str,
        action: str = "query",
        deadline: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行目标操作"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if action == "create":
                cursor.execute("""
                    INSERT INTO goals (user_id, title, deadline)
                    VALUES (?, ?, ?)
                """, (user_id, goal_title, deadline))
                conn.commit()
                
                return json.dumps({
                    "status": "success",
                    "message": f"🎯 目标「{goal_title}」已创建",
                    "deadline": deadline,
                    "tip": "建议将目标拆解为3-5个里程碑"
                }, ensure_ascii=False)
            
            elif action == "breakdown":
                # 这里可以集成 LLM 来自动生成里程碑
                # 简化版：返回建议结构
                return json.dumps({
                    "goal": goal_title,
                    "suggested_milestones": [
                        {"title": "阶段1：基础准备", "timeline": "第1-2周"},
                        {"title": "阶段2：核心推进", "timeline": "第3-6周"},
                        {"title": "阶段3：冲刺收尾", "timeline": "第7-8周"}
                    ],
                    "first_step": "今天就可以开始准备基础材料"
                }, ensure_ascii=False)
            
            else:  # query
                cursor.execute("""
                    SELECT title, deadline, status, progress, created_at
                    FROM goals
                    WHERE user_id = ? AND status = 'active'
                """, (user_id,))
                
                goals = cursor.fetchall()
                return json.dumps({
                    "active_goals": len(goals),
                    "goals": [
                        {
                            "title": g[0],
                            "deadline": g[1],
                            "status": g[2],
                            "progress": f"{g[3]}%",
                            "created": g[4]
                        }
                        for g in goals
                    ]
                }, ensure_ascii=False)
        
        finally:
            conn.close()


# =============================================================================
# 3. 反思记录工具
# =============================================================================

class ReflectionTool(BaseTool):
    """反思和总结工具"""
    name: str = "reflection_recorder"
    description: str = """记录用户的反思和总结：
    - 每日反思
    - 每周回顾
    - 每月总结
    
    输入：用户ID、周期、反思内容
    输出：反思记录或历史反思"""
    
    args_schema: Type[BaseModel] = ReflectionInput
    db_path: str = "lifeos_data.db"  # 声明字段
    
    def __init__(self, db_path: str = "lifeos_data.db"):
        super().__init__()
        self.db_path = db_path
        self._init_reflections_table()
    
    def _init_reflections_table(self):
        """初始化反思表"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                period TEXT NOT NULL,
                content TEXT,
                insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _run(
        self,
        user_id: str,
        period: str,
        content: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """记录反思"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if content:
                # 保存反思
                cursor.execute("""
                    INSERT INTO reflections (user_id, period, content)
                    VALUES (?, ?, ?)
                """, (user_id, period, content))
                conn.commit()
                
                return json.dumps({
                    "status": "success",
                    "message": f"📝 {period} 反思已保存"
                }, ensure_ascii=False)
            else:
                # 查询历史反思
                cursor.execute("""
                    SELECT period, content, created_at
                    FROM reflections
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (user_id,))
                
                reflections = cursor.fetchall()
                return json.dumps({
                    "recent_reflections": [
                        {"period": r[0], "content": r[1][:100], "date": r[2]}
                        for r in reflections
                    ]
                }, ensure_ascii=False)
        
        finally:
            conn.close()


# =============================================================================
# 4. 数据统计工具
# =============================================================================

class DataStatsTool(BaseTool):
    """数据统计和可视化工具"""
    name: str = "data_analytics"
    description: str = """生成用户数据统计：
    - 任务完成率
    - 习惯坚持率
    - 目标进度
    - 整体表现
    
    输入：用户ID、统计类型、时间范围
    输出：统计数据和洞察"""
    
    args_schema: Type[BaseModel] = StatsInput
    db_path: str = "lifeos_data.db"  # 声明字段
    
    def __init__(self, db_path: str = "lifeos_data.db"):
        super().__init__()
        self.db_path = db_path
    
    def _run(
        self,
        user_id: str,
        stat_type: str,
        time_range: str = "week",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """生成统计数据"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 时间范围过滤
            if time_range == "today":
                time_filter = "date('now')"
            elif time_range == "week":
                time_filter = "date('now', '-7 days')"
            else:  # month
                time_filter = "date('now', '-30 days')"
            
            if stat_type == "habits":
                cursor.execute(f"""
                    SELECT h.habit_name, COUNT(hc.id) as checkins
                    FROM habits h
                    LEFT JOIN habit_checkins hc ON h.id = hc.habit_id
                        AND hc.checkin_date >= {time_filter}
                    WHERE h.user_id = ?
                    GROUP BY h.id
                """, (user_id,))
                
                habits = cursor.fetchall()
                return json.dumps({
                    "period": time_range,
                    "habit_stats": [
                        {"habit": h[0], "checkins": h[1]}
                        for h in habits
                    ],
                    "insight": "本周坚持最好的是：" + (habits[0][0] if habits else "暂无数据")
                }, ensure_ascii=False)
            
            elif stat_type == "overall":
                # 综合统计
                cursor.execute("SELECT COUNT(*) FROM habits WHERE user_id = ?", (user_id,))
                total_habits = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id = ? AND status = 'active'", (user_id,))
                active_goals = cursor.fetchone()[0]
                
                return json.dumps({
                    "summary": {
                        "total_habits": total_habits,
                        "active_goals": active_goals,
                        "user_level": "进阶" if total_habits > 3 else "新手"
                    },
                    "encouragement": "你已经建立了良好的成长习惯！"
                }, ensure_ascii=False)
            
            else:
                return json.dumps({"error": "不支持的统计类型"}, ensure_ascii=False)
        
        finally:
            conn.close()


# =============================================================================
# 工具注册函数
# =============================================================================

def get_complete_tools(db_path: str = "lifeos_data.db") -> List[BaseTool]:
    """获取完整工具集"""
    return [
        HabitTrackingTool(db_path),
        GoalManagementTool(db_path),
        ReflectionTool(db_path),
        DataStatsTool(db_path)
    ]
