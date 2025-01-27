from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import UserSignupDTO, UserLoginDTO
from app.models import User, UserType
from app.models.role import Role
from app.auth_util.jwt import get_tokens
from app.auth_util.pwd_util import _hash_password
  
def signup(userDTO: UserSignupDTO, session: Session, logged_user: User):
    try:
        user_type = session.query(UserType).filter(UserType.permissions == Role.USER).one_or_none()

        if not user_type:
            raise HTTPException(status_code=500, detail="User type not found in the database")
        
        # Check if the user has the user mantainer bit set
        if logged_user and (logged_user.user_type.permissions & Role.USER_MAINTAINER) and userDTO.user_type_id:
            user_type = session.query(UserType).filter(UserType.id == userDTO.user_type_id).one_or_none()


        user = session.query(User).filter(
            or_(User.email == userDTO.email, User.username == userDTO.username)
        ).one_or_none()

        if user:
            raise HTTPException(status_code=409, detail="Email or username already exists")

        password_hash, salt = _hash_password(password=userDTO.password)

        user = User(username=userDTO.username, email=userDTO.email, password_hash=password_hash, salt=salt, user_type_id=user_type.id, deletion_date=None)

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
        
        if userMap.deletion_date is not None:
            raise HTTPException(status_code=404, detail="User not found")
        password_hash, _ = _hash_password(password=userDTO.password, salt=bytes.fromhex(userMap.salt))

        if password_hash != userMap.password_hash:
            raise HTTPException(status_code=401, detail="Invalid password")

        return get_tokens(userMap.id, userMap.username, userMap.user_type.permissions)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))