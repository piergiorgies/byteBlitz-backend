from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ListDTOBase, ListResponse, User, UserDTO

#TODO: aggiungere controlli di user type (cosa può fare per esempio uno user sul suo stesso account)

def list(body: ListDTOBase, user: User, session: Session) -> ListResponse:
    """
    List all users
    
    Args:
        body (ListDTOBase):
        user (User):
        session (Session):
    
    Returns:
        [ListResponse]: list of users
    """
    #TODO: show password hash or not ?? join user_type_id with code ??
    try:
        builder = QueryBuilder(User, session, body.limit, body.offset)
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
    
def update(id: int, updated_user: UserDTO, current_user: User, session: Session) -> UserDTO:
    """
    Update user by id
    
    Args:
        id (int):
        updated_user (UserDTO):
    
    Returns:
        user (UserDTO):
    """

    try:
        user : User = get_object_by_id(User, session, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        username = session.query(User).filter(User.username == updated_user.username).one_or_none()
        email = session.query(User).filter(User.email == updated_user.email).one_or_none()
        if email or username:
            raise HTTPException(status_code=409, detail="Email or username already exist")

        user.username = updated_user.username
        user.email = updated_user.email
        #TODO: password hashing

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