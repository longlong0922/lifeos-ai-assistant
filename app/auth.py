"""
用户认证相关功能
包括注册、登录、Token验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production-use-random-string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    """
    密码加密
    
    使用 bcrypt 加密密码。bcrypt 会自动处理盐值。
    """
    # 将密码转换为字节,bcrypt 需要字节输入
    password_bytes = password.encode('utf-8')
    # 生成盐值并加密
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 返回字符串形式的哈希值
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    比较明文密码和哈希密码是否匹配
    """
    try:
        # 将密码和哈希值转换为字节
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # 验证密码
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Token
    
    Args:
        data: 要编码的数据（通常包含 user_id）
        expires_delta: 过期时间
    
    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    解码 JWT Token
    
    Args:
        token: JWT token 字符串
    
    Returns:
        解码后的数据字典
    
    Raises:
        HTTPException: token 无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_from_token(token: str) -> int:
    """
    从 Token 中提取 user_id
    
    Args:
        token: JWT token 字符串
    
    Returns:
        用户 ID
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 中没有用户信息"
        )
    
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户 ID"
        )
