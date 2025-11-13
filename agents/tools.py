"""
LangChain Tools - 智能体工具集
每个工具封装一个特定能力
"""

from typing import Type, List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field
import json
from datetime import datetime

from modules.memory import MemoryManager, MemoryStore


# =============================================================================
# 工具输入模型
# =============================================================================

class TaskAnalysisInput(BaseModel):
    """任务分析工具输入"""
    tasks: List[str] = Field(description="任务列表")
    user_context: Dict[str, Any] = Field(description="用户上下文", default={})


class PriorityInput(BaseModel):
    """优先级评估工具输入"""
    task: str = Field(description="任务描述")
    deadline: Optional[str] = Field(description="截止时间", default=None)
    importance_hint: Optional[int] = Field(description="重要性提示 (1-10)", default=None)


class TimeEstimationInput(BaseModel):
    """时间估算工具输入"""
    task: str = Field(description="任务描述")
    complexity: str = Field(description="复杂度: simple/medium/complex", default="medium")


class MemorySearchInput(BaseModel):
    """记忆搜索工具输入"""
    user_id: str = Field(description="用户ID")
    query: str = Field(description="搜索查询")


class ActionDecompositionInput(BaseModel):
    """行动拆解工具输入"""
    task: str = Field(description="任务描述")
    total_minutes: int = Field(description="预计总时长（分钟）")
    user_style: str = Field(description="用户风格", default="balanced")


# =============================================================================
# 1. 任务分析工具
# =============================================================================

class TaskAnalysisTool(BaseTool):
    """
    分析任务的重要性、紧急性、类别
    """
    name: str = "task_analyzer"
    description: str = """分析任务的属性：
    - 重要性 (1-10)
    - 紧急性 (1-10)
    - 类别 (work/personal/learning/health)
    - 预计耗时
    - 是否可延后
    
    输入：JSON 格式的任务列表和用户上下文
    输出：分析后的任务详情"""
    
    args_schema: Type[BaseModel] = TaskAnalysisInput
    
    def _run(
        self,
        tasks: List[str],
        user_context: Dict[str, Any] = {},
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行任务分析"""
        analyzed_tasks = []
        
        current_time = datetime.now()
        current_hour = current_time.hour
        
        for task_desc in tasks:
            # 基于规则的初步分析
            task_lower = task_desc.lower()
            
            # 判断紧急性
            urgency = 5  # 默认
            if any(word in task_lower for word in ['明天', '今天', '马上', '立即', '紧急']):
                urgency = 9
            elif any(word in task_lower for word in ['本周', '这周', '近期']):
                urgency = 7
            elif any(word in task_lower for word in ['下周', '月底']):
                urgency = 5
            
            # 判断重要性
            importance = 6  # 默认
            if any(word in task_lower for word in ['报告', '项目', '会议', '客户', '考试']):
                importance = 8
            elif any(word in task_lower for word in ['邮件', '回复', '查看']):
                importance = 5
            
            # 判断类别
            category = 'personal'
            if any(word in task_lower for word in ['工作', '项目', '会议', '报告', '客户']):
                category = 'work'
            elif any(word in task_lower for word in ['学习', '学', '练习', '教程']):
                category = 'learning'
            elif any(word in task_lower for word in ['运动', '健身', '健康']):
                category = 'health'
            
            # 估算时间
            estimated_minutes = 30  # 默认
            if any(word in task_lower for word in ['写', '做', '完成', '准备']):
                estimated_minutes = 60
            elif any(word in task_lower for word in ['回复', '查看', '确认']):
                estimated_minutes = 10
            elif any(word in task_lower for word in ['报告', '文档', '方案']):
                estimated_minutes = 120
            
            # 是否可延后
            can_defer = urgency < 7 and importance < 7
            
            # 生成理由
            if urgency >= 9:
                reason = f"时间紧迫，必须尽快完成"
            elif importance >= 8:
                reason = f"高重要性任务，优先处理"
            elif can_defer:
                reason = f"不紧急且重要性一般，可以延后"
            else:
                reason = f"正常优先级任务"
            
            analyzed_tasks.append({
                "description": task_desc,
                "category": category,
                "importance": importance,
                "urgency": urgency,
                "estimated_minutes": estimated_minutes,
                "can_defer": can_defer,
                "reason": reason
            })
        
        return json.dumps(analyzed_tasks, ensure_ascii=False, indent=2)


# =============================================================================
# 2. 优先级评估工具
# =============================================================================

class PriorityAssessmentTool(BaseTool):
    """
    评估单个任务的优先级
    """
    name: str = "priority_assessor"
    description: str = """评估任务优先级（1-10分）
    考虑因素：截止时间、重要性、影响范围
    输出：优先级分数和理由"""
    
    args_schema: Type[BaseModel] = PriorityInput
    
    def _run(
        self,
        task: str,
        deadline: Optional[str] = None,
        importance_hint: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """计算优先级分数"""
        score = 5  # 基础分
        
        # 截止时间加权
        if deadline:
            if '明天' in deadline or '今天' in deadline:
                score += 4
            elif '本周' in deadline:
                score += 2
        
        # 重要性提示
        if importance_hint:
            score = (score + importance_hint) / 2
        
        # 任务关键词加权
        task_lower = task.lower()
        if any(word in task_lower for word in ['客户', '老板', '领导']):
            score += 1
        if any(word in task_lower for word in ['紧急', '马上', '立即']):
            score += 2
        
        score = min(10, max(1, int(score)))
        
        result = {
            "task": task,
            "priority_score": score,
            "reasoning": f"基于时间紧迫性和任务重要性，评分为 {score}/10"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)


# =============================================================================
# 3. 时间估算工具
# =============================================================================

class TimeEstimationTool(BaseTool):
    """
    估算任务所需时间
    """
    name: str = "time_estimator"
    description: str = """估算任务完成时间（分钟）
    输入：任务描述、复杂度
    输出：预计时间和拆解建议"""
    
    args_schema: Type[BaseModel] = TimeEstimationInput
    
    def _run(
        self,
        task: str,
        complexity: str = "medium",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """估算时间"""
        task_lower = task.lower()
        
        # 基础时间
        base_time = {
            'simple': 15,
            'medium': 45,
            'complex': 120
        }.get(complexity, 45)
        
        # 根据关键词调整
        if any(word in task_lower for word in ['报告', '文档', '方案', '策划']):
            base_time = max(base_time, 90)
        elif any(word in task_lower for word in ['邮件', '回复', '确认']):
            base_time = min(base_time, 15)
        elif any(word in task_lower for word in ['会议', '讨论']):
            base_time = 60
        
        # 生成拆解建议
        if base_time > 60:
            suggestion = f"建议拆解成 {base_time // 30} 个 30 分钟的小块"
        else:
            suggestion = "可一次性完成"
        
        result = {
            "task": task,
            "estimated_minutes": base_time,
            "complexity": complexity,
            "decomposition_suggestion": suggestion
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)


# =============================================================================
# 4. 记忆搜索工具
# =============================================================================

class MemorySearchTool(BaseTool):
    """
    搜索用户历史偏好和习惯
    """
    name: str = "memory_searcher"
    description: str = """搜索用户的历史偏好、习惯、目标
    输入：用户ID、搜索查询
    输出：相关记忆"""
    
    args_schema: Type[BaseModel] = MemorySearchInput
    memory_manager: MemoryManager = None
    
    def __init__(self, db_path: str = "lifeos_data.db"):
        super().__init__()
        memory_store = MemoryStore(db_path)
        self.memory_manager = MemoryManager(memory_store)
    
    def _run(
        self,
        user_id: str,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """搜索记忆"""
        # 获取用户画像
        profile = self.memory_manager.get_user_profile(user_id)
        
        result = {
            "user_id": user_id,
            "morning_productivity": profile.morning_productivity,
            "evening_productivity": profile.evening_productivity,
            "prefers_short_tasks": profile.prefers_short_tasks,
            "long_term_goals": profile.long_term_goals,
            "work_style": profile.work_style or "未知"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)


# =============================================================================
# 5. 行动拆解工具
# =============================================================================

class ActionDecompositionTool(BaseTool):
    """
    将任务拆解成小步骤
    """
    name: str = "action_decomposer"
    description: str = """将大任务拆解成5分钟可启动的小步骤
    输入：任务、总时长、用户风格
    输出：拆解后的步骤列表"""
    
    args_schema: Type[BaseModel] = ActionDecompositionInput
    
    def _run(
        self,
        task: str,
        total_minutes: int,
        user_style: str = "balanced",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """拆解任务"""
        steps = []
        
        # 第一步：5分钟启动
        steps.append({
            "step_number": 1,
            "description": self._generate_quick_start(task),
            "estimated_minutes": 5,
            "difficulty": "easy",
            "expected_outcome": "完成初始设置，进入工作状态",
            "type": "immediate"
        })
        
        # 中间步骤
        remaining_time = total_minutes - 5
        num_steps = max(2, remaining_time // 30)
        
        for i in range(num_steps):
            steps.append({
                "step_number": i + 2,
                "description": f"完成{task}的第{i+1}部分",
                "estimated_minutes": min(30, remaining_time // num_steps),
                "difficulty": "medium",
                "expected_outcome": f"完成进度 {((i+1)/num_steps)*100:.0f}%",
                "type": "core"
            })
        
        # 最后一步：检查
        steps.append({
            "step_number": len(steps) + 1,
            "description": f"检查{task}的完整性",
            "estimated_minutes": 10,
            "difficulty": "easy",
            "expected_outcome": "确保质量无误",
            "type": "review"
        })
        
        result = {
            "task": task,
            "total_estimated_minutes": total_minutes,
            "steps": steps,
            "quick_start": steps[0]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def _generate_quick_start(self, task: str) -> str:
        """生成快速启动步骤"""
        task_lower = task.lower()
        
        if '写' in task_lower or '报告' in task_lower:
            return "打开文档，写下3个核心要点"
        elif '学' in task_lower:
            return "打开学习材料，浏览目录"
        elif '准备' in task_lower:
            return "列出需要准备的清单"
        elif '整理' in task_lower:
            return "新建文件夹，分类放置"
        else:
            return f"打开与'{task}'相关的工具/文档"


# =============================================================================
# 导出所有工具
# =============================================================================

def get_all_tools(db_path: str = "lifeos_data.db") -> List[BaseTool]:
    """获取所有工具实例"""
    return [
        TaskAnalysisTool(),
        PriorityAssessmentTool(),
        TimeEstimationTool(),
        MemorySearchTool(db_path),
        ActionDecompositionTool(),
    ]


__all__ = [
    'TaskAnalysisTool',
    'PriorityAssessmentTool',
    'TimeEstimationTool',
    'MemorySearchTool',
    'ActionDecompositionTool',
    'get_all_tools',
]
