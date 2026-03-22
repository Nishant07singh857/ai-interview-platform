"""
AI Interview Platform - Main Application Entry Point
FastAPI + Firebase Backend - Production Ready
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.core.security import security_manager
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    AuthenticationMiddleware
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    All services are properly initialized here
    """
    # STARTUP EVENTS
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    
    try:
        # Initialize Firebase
        firebase_client.initialize()
        logger.info("✅ Firebase initialized successfully")
        
        # Initialize Cache
        await cache_manager.initialize()
        logger.info("✅ Cache manager initialized")
        
        # Initialize Security Manager
        await security_manager.initialize()
        logger.info("✅ Security manager initialized")
        
        # Load ML Models
        from app.ml_services.model_loader import ModelLoader
        model_loader = ModelLoader()
        await model_loader.load_all_models()
        logger.info("✅ ML Models loaded successfully")
        
        # Initialize Background Tasks
        from app.tasks.celery_app import celery_app
        logger.info("✅ Celery task queue initialized")
        
        logger.info("✨ All services started successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    
    yield
    
    # SHUTDOWN EVENTS
    logger.info("🛑 Shutting down services...")
    
    try:
        # Cleanup cache
        await cache_manager.close()
        
        # Close Firebase connections
        firebase_client.close()
        
        # Close ML models
        from app.ml_services.model_loader import ModelLoader
        model_loader = ModelLoader()
        await model_loader.unload_models()
        
        logger.info("✅ All services shut down gracefully")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Interview Platform - Complete Interview Preparation for AI/ML/DL/DS",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Setup exception handlers
setup_exception_handlers(app)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit"]
)

# Custom Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthenticationMiddleware)
# app.add_middleware(RequestIDMiddleware)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health check endpoint with detailed status
@app.get("/health")
async def health_check() -> Dict:
    """Comprehensive health check endpoint"""
    from app.core.health import health_checker
    
    health_status = await health_checker.check_all()
    return health_status

@app.get("/")
async def root() -> Dict:
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs" if settings.DEBUG else "Documentation not available in production",
        "endpoints": {
            "health": "/health",
            "api": settings.API_V1_PREFIX
        }
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from app.core.monitoring import metrics_collector
    return await metrics_collector.get_metrics()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
        ssl_keyfile=settings.SSL_KEYFILE if settings.SSL_ENABLED else None,
        ssl_certfile=settings.SSL_CERTFILE if settings.SSL_ENABLED else None
    )