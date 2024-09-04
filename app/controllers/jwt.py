from app.config import settings
from app.models import User
from app.models.DTOs import Token

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

def _create_access_token(data: dict = None, expires_delta: timedelta = None):
    if data:
        to_encode = data.copy()
    else:
        to_encode = {}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_tokens(userCode):
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = _create_access_token(data={"userType": userCode}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = _create_access_token(data={"userType": userCode}, expires_delta=refresh_token_expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def get_refresh_token():
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = _create_access_token(expires_delta=refresh_token_expires)
    return Token(access_token="", refresh_token=refresh_token)

def get_user_by_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


