import random
from hashlib import sha256
from datetime import datetime, timedelta

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.schemas import LoginRequest, LoginResponse, ResetPasswordRequest, ChangeResetPasswordRequest
from app.models.mapping import User
from app.util.jwt import get_tokens
from app.util.pwd import _hash_password
from app.util.mail import MailSender
from app.config import settings

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
        
        user_db.reset_password_token = sha256(str(random.getrandbits(256)).encode()).hexdigest()
        user_db.reset_password_token_expiration = datetime.now() + timedelta(hours=1)        
        session.commit()


        body = f"""<h1>Reset your password</h1>
                    <p>Click on the link to reset your password:
                    <a href='{settings.APP_DOMAIN}/password-reset?token={user_db.reset_password_token}'>Reset password</a></p>
                """

        sender = MailSender()    
        sender.send_mail(
            subject="Password reset",
            body=body,
            to=user_db.email
        )

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