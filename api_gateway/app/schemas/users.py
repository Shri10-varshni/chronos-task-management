from datetime import datetime, time, timedelta
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, validator, Field
from jose import jwt
from app.core.config import settings

# Base User Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    reminder_enabled: bool = True
    reminder_notify_method: str = 'email'
    theme_preference: Optional[str] = 'light'
    daily_start_time: Optional[time] = time(9, 0)
    daily_end_time: Optional[time] = time(17, 0)
    
    @validator('reminder_notify_method')
    def validate_notify_method(cls, v):
        if v not in ['email', 'push', 'sms']:
            raise ValueError('Notification method must be email, push, or sms')
        return v
    
    @validator('theme_preference')
    def validate_theme(cls, v):
        if v not in ['light', 'dark', 'system']:
            raise ValueError('Theme must be light, dark, or system')
        return v

# Schema for user creation
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# Schema for updating user
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    reminder_notify_method: Optional[str] = None
    theme_preference: Optional[str] = None
    daily_start_time: Optional[time] = None
    daily_end_time: Optional[time] = None
    is_active: Optional[bool] = None
    
    @validator('reminder_notify_method')
    def validate_notify_method(cls, v):
        if v is not None and v not in ['email', 'push', 'sms']:
            raise ValueError('Notification method must be email, push, or sms')
        return v

# Schema for user in response
class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    role: str
    
    class Config:
        orm_mode = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    def is_access_token_expired(self) -> bool:
        """Check if access token is expired"""
        try:
            payload = jwt.decode(
                self.access_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            expiration = datetime.fromtimestamp(payload.get("exp"))
            return datetime.utcnow() >= expiration
        except:
            return True

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

# Login schema
class UserLogin(BaseModel):
    username: str
    password: str
