"""
Rate Limiting - API rate limiting functionality
"""

import time
import logging
from typing import Dict, Tuple, Optional
from collections import defaultdict
from fastapi import HTTPException, Request
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    """In-memory rate limiter using token bucket algorithm"""
    
    def __init__(self):
        # Store: client_id -> (tokens, last_update)
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))
        self.default_rate = 100  # requests per minute
        self.default_burst = 20   # burst capacity
    
    def check_rate_limit(
        self,
        client_id: str,
        rate: Optional[int] = None,
        burst: Optional[int] = None
    ) -> bool:
        """
        Check if request is within rate limit
        Returns True if allowed, False if rate limited
        """
        rate = rate or self.default_rate
        burst = burst or self.default_burst
        
        now = time.time()
        tokens, last = self.buckets[client_id]
        
        # Add new tokens based on time passed
        time_passed = now - last
        new_tokens = time_passed * (rate / 60.0)  # rate per minute
        
        tokens = min(burst, tokens + new_tokens)
        
        if tokens >= 1:
            # Consume one token
            self.buckets[client_id] = (tokens - 1, now)
            return True
        else:
            # Rate limited
            self.buckets[client_id] = (tokens, now)
            return False
    
    def get_wait_time(self, client_id: str, rate: Optional[int] = None) -> float:
        """Get time to wait until next request is allowed"""
        rate = rate or self.default_rate
        
        tokens, last = self.buckets.get(client_id, (0.0, time.time()))
        
        if tokens >= 1:
            return 0
        
        # Time needed to get one token
        return (1 - tokens) * (60.0 / rate)
    
    def reset_client(self, client_id: str):
        """Reset rate limit for a client"""
        if client_id in self.buckets:
            del self.buckets[client_id]

# Global rate limiter instance
rate_limiter = RateLimiter()

# Dependency for FastAPI
async def check_rate_limit(
    request: Request,
    rate: Optional[int] = None,
    burst: Optional[int] = None,
    key_func: Optional[callable] = None
):
    """
    FastAPI dependency for rate limiting
    
    Usage:
    @app.get("/endpoint")
    async def endpoint(_: None = Depends(check_rate_limit)):
        return {"message": "ok"}
    """
    
    # Get client identifier
    if key_func:
        client_id = key_func(request)
    else:
        # Default: use client IP
        client_id = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not rate_limiter.check_rate_limit(client_id, rate, burst):
        wait_time = rate_limiter.get_wait_time(client_id, rate)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": wait_time,
                "message": f"Too many requests. Please try again in {wait_time:.1f} seconds."
            },
            headers={"X-RateLimit-Reset": str(int(time.time() + wait_time))}
        )
    
    # Add rate limit headers to response (will be added by middleware)
    request.state.rate_limit_remaining = rate_limiter.buckets.get(client_id, (0, 0))[0]
    request.state.rate_limit_reset = time.time() + rate_limiter.get_wait_time(client_id, rate)

# Decorator for non-FastAPI functions
def rate_limit(rate: Optional[int] = None, burst: Optional[int] = None):
    """Decorator for rate limiting on regular functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get client_id from kwargs or use a default
            client_id = kwargs.get('client_id', 'default')
            
            if not rate_limiter.check_rate_limit(client_id, rate, burst):
                raise Exception("Rate limit exceeded")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Middleware for automatic rate limiting
class RateLimitMiddleware:
    """FastAPI middleware for automatic rate limiting"""
    
    def __init__(
        self,
        app,
        rate: Optional[int] = None,
        burst: Optional[int] = None,
        exclude_paths: Optional[list] = None
    ):
        self.app = app
        self.rate = rate
        self.burst = burst
        self.exclude_paths = exclude_paths or []
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create request object
        from starlette.requests import Request
        request = Request(scope, receive)
        
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            await self.app(scope, receive, send)
            return
        
        # Get client IP
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not rate_limiter.check_rate_limit(client_id, self.rate, self.burst):
            wait_time = rate_limiter.get_wait_time(client_id, self.rate)
            
            # Send rate limit response
            from starlette.responses import JSONResponse
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": {
                        "error": "Rate limit exceeded",
                        "retry_after": wait_time,
                        "message": f"Too many requests. Please try again in {wait_time:.1f} seconds."
                    }
                },
                headers={
                    "X-RateLimit-Reset": str(int(time.time() + wait_time))
                }
            )
            await response(scope, receive, send)
            return
        
        # Add rate limit info to scope
        scope["state"] = getattr(scope, "state", {})
        scope["state"].rate_limit_remaining = rate_limiter.buckets.get(client_id, (0, 0))[0]
        scope["state"].rate_limit_reset = time.time() + rate_limiter.get_wait_time(client_id, self.rate)
        
        await self.app(scope, receive, send)