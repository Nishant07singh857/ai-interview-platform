"""
Authentication Endpoints
Complete implementation with all auth features
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.core.security import security_manager
from app.core.database import firebase_client
from app.core.config import settings
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordReset,
    EmailVerification,
    ChangePassword
)
from app.services.auth_service import AuthService
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.core.rate_limit import rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register(
    request: Request,
    user_data: UserCreate
):
    """
    Register a new user
    - Creates Firebase user
    - Creates user profile in database
    - Sends verification email
    """
    try:
        # Check rate limit
        client_ip = request.client.host
        rate_limiter.check_rate_limit(f"register:{client_ip}", 5, 3600)
        
        # Register user
        user = await auth_service.register_user(user_data)
        
        # Send verification email
        await auth_service.send_verification_email(user.email)
        
        logger.info(f"User registered successfully: {user.email}")
        return user
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin
):
    """
    Login user
    - Validates credentials
    - Returns access and refresh tokens
    - Sets secure cookies
    """
    try:
        # Check rate limit
        client_ip = request.client.host
        rate_limiter.check_rate_limit(f"login:{client_ip}", 10, 300)
        
        # Authenticate
        tokens = await auth_service.authenticate_user(
            credentials.email,
            credentials.password
        )
        
        # Set secure cookies
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=1800  # 30 minutes
        )
        
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=604800  # 7 days
        )
        
        logger.info(f"User logged in: {credentials.email}")
        return tokens
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Logout user
    - Clears authentication cookies
    - Invalidates tokens
    """
    try:
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        # Invalidate tokens if user is authenticated
        if current_user:
            await auth_service.invalidate_tokens(current_user.uid)
        
        logger.info(f"User logged out: {current_user.email if current_user else 'anonymous'}")
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response
):
    """
    Refresh access token using refresh token
    """
    try:
        # Get refresh token from cookie or header
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                refresh_token = auth_header.replace("Bearer ", "")
        
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token")
        
        # Refresh tokens
        tokens = await auth_service.refresh_tokens(refresh_token)
        
        # Update cookies
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=1800
        )
        
        logger.info("Token refreshed successfully")
        return tokens
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification
):
    """
    Verify user email with token
    """
    try:
        success = await auth_service.verify_email(verification.token)
        if success:
            logger.info(f"Email verified: {verification.token[:10]}...")
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
            
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Verification failed")

@router.post("/resend-verification")
async def resend_verification(
    email: str
):
    """
    Resend verification email
    """
    try:
        await auth_service.send_verification_email(email)
        logger.info(f"Verification email resent: {email}")
        return {"message": "Verification email sent"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.post("/forgot-password")
async def forgot_password(
    email: str
):
    """
    Send password reset email
    """
    try:
        await auth_service.send_password_reset_email(email)
        logger.info(f"Password reset email sent: {email}")
        return {"message": "Password reset email sent"}
        
    except ValueError as e:
        # Don't reveal if email exists or not for security
        logger.warning(f"Password reset attempted for non-existent email: {email}")
        return {"message": "If email exists, reset link will be sent"}
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset
):
    """
    Reset password with token
    """
    try:
        success = await auth_service.reset_password(
            reset_data.token,
            reset_data.new_password
        )
        
        if success:
            logger.info(f"Password reset successful")
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
            
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset failed")

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user)
):
    """
    Change password (authenticated users)
    """
    try:
        success = await auth_service.change_password(
            current_user.uid,
            password_data.current_password,
            password_data.new_password
        )
        
        if success:
            logger.info(f"Password changed for user: {current_user.email}")
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
            
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password change failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user info
    """
    return current_user

@router.post("/logout-all")
async def logout_all_devices(
    current_user: User = Depends(get_current_user)
):
    """
    Logout from all devices
    """
    try:
        await auth_service.invalidate_all_tokens(current_user.uid)
        logger.info(f"Logged out all devices for user: {current_user.email}")
        return {"message": "Logged out from all devices"}
        
    except Exception as e:
        logger.error(f"Logout all error: {str(e)}")
        raise HTTPException(status_code=500, detail="Operation failed")

@router.get("/sessions")
async def get_active_sessions(
    current_user: User = Depends(get_current_user)
):
    """
    Get all active sessions for user
    """
    try:
        sessions = await auth_service.get_active_sessions(current_user.uid)
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Revoke specific session
    """
    try:
        await auth_service.revoke_session(current_user.uid, session_id)
        logger.info(f"Session revoked: {session_id}")
        return {"message": "Session revoked"}
        
    except Exception as e:
        logger.error(f"Revoke session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to revoke session")

@router.post("/mfa/setup")
async def setup_mfa(
    current_user: User = Depends(get_current_user)
):
    """
    Setup Multi-Factor Authentication
    """
    try:
        mfa_data = await auth_service.setup_mfa(current_user.uid)
        logger.info(f"MFA setup initiated for user: {current_user.email}")
        return mfa_data
        
    except Exception as e:
        logger.error(f"MFA setup error: {str(e)}")
        raise HTTPException(status_code=500, detail="MFA setup failed")

@router.post("/mfa/verify")
async def verify_mfa(
    code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Verify and enable MFA
    """
    try:
        success = await auth_service.verify_and_enable_mfa(current_user.uid, code)
        if success:
            logger.info(f"MFA enabled for user: {current_user.email}")
            return {"message": "MFA enabled successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid verification code")
            
    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="MFA verification failed")

@router.post("/mfa/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user)
):
    """
    Disable MFA
    """
    try:
        await auth_service.disable_mfa(current_user.uid)
        logger.info(f"MFA disabled for user: {current_user.email}")
        return {"message": "MFA disabled successfully"}
        
    except Exception as e:
        logger.error(f"MFA disable error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disable MFA")
