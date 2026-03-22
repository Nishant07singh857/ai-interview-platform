"""
Security Module - JWT, Encryption, Password Hashing
Complete implementation with no placeholders
"""

import jwt
import bcrypt
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # ✅ FIXED: Correct import
import base64
import logging
from .config import settings

logger = logging.getLogger(__name__)

class SecurityManager:
    """Complete security management system"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.encryption_key = None
            self.fernet = None
            self._initialized = True
    
    async def initialize(self):
        """Initialize security components"""
        try:
            # Generate or load encryption key
            self.encryption_key = self._get_encryption_key()
            self.fernet = Fernet(self.encryption_key)
            logger.info("Security manager initialized")
        except Exception as e:
            logger.error(f"Security initialization failed: {str(e)}")
            raise
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key"""
        # In production, this should come from a secure key management service
        # For now, derive from SECRET_KEY
        kdf = PBKDF2HMAC(  # ✅ FIXED: Correct class name
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai_interview_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return key
    
    # Password Hashing
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    # JWT Tokens
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        if payload and payload.get("type") == "refresh":
            # Remove exp and iat from payload
            payload.pop("exp", None)
            payload.pop("iat", None)
            payload.pop("type", None)
            return self.create_access_token(payload)
        return None
    
    # Encryption
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
    
    # API Key Generation
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def generate_webhook_secret(self) -> str:
        """Generate webhook secret"""
        return secrets.token_hex(32)
    
    # CSRF Tokens
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, stored_token: str) -> bool:
        """Verify CSRF token"""
        return hmac.compare_digest(token, stored_token)
    
    # OTP Generation
    def generate_otp(self, length: int = 6) -> str:
        """Generate numeric OTP"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    # Session Management
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return secrets.token_urlsafe(16)
    
    # Secure Random
    def secure_random(self, length: int = 32) -> str:
        """Generate cryptographically secure random string"""
        return secrets.token_hex(length)
    
    # Hash functions
    def sha256_hash(self, data: str) -> str:
        """SHA-256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sha512_hash(self, data: str) -> str:
        """SHA-512 hash"""
        return hashlib.sha512(data.encode()).hexdigest()
    
    def hmac_sign(self, data: str, key: Optional[str] = None) -> str:
        """HMAC signature"""
        if key is None:
            key = settings.SECRET_KEY
        signature = hmac.new(
            key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def hmac_verify(self, data: str, signature: str, key: Optional[str] = None) -> bool:
        """Verify HMAC signature"""
        expected = self.hmac_sign(data, key)
        return hmac.compare_digest(signature, expected)
    
    # Email verification token
    def generate_email_verification_token(self, email: str) -> str:
        """Generate email verification token"""
        data = {
            "email": email,
            "purpose": "email_verification",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    # Password reset token
    def generate_password_reset_token(self, user_id: str) -> str:
        """Generate password reset token"""
        data = {
            "user_id": user_id,
            "purpose": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# Global instance
security_manager = SecurityManager()