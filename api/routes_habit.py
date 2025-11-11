"""
习惯和计划管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.database import Database
from configs.settings import get_settings

router = APIRouter(prefix="/api", tags=["habit"])

settings = get_settings()
db = Database(settings.DB_PATH)


# ==================== 请求模型 ====================

class CreateHabitRequest(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    target_frequency: str = "daily"


class HabitRecordRequest(BaseModel):
    habit_id: int
    user_id: int
    status: str  # completed, missed, partial
    context: Optional[str] = None


class UpdateHabitRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_frequency: Optional[str] = None


class CreateGoalRequest(BaseModel):
    user_id: int
    title: str
    description: str
    deadline: Optional[datetime] = None


# ==================== 习惯相关 ====================

@router.post("/habit/create")
async def create_habit(request: CreateHabitRequest):
    """创建习惯"""
    try:
        habit_id = db.create_habit(
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            target_frequency=request.target_frequency
        )
        return {
            "habit_id": habit_id,
            "message": "Habit created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/habit/{user_id}")
async def get_user_habits(user_id: int, active_only: bool = True):
    """获取用户的习惯列表"""
    try:
        habits = db.get_user_habits(user_id, active_only)
        return {"habits": habits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/habit/record")
async def record_habit(request: HabitRecordRequest):
    """记录习惯完成情况"""
    try:
        record_id = db.add_habit_record(
            habit_id=request.habit_id,
            user_id=request.user_id,
            date=datetime.now(),
            status=request.status,
            context=request.context
        )
        return {
            "record_id": record_id,
            "message": "Habit recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/habit/{habit_id}/records")
async def get_habit_records(habit_id: int, limit: int = 30):
    """获取习惯记录"""
    try:
        records = db.get_habit_records(habit_id, limit)
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/habit/{habit_id}")
async def update_habit(habit_id: int, request: UpdateHabitRequest):
    """更新习惯信息"""
    try:
        success = db.update_habit(
            habit_id=habit_id,
            name=request.name,
            description=request.description,
            target_frequency=request.target_frequency
        )
        if success:
            return {"message": "Habit updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Habit not found or no changes made")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/habit/{habit_id}")
async def delete_habit(habit_id: int, hard_delete: bool = False):
    """删除习惯（默认软删除）"""
    try:
        success = db.delete_habit(habit_id, soft_delete=not hard_delete)
        if success:
            return {"message": "Habit deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Habit not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 目标相关 ====================

@router.post("/goal")
async def create_goal(request: CreateGoalRequest):
    """创建目标"""
    try:
        goal_id = db.create_goal(
            user_id=request.user_id,
            title=request.title,
            description=request.description,
            deadline=request.deadline
        )
        return {
            "goal_id": goal_id,
            "message": "Goal created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goal/{user_id}")
async def get_user_goals(user_id: int, status: str = "active"):
    """获取用户目标"""
    try:
        goals = db.get_user_goals(user_id, status)
        return {"goals": goals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 反思相关 ====================

@router.get("/reflect/{user_id}")
async def get_reflections(user_id: int, limit: int = 10):
    """获取反思记录"""
    try:
        reflections = db.get_recent_reflections(user_id, limit)
        return {"reflections": reflections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 每日简报 ====================

@router.get("/brief/{user_id}")
async def get_daily_brief(user_id: int, date: Optional[str] = None):
    """获取每日简报"""
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.now()
        brief = db.get_daily_brief(user_id, target_date)
        
        if not brief:
            return {
                "message": "No brief found for this date",
                "date": target_date.isoformat()
            }
        
        return {"brief": brief}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
