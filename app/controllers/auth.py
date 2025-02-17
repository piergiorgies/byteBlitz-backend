from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.schemas import LoginRequest, LoginResponse
from app.models.mapping import User, UserType
from app.models.role import Role
from app.util.jwt import get_tokens
from app.util.pwd import _hash_password

def login(user_login: LoginRequest, session: Session):
    try:
        user_db = session.query(User).filter(User.username == user_login.username).one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_db.deletion_date is not None:
            raise HTTPException(status_code=404, detail="User not found")
        password_hash, _ = _hash_password(password=user_login.password, salt=bytes.fromhex(user_db.salt))

        if password_hash != user_db.password_hash:
            raise HTTPException(status_code=401, detail="Invalid password")

        return LoginResponse.model_validate_json(
            json_data=get_tokens(user_db.id, user_db.username, user_db.user_type.permissions)
        )
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))