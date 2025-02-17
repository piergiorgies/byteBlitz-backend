from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user
from app.controllers.user import list_user, read_user, read_me, delete_user, update_user, available_user_types_list
from app.schemas import get_pagination_params, PaginationParams, UserListResponse, UserCreate, UserUpdate, UserResponse
from app.database import get_session

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)



@router.get("/me", response_model=UserResponse, summary="Get the logged user", dependencies=[Depends(RoleChecker([Role.USER]))])
async def read_user_me(current_user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get the logged user
    """

    try:
        user: UserResponse = read_me(current_user, session)
        return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=UserResponse, summary="Get user by id", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER, Role.USER]))])
async def read(id: int, current_user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get user by id

    Args:
        id: int
    """

    try:
        user: UserResponse = read_user(id, current_user, session)
        return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.delete("/{id}", summary="Delete a user by id", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER, Role.USER]))])
async def delete(id: int, user=Depends(get_current_user), session=Depends(get_session)):
    """
    Delete user by id

    Args:
        id: int
    """

    try:
        deleted = delete_user(id, user, session)

        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    