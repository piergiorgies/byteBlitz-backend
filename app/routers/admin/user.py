from fastapi import APIRouter, Depends, HTTPException, Body
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user
from app.controllers.user import list_user, update_user, available_user_types_list
from app.schemas import get_pagination_params, PaginationParams, UserListResponse, UserUpdate
from app.database import get_session
from app.models import Role


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin User"],
)


@router.get("/", response_model=UserListResponse, summary="List users", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER]))])
async def list(
    pagination : PaginationParams = Depends(get_pagination_params),
    user=Depends(get_current_user),
    session=Depends(get_session)
    ):
    """
    List users

    Returns:
        JSONResponse: response
    """

    try:
        users = list_user(pagination, user, session)
        return users

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

@router.put("/{id}", summary="Update a user by id", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER]))])
async def update_user(id: int, updated_user: UserUpdate = Body(), current_user=Depends(get_current_user), session=Depends(get_session)):
    """
    Update a user by id

    Args:
        id: int
        updated_user: UserDTO

    Returns:
        JSONResponse
    """

    try:
        user = update_user(id, updated_user, current_user, session)
        return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/types/available", summary="Get available UserType", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER]))])
async def get_user_types(session=Depends(get_session)):
    """
    Get available UserType

    Returns:
        List[UserType]
    """
    try:
        return available_user_types_list(session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    