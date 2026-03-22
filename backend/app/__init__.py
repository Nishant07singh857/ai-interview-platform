"""
FastAPI Application Factory
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.core.security import security_manager
from app.api.v1 import router as api_router
from app.core.middleware import RequestLoggingMiddleware, RateLimitMiddleware
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    )
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        logger.info("🚀 Starting up application...")
        
        # Initialize Firebase
        firebase_client.initialize()
        
        # Initialize Cache
        await cache_manager.initialize()
        
        # Initialize Security
        await security_manager.initialize()
        
        logger.info("✅ Application startup complete")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info("🛑 Shutting down application...")
        
        # Close cache connection
        await cache_manager.close()
        
        logger.info("✅ Application shutdown complete")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    return app

app = create_application()
