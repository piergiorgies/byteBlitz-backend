from operator import is_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List
from datetime import datetime

from app.models.role import Role
from app.auth_util.role_checker import RoleChecker
from app.database import QueryBuilder, get_object_by_id
from app.models import ListResponse, User, UserDTO, UserLoginDTO, UserPermissionsDTO, UserType
from app.controllers.auth import _hash_password

def list(limit: int, offset: int, searchFilter: str, user: User, session: Session) -> ListResponse:
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
    
    try:
        judge_type = session.query(UserType).filter(UserType.permissions == Role.JUDGE).one_or_none()
        if not judge_type:
            raise HTTPException(status_code=500, detail="Judge user type not found")
        guest_type = session.query(UserType).filter(UserType.permissions == Role.GUEST).one_or_none()
        if not guest_type:
            raise HTTPException(status_code=500, detail="Guest user type not found")
        
        builder = session.query(User).filter(User.deletion_date == None, User.user_type_id != judge_type.id, User.user_type_id != guest_type.id)
        if searchFilter:
            builder = builder.filter(User.username.ilike(f"%{searchFilter}%"))
        users: List[User] = builder.limit(limit).offset(offset).all()
        count = builder.count()
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
        is_admin_maintainer = RoleChecker.hasRole(current_user, Role.USER_MAINTAINER)
        user: User = get_object_by_id(User, session, id)
        if not user or (not is_admin_maintainer and user.id != current_user.id):
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserDTO.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def read_me(current_user: User, session: Session) -> UserDTO:
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
    


def update(id: int, updated_user: UserDTO, current_user: User, session: Session) -> UserDTO:
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
        return UserDTO.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


# def update_data(id: int, updated_user: UserLoginDTO, current_user: User, session: Session) -> UserDTO:
#     """
#     Update username and/or password by id
    
#     Args:
#         id (int):
#         updated_user (UserLoginDTO):
    
#     Returns:
#         user (UserDTO):
#     """

#     try:
#         is_admin_maintainer = RoleChecker.hasRole(current_user, Role.USER_MAINTAINER)
#         user: User = get_object_by_id(User, session, id)
#         if not user or (not is_admin_maintainer and user.id != current_user.id):
#             raise HTTPException(status_code=404, detail="User not found")
#         username_check : User = session.query(User).filter(User.username == updated_user.username).one_or_none()
#         if username_check and username_check.id != id:
#             raise HTTPException(status_code=409, detail="Username already exists")

#         password_hash, _ = _hash_password(password=updated_user.password, salt=bytes.fromhex(user.salt))

#         user.username = updated_user.username
#         user.password_hash = password_hash

#         session.commit()
#         return UserDTO.model_validate(obj=user)
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
# def update_permissions(id: int, updated_user: UserPermissionsDTO, current_user: User, session: Session) -> UserDTO:
#     """
#     Update permissions of a user by id
    
#     Args:
#         id (int):
#         updated_user (UserPermissionsDTO):
    
#     Returns:
#         user (UserDTO):
#     """

#     try:
#         user : User = get_object_by_id(User, session, id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         user.user_type_id = updated_user.user_type_id

#         session.commit()
#         return UserDTO.model_validate(obj=user)
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
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