"""
Custom Middleware - Request logging, rate limiting, authentication
"""

import time
import uuid
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

from app.core.rate_limit import rate_limiter

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        # Track start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error {request_id}: {str(e)}")
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(
        self,
        app: ASGIApp,
        rate: Optional[int] = None,
        burst: Optional[int] = None,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.rate = rate
        self.burst = burst
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client IP
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not rate_limiter.check_rate_limit(client_id, self.rate, self.burst):
            wait_time = rate_limiter.get_wait_time(client_id, self.rate)
            
            return Response(
                status_code=429,
                content=json.dumps({
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": f"Too many requests. Please try again in {wait_time:.1f} seconds.",
                        "retry_after": wait_time
                    }
                }),
                media_type="application/json",
                headers={
                    "X-RateLimit-Reset": str(int(time.time() + wait_time)),
                    "Retry-After": str(int(wait_time))
                }
            )
        
        # Add rate limit info to request state
        request.state.rate_limit_remaining = rate_limiter.buckets.get(client_id, (0, 0))[0]
        request.state.rate_limit_reset = time.time() + rate_limiter.get_wait_time(client_id, self.rate)
        
        return await call_next(request)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for certain paths
        public_paths = [
            "/",
            "/health",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/verify-email"
        ]
        
        if request.url.path in public_paths or request.url.path.startswith("/api/v1/auth/"):
            return await call_next(request)
        
        # Authentication is handled by dependency injection
        # This middleware just ensures the request has proper headers
        auth_header = request.headers.get("Authorization")
        
        if not auth_header and not request.url.path.startswith("/api/v1/auth/"):
            # For non-authenticated requests, just continue (deps will handle 401)
            pass
        
        return await call_next(request)

class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware"""
    
    def __init__(self, app: ASGIApp, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        origin = request.headers.get("origin")
        
        if origin and (self.allowed_origins == ["*"] or origin in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = (
                "DNT, User-Agent, X-Requested-With, If-Modified-Since, "
                "Cache-Control, Content-Type, Range, Authorization"
            )
            response.headers["Access-Control-Expose-Headers"] = (
                "Content-Length, Content-Range, X-Request-ID, X-Process-Time"
            )
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            return Response(status_code=200, headers=dict(response.headers))
        
        return response

# Export all middleware
__all__ = [
    'RequestLoggingMiddleware',
    'RateLimitMiddleware',
    'AuthenticationMiddleware',
    'CORSMiddleware'
]