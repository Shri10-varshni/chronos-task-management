from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import verify_password, create_access_token, verify_token
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import Token, TokenPayload, UserLogin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
bearer_scheme = HTTPBearer()

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate token and return current user
    """
    try:
        payload = verify_token(token)  # Use verify_token instead of direct decode
        token_data = TokenPayload(**payload)
    except (jwt.ExpiredSignatureError, jwt.JWTError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive",
        )
    return user

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Get access token for future API calls
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/token-status")
async def check_token_status(token: str = Depends(oauth2_scheme)):
    """
    Check if the provided token is valid and get its details
    """
    try:
        payload = verify_token(token)
        expiration = datetime.fromtimestamp(payload.get("exp"))
        now = datetime.utcnow()
        
        if expiration > now:
            time_left = expiration - now
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            seconds = time_left.seconds % 60
            time_left_str = f"{hours}h {minutes}m {seconds}s"
        else:
            time_left_str = "expired"

        return {
            "expires_at": expiration,
            "is_expired": now >= expiration,
            "time_left": time_left_str
        }
    except (jwt.ExpiredSignatureError, jwt.JWTError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
