import os
from hashlib import sha256
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import UserSignupDTO, UserLoginDTO
from app.models import User, UserType
from .jwt import get_tokens, get_user_by_token

def _hash_password(password: str, salt: str):
    if not salt:
        salt = os.urandom(32)
    key = sha256(salt + password.encode()).hexdigest()
    return key, salt.hex()
    
def signup(userDTO: UserSignupDTO, session: Session):
    try:
        user = session.query(User).filter(
            or_(User.email == userDTO.email, User.username == userDTO.username)
        ).one_or_none()

        if user:
            raise HTTPException(status_code=409, detail="Email or username already exists")

        user_type = session.query(UserType).filter(UserType.code == "user").one_or_none()

        # Assuming user_type should always be present in the database
        if not user_type:
            raise HTTPException(status_code=500, detail="User type not found in the database")

        password_hash, salt = _hash_password(password=userDTO.password, salt=None)

        user = User(username=userDTO.username, email=userDTO.email, password_hash=password_hash, salt=salt, user_type_id=user_type.id)

        session.add(user)
        session.commit()

        return {"message": "User added successfully"}, 201
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def login(userDTO: UserLoginDTO, session: Session):
    try:
        userMap = session.query(User).filter(User.username == userDTO.username).one_or_none()

        if not userMap:
            raise HTTPException(status_code=404, detail="User not found")

        password_hash, _ = _hash_password(password=userDTO.password, salt=bytes.fromhex(userMap.salt))

        if password_hash != userMap.password_hash:
            raise HTTPException(status_code=401, detail="Invalid password")

        return get_tokens(userMap.user_type.code)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

def refresh_token(token: str):
    try:
        user_type = get_user_by_token(token)

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    return get_tokens(user_type)