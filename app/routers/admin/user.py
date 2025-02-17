from fastapi import APIRouter, Depends, HTTPException, Body
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user
from app.controllers.admin.user import available_user_types_list, read_user, delete_user, update_user, list_user, create_user
from app.schemas import get_pagination_params, PaginationParams, UserListResponse, UserUpdate, UserCreate
from app.database import get_session
from app.models import Role
from app.schemas import UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse


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
    

@router.get("/{id}", response_model=UserResponse, summary="Get user by id", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER]))])
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
    
@router.delete("/{id}", summary="Delete a user by id", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER]))])
async def delete(id: int, session=Depends(get_session)):
    """
    Delete user by id

    Args:
        id: int
    """

    try:
        deleted = delete_user(id, session)

        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")

        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/", summary="Create a user", dependencies=[Depends(RoleChecker([Role.USER_MAINTAINER]))])
async def create(user: UserCreate = Body(), session=Depends(get_session)):
    """
    Create a user

    Args:
        user: UserCreate
    """

    try:
        created_user = create_user(user, session)
        return JSONResponse(status_code=201, content={"message": "User created successfully", "id": created_user.id})

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))