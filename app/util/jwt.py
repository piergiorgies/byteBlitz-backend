from app.config import settings
from app.models.mapping import User, UserType
from app.database import get_session
from app.models.role import Role

from datetime import datetime, timedelta, timezone
from jose import ExpiredSignatureError, JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Cookie, HTTPException, Query, Request, WebSocket, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class BearerScheme:
    async def __call__(self, request: Request):
        token = request.headers.get('Authorization')
        if token == None or not token.startswith('Bearer '):
            return None
        
        return token.split(' ')[1]

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def _create_access_token(data: dict = None, expires_delta: timedelta = None):
    # data is the payload of the token
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.PRIVATE_KEY, algorithm=settings.ALGORITHM)

def get_tokens(user_id, username, user_permissions):
    # Generate access token
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expire = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    data = {
        "user_id": user_id,
        "sub": username,
        "user_permissions": user_permissions
    }

    access_token = _create_access_token(data=data, expires_delta=access_token_expire)
    # refresh_token = _create_access_token(data=data, expires_delta=refresh_token_expire)
    return {
        "access_token": access_token,
        # "refresh_token": refresh_token
    }

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, settings.PUBLIC_KEY, algorithms=[settings.ALGORITHM])
        
        user_id = payload.get("user_id")
        username = payload.get("sub")
        role = payload.get("user_permissions")

        if not user_id or not username or not role:
            raise credentials_exception
    

        return user_id, username
    
    except ExpiredSignatureError as e:
        return '', ''
    except JWTError as e:
        raise credentials_exception

def get_current_user(token: Annotated[str | None, Cookie()], api_token: Annotated[str | None, Depends(BearerScheme())], session: Session = Depends(get_session)):
    token = token or api_token

    try:
        if token == '':
            user_type = session.query(UserType).filter(UserType.permissions == Role.GUEST).one_or_none()
            if not user_type:
                raise HTTPException(status_code=500, detail="Guest user type not found")
            
            user: User = session.query(User).filter(User.user_type_id == user_type.id).first()

            if user is None:
                raise credentials_exception
            return user

        else:
            id, username = decode_token(token)

            if (id == '' or username == ''):
                user_type = session.query(UserType).filter(UserType.permissions == Role.GUEST).one_or_none()
                if not user_type:
                    raise HTTPException(status_code=500, detail="Guest user type not found")
            
                user: User = session.query(User).filter(User.user_type_id == user_type.id).first()

                if user is None:
                    raise credentials_exception
                return user

            user: User = session.query(User).filter(User.id == id, User.username == username).first()

            if user is None:
                raise credentials_exception

            return user

    except HTTPException as e:
        raise e
    
def get_judge(data: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    try:
        if data == '' or not ':' in data:
            return None
        else:
            name, hashed = data.split(':')
            judge: User = session.query(User).filter(User.username == name, User.password_hash == hashed).first()
            return judge
        
    except HTTPException as e:
        raise e

def get_websocket_user(_: WebSocket, token: Annotated[str | None, Cookie()], session: Session = Depends(get_session)):
    id, username = decode_token(token)
    user: User = session.query(User).filter(User.id == id, User.username == username).first()

    if user is None:
        raise credentials_exception

    return user
