from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ListResponse, User, UserDTO, UserLoginDTO, UserPermissionsDTO
from app.controllers.auth import _hash_password

#TODO: aggiungere controlli di user type (cosa può fare per esempio uno user sul suo stesso account)

def list(limit : int, offset : int, user: User, session: Session) -> ListResponse:
    """
    List all users
    
    Args:
        limit (int):
        offset (int):
        user (User):
        session (Session):
    
    Returns:
        [ListResponse]: list of users
    """
    #TODO: show password hash or not ?? join user_type_id with code ??
    try:
        builder = QueryBuilder(User, session, limit, offset)
        users: List[User] = builder.getQuery().all()
        count = builder.getCount()
        return {"data": [UserDTO.model_validate(obj=obj) for obj in users], "count": count}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def read(id: int, current_user: User, session: Session) -> UserDTO:
    """
    Read a user by id
    
    Args: 
        id (int):
        session (Session):
    
    Returns:
        UserDTO: user
    """
    
    try:
        user: User = get_object_by_id(User, session, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserDTO.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def delete(id: int, current_user: User, session: Session) -> bool:
    """
    Delete user by id
    
    Args:
        id (int):
        session (session):
    
    Returns:
        bool: the result of delete operation
    
    """
    try:
        user : User = get_object_by_id(User, session, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        session.delete(user)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def update_data(id: int, updated_user: UserLoginDTO, current_user: User, session: Session) -> UserDTO:
    """
    Update username and/or password by id
    
    Args:
        id (int):
        updated_user (UserLoginDTO):
    
    Returns:
        user (UserDTO):
    """

    try:
        user : User = get_object_by_id(User, session, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        username_check : User = session.query(User).filter(User.username == updated_user.username).one_or_none()
        if username_check and username_check.id != id:
            raise HTTPException(status_code=409, detail="Username already exists")

        password_hash, _ = _hash_password(password=updated_user.password, salt=bytes.fromhex(user.salt))

        user.username = updated_user.username
        user.password_hash = password_hash

        session.commit()
        return UserDTO.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def update_permissions(id: int, updated_user: UserPermissionsDTO, current_user: User, session: Session) -> UserDTO:
    """
    Update permissions of a user by id
    
    Args:
        id (int):
        updated_user (UserPermissionsDTO):
    
    Returns:
        user (UserDTO):
    """

    try:
        user : User = get_object_by_id(User, session, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.user_type_id = updated_user.user_type_id

        session.commit()
        return UserDTO.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))