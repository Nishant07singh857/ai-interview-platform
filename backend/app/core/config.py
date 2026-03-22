"""
Configuration Management - All settings from environment variables
No hardcoded values, everything comes from .env
"""

import os
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from dotenv import load_dotenv
import json

load_dotenv()

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "AI Interview Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)
    APP_URL: str = Field(default="http://localhost:3000", env="APP_URL")
    GCS_BUCKET: Optional[str] = Field(default=None, env="GCS_BUCKET")
    GCS_CREDENTIALS: Optional[str] = Field(default=None, env="GCS_CREDENTIALS")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT", ge=1, le=65535)
    WORKERS: int = Field(default=4, env="WORKERS", ge=1, le=16)
    API_V1_PREFIX: str = Field(default="/api/v1", env="API_V1_PREFIX")
    
    # Security
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS: str = Field(..., env="FIREBASE_CREDENTIALS")
    FIREBASE_DATABASE_URL: str = Field(..., env="FIREBASE_DATABASE_URL")
    FIREBASE_STORAGE_BUCKET: str = Field(..., env="FIREBASE_STORAGE_BUCKET")
    FIREBASE_API_KEY: str = Field(..., env="FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN: str = Field(..., env="FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID: str = Field(..., env="FIREBASE_PROJECT_ID")
    FIREBASE_SERVICE_ACCOUNT: Optional[str] = Field(default=None, env="FIREBASE_SERVICE_ACCOUNT")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_EAGER_PROPAGATES: bool = False
    CELERY_TASK_TIME_LIMIT: int = 600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 300
    
    # Database (PostgreSQL optional)
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    
    # AI Services - FIXED MODELS
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_ORG_ID: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # 🔴 FIXED: GEMINI_MODEL default should match your .env
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", env="GEMINI_MODEL")  # Changed from "gemini-pro"
    
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL: str = Field(default="microsoft/deberta-v3-base", env="HUGGINGFACE_MODEL")
    
    # AWS Services
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    EMAIL_FROM: str = Field(default="noreply@aiinterview.com", env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = "AI Interview Platform"
    
    # Payment Gateway (Stripe)
    STRIPE_PUBLIC_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    STRIPE_CURRENCY: str = "usd"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".jpg", ".png", ".jpeg"],
        env="ALLOWED_EXTENSIONS"
    )
    UPLOAD_PATH: str = "uploads"
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: int = 10485760
    LOG_BACKUP_COUNT: int = 5
    
    # ML Models
    SKILL_EXTRACTOR_MODEL_PATH: str = "ml_services/models/skill_extractor.pkl"
    READINESS_MODEL_PATH: str = "ml_services/models/readiness_model.pkl"
    DIFFICULTY_CLASSIFIER_PATH: str = "ml_services/models/difficulty_classifier.pkl"
    QUESTION_GENERATOR_PATH: str = "ml_services/models/question_generator"
    
    # Cache
    CACHE_TTL: int = 3600
    CACHE_MAX_SIZE: int = 1000
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    # SSL
    SSL_ENABLED: bool = Field(default=False, env="SSL_ENABLED")
    SSL_KEYFILE: Optional[str] = Field(default=None, env="SSL_KEYFILE")
    SSL_CERTFILE: Optional[str] = Field(default=None, env="SSL_CERTFILE")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v
    
    @validator("DEBUG")
    def validate_debug(cls, v):
        if v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("DEBUG cannot be True in production")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create global settings instance
settings = Settings()

# Validate critical settings on startup
def validate_settings():
    """Validate that all required settings are present"""
    required_settings = [
        "SECRET_KEY",
        "FIREBASE_CREDENTIALS",
        "FIREBASE_DATABASE_URL",
        "FIREBASE_API_KEY",
        "SMTP_USER",
        "SMTP_PASSWORD"
    ]
    
    # Optional settings - just log warning, don't fail
    if not settings.GEMINI_API_KEY:
        print("⚠️ Warning: GEMINI_API_KEY not set. Gemini features will not work.")
    
    missing = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing.append(setting)
    
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")

validate_settings()