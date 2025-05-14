import random
from hashlib import sha256
from datetime import datetime, timedelta

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from fastapi import HTTPException
from app.models.mapping import UserType
from app.models import Role
from app.schemas import LoginRequest, LoginResponse, ResetPasswordRequest, ChangeResetPasswordRequest
from app.models.mapping import User
from app.util.jwt import get_tokens
from app.util.pwd import _hash_password
from app.util.mail import MailSender
from app.config import settings

def login(user_login: LoginRequest, session: Session):
    try:
        user_db = session.query(User).filter(
            (func.lower(User.username) == func.lower(user_login.username)) |
            (func.lower(User.email) == func.lower(user_login.username))
        ).join(UserType).one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_db.deletion_date is not None:
            raise HTTPException(status_code=404, detail="User not found")
        password_hash, _ = _hash_password(password=user_login.password, salt=bytes.fromhex(user_db.salt))

        if password_hash != user_db.password_hash:
            raise HTTPException(status_code=401, detail="Invalid password")

        return LoginResponse.model_validate(
            get_tokens(user_db.id, user_db.username, user_db.user_type.permissions)
        )
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

def reset_password(data: ResetPasswordRequest, session: Session):
    try:
        user_db = session.query(User).filter(User.email == data.email, User.deletion_date == None).one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        # check if another token is already active
        if user_db.reset_password_token_expiration and user_db.reset_password_token_expiration > datetime.now():
            raise HTTPException(status_code=400, detail="Token already sent, please check your email")
        
        user_db.reset_password_token = sha256(str(random.getrandbits(256)).encode()).hexdigest()
        user_db.reset_password_token_expiration = datetime.now() + timedelta(minutes=30)        
        session.commit()


        body = f"""<h1>Reset your password</h1>
<p>Click on the link to reset your password:
<a href='{settings.APP_DOMAIN}/password-reset?token={user_db.reset_password_token}'>Reset password</a></p>"""

        sender = MailSender()    
        sender.send_mail(
            subject="Password reset",
            body=body,
            to=user_db.email
        )
        del sender

        return
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

def change_reset_password(data: ChangeResetPasswordRequest, session: Session):
    try:
        user_db = session.query(User).filter(User.reset_password_token == data.token).one_or_none()

        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_db.reset_password_token_expiration < datetime.now():
            raise HTTPException(status_code=400, detail="Token expired")
        
        password_hash, salt = _hash_password(password=data.password)
        user_db.password_hash = password_hash
        user_db.salt = salt
        user_db.reset_password_token = None
        user_db.reset_password_token_expiration = None
        session.commit()

        return JSONResponse(
            status_code=200,
            content={"detail": "Password changed"}
        )
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred" + str(e))
    


def create_github_user(user_json: dict, session: Session):
    """
    Create a user from the github login, if the user does not exist

    Args:
        user_json (dict): user data from github
        session (Session): sqlalchemy session

    Returns:
        LoginResponse: response
    """

    try:
        # get the User type
        user_type = session.query(UserType).filter(UserType.permissions == Role.USER).one_or_none()

        if not user_type:
            raise HTTPException(status_code=500, detail="User type not found")


        user_email = user_json["email"] if user_json["email"] else user_json["login"] + "@github.com"

        user_db = session.query(User).filter(User.email == user_email).one_or_none()

        if not user_db:
            user_db = User(
                username=user_json["login"],
                email=user_email,
                password_hash="",
                salt="",
                user_type_id=user_type.id
            )
            session.add(user_db)
            session.commit()
        
        else:
            user_db.username = user_json["login"]
            user_db.email = user_email
            session.commit()

        return LoginResponse.model_validate(
            get_tokens(user_db.id, user_db.username, user_db.user_type.permissions)
        )
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred" + str(e))


