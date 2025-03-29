from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    to_encode = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify token and return payload with detailed error if invalid"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload.get("exp"))
        now = datetime.utcnow()
        
        if now >= exp:
            remaining = exp - now
            raise jwt.ExpiredSignatureError(
                f"Token expired {abs(remaining)} ago"
            )
            
        return payload
    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignatureError(str(e))
    except jwt.JWTError as e:
        raise jwt.JWTError(f"Token validation failed: {str(e)}")