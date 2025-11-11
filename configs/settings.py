"""
配置管理
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置"""
    
    # 应用基本信息
    APP_NAME: str = "LifeOS AI Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DB_PATH: str = "data/lifeos.db"
    
    # LLM 配置
    LLM_PROVIDER: str = "mock"  # openai, hunyuan, mock
    
    # OpenAI 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_BASE_URL: Optional[str] = None
    
    # 腾讯混元配置
    TENCENT_SECRET_ID: Optional[str] = None
    TENCENT_SECRET_KEY: Optional[str] = None
    HUNYUAN_MODEL: str = "hunyuan-lite"
    
    # CORS 配置（如果不需要修改，注释掉 .env 中的 CORS_ORIGINS）
    CORS_ORIGINS: list = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/lifeos.log"
    
    # 其他配置
    MAX_CHAT_HISTORY: int = 50
    SESSION_TIMEOUT: int = 3600  # 秒
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
