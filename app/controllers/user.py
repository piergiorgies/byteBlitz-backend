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

