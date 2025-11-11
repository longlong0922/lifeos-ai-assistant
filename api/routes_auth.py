"""
用户认证 API 路由
包括注册、登录、登出等
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import Database
from app.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_user_id_from_token
)
from configs.settings import get_settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

settings = get_settings()
db = Database(settings.DB_PATH)


# ==================== 请求/响应模型 ====================

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: Optional[EmailStr] = None
    timezone: str = "Asia/Shanghai"


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class AuthResponse(BaseModel):
    """认证响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    is_new_user: bool


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    user_id: int
    username: str
    email: Optional[str]
    is_new_user: bool
    onboarding_completed: bool
    created_at: str


# ==================== 依赖函数 ====================

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    从 Token 中获取当前用户 ID
    用作其他接口的依赖
    """
    token = credentials.credentials
    return get_user_id_from_token(token)


# ==================== API 端点 ====================

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    用户注册
    
    Args:
        request: 注册请求（用户名、密码、邮箱）
    
    Returns:
        认证响应（token + 用户信息）
    """
    # 检查用户名是否已存在
    existing_user = db.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if request.email:
        existing_email = db.get_user_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 密码加密
    password_hash = hash_password(request.password)
    
    # 创建用户
    user_id = db.create_user_with_password(
        username=request.username,
        password_hash=password_hash,
        email=request.email,
        timezone=request.timezone
    )
    
    # 生成 token
    access_token = create_access_token(data={"sub": str(user_id)})
    
    return AuthResponse(
        access_token=access_token,
        user_id=user_id,
        username=request.username,
        is_new_user=True
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    Args:
        request: 登录请求（用户名、密码）
    
    Returns:
        认证响应（token + 用户信息）
    """
    # 查找用户
    user = db.get_user_by_username(request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not user.get('password_hash'):
        # 兼容旧用户（没有密码）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此用户尚未设置密码，请联系管理员"
        )
    
    if not verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 更新最后登录时间
    db.update_last_login(user['id'])
    
    # 生成 token
    access_token = create_access_token(data={"sub": str(user['id'])})
    
    return AuthResponse(
        access_token=access_token,
        user_id=user['id'],
        username=user['username'],
        is_new_user=bool(user.get('is_new_user', False))
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user(user_id: int = Depends(get_current_user_id)):
    """
    获取当前用户信息
    
    需要在 Header 中携带 Authorization: Bearer <token>
    
    Returns:
        用户信息
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserInfoResponse(
        user_id=user['id'],
        username=user['username'],
        email=user.get('email'),
        is_new_user=bool(user.get('is_new_user', False)),
        onboarding_completed=bool(user.get('onboarding_completed', False)),
        created_at=str(user.get('created_at', ''))
    )


@router.post("/complete-onboarding")
async def complete_onboarding(user_id: int = Depends(get_current_user_id)):
    """
    完成新手引导
    
    需要在 Header 中携带 Authorization: Bearer <token>
    
    Returns:
        成功消息
    """
    db.mark_onboarding_completed(user_id)
    
    return {"message": "新手引导已完成", "user_id": user_id}


@router.post("/logout")
async def logout(user_id: int = Depends(get_current_user_id)):
    """
    登出（前端删除 token 即可）
    
    Returns:
        成功消息
    """
    return {"message": "登出成功", "user_id": user_id}
