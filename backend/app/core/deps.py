"""
Dependencies - FastAPI dependency injection
"""

from fastapi import Depends, HTTPException, status, WebSocket, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Union
import logging

from app.core.security import security_manager
from app.core.database import firebase_client
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
logger = logging.getLogger(__name__)

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user from token"""
    
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    payload = security_manager.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_data = firebase_client.get_data(f"users/{user_id}")
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user_data.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )
    
    return User(**user_data)

async def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if not token:
        token = request.cookies.get("access_token")
        if not token:
            return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin role"""
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    
    return current_user

async def get_current_pro_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify pro/premium role"""
    
    if current_user.role not in [UserRole.PRO, UserRole.PREMIUM, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a Pro or Premium subscription"
        )
    
    return current_user

async def get_current_user_ws(websocket: WebSocket, token: Optional[str] = None) -> Optional[User]:
    """Get current user from WebSocket connection"""
    
    # Try to get token from query params
    if not token:
        token = websocket.query_params.get("token")
    
    if not token:
        return None
    
    try:
        payload = security_manager.verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        user_data = firebase_client.get_data(f"users/{user_id}")
        
        if not user_data:
            return None
        
        return User(**user_data)
    except Exception as e:
        logger.error(f"WebSocket auth error: {str(e)}")
        return None
