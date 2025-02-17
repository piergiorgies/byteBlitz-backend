from operator import is_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List
from datetime import datetime

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.database import get_object_by_id
from app.schemas import UserListResponse, UserResponse, UserCreate, UserUpdate, PaginationParams
from app.models.mapping import User, UserType
from app.repositories import UserRepository

def create_user(user: UserCreate, session: Session) -> UserResponse:
    """
    create a new user

    Args:
        user (UserCreate): the user DTO
        session (Session): the session

    Returns:
        UserResponse: the created user
    """
    try:
        repo = UserRepository(session)
        user_type = repo.get_user_type_by_id(user.user_type_id)
        if not user_type:
            raise HTTPException(status_code=404, detail="User type not found")
        
        user = repo.create(user)
        return user
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))



def list_user(pagination: PaginationParams, user: User, session: Session) -> UserListResponse:
    """
    List all users
    
    Args:
        limit (int):
        offset (int):
        user (User):
        session (Session):
    
    Returns:
        [UserListResponse]: list of users
    """
    
    try:

        judge_type = session.query(UserType).filter(UserType.permissions == Role.JUDGE).one_or_none()
        if not judge_type:
            raise HTTPException(status_code=500, detail="Judge user type not found")
        guest_type = session.query(UserType).filter(UserType.permissions == Role.GUEST).one_or_none()
        if not guest_type:
            raise HTTPException(status_code=500, detail="Guest user type not found")
        
        builder = session.query(User).filter(User.deletion_date == None, User.user_type_id != judge_type.id, User.user_type_id != guest_type.id)
        if pagination.search_filter:
            builder = builder.filter(User.username.ilike(f"%{pagination.search_filter}%"))
        users: List[User] = builder.limit(pagination.limit).offset(pagination.offset).all()
        count = builder.count()
        return {"data": [UserResponse.model_validate(obj=obj) for obj in users], "count": count}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def read_user(id: int, current_user: User, session: Session) -> UserResponse:
    """
    Read a user by id
    
    Args: 
        id (int):
        session (Session):
    
    Returns:
        UserResponse: user
    """
    
    try:
        is_admin_maintainer = RoleChecker.hasRole(current_user, Role.USER_MAINTAINER)
        user: User = get_object_by_id(User, session, id)
        if not user or (not is_admin_maintainer and user.id != current_user.id):
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def read_me(current_user: User, session: Session) -> UserResponse:
    """
    Read the information of the logged user
    
    Args: 
        session (Session):
    
    Returns:
        UserDTO: user
    """
    
    try:
        user: User = get_object_by_id(User, session, current_user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


def delete_user(id: int, current_user: User, session: Session) -> bool:
    """
    Delete user by id
    
    Args:
        id (int):
        session (session):
    
    Returns:
        bool: the result of delete operation
    
    """
    try:
        is_admin = RoleChecker.hasRole(current_user, Role.USER_MAINTAINER)
        user: User = get_object_by_id(User, session, id)

        if not user or (not is_admin and user.id != current_user.id):
            raise HTTPException(status_code=404, detail="User not found")
        
        user.deletion_date = datetime.now()
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
    


def update_user(id: int, updated_user: UserUpdate, current_user: User, session: Session) -> UserResponse:
    """update user by id

    Args:
        id (int): the id of the user
        updated_user (UserDTO): the updated user DTO
        current_user (User): the current user
        session (Session): session

    Returns:
        UserDTO: the updated user
    """
    try:
        is_admin_maintainer = RoleChecker.hasRole(current_user, Role.USER_MAINTAINER)
        user: User = get_object_by_id(User, session, id)
        if not user or (not is_admin_maintainer and user.id != current_user.id):
            raise HTTPException(status_code=404, detail="User not found")
        username_check : User = session.query(User).filter(User.username == updated_user.username).one_or_none()
        if username_check and username_check.id != id:
            raise HTTPException(status_code=409, detail="Username already exists")

        user_type = session.query(UserType).filter(UserType.id == updated_user.user_type_id).one_or_none()
        if not user_type:
            raise HTTPException(status_code=404, detail="User type not found")

        user.username = updated_user.username
        user.email = updated_user.email
        user.user_type_id = updated_user.user_type_id

        session.commit()
        return UserUpdate.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


def available_user_types_list(session: Session) -> List[UserType]:
    """
    Get all user types
    
    Args:
        session (Session):
    
    Returns:
        List[UserType]: list of user types
    """
    try:
        # exclude judge and guest user types

        to_exclude = [Role.JUDGE, Role.GUEST]
        user_types: List[UserType] = session.query(UserType).filter(UserType.permissions.notin_(to_exclude)).all()
        return user_types
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))