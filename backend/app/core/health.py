from typing import Dict, Any
from datetime import datetime
from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.core.config import settings
import psutil
import redis
import asyncpg

class HealthChecker:
    """Comprehensive health checker"""
    
    async def check_all(self) -> Dict[str, Any]:
        """Check all system components"""
        
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check Firebase
        try:
            firebase_client.get_data("health_check")
            status["components"]["firebase"] = {"status": "healthy"}
        except Exception as e:
            status["components"]["firebase"] = {"status": "unhealthy", "error": str(e)}
            status["status"] = "degraded"
        
        # Check Redis
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            status["components"]["redis"] = {"status": "healthy"}
        except Exception as e:
            status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
            status["status"] = "degraded"
        
        # Check PostgreSQL if configured
        if settings.DATABASE_URL:
            try:
                conn = await asyncpg.connect(settings.DATABASE_URL)
                await conn.close()
                status["components"]["postgres"] = {"status": "healthy"}
            except Exception as e:
                status["components"]["postgres"] = {"status": "unhealthy", "error": str(e)}
                status["status"] = "degraded"
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            status["components"]["disk"] = {
                "status": "warning",
                "percent_used": disk.percent,
                "free_gb": disk.free / (1024**3)
            }
            status["status"] = "degraded"
        
        return status
health_checker = HealthChecker()
