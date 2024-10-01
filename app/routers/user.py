from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.user import list, read, delete, update_data, update_permissions
from app.router_util.params import pagination_params

from app.database import get_session
from app.models import ListResponse, UserDTO, UserLoginDTO, UserPermissionsDTO

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)

@router.get("/", response_model=ListResponse, summary="List users", dependencies=[Depends(RoleChecker(["admin"]))])
async def list_users(pagination : dict = Depends(pagination_params),  user=Depends(get_current_user), session=Depends(get_session)):
    """
    List users
    
    Returns:
        JSONResponse: response
    """

    try:
        users = list(pagination["limit"], pagination["offset"], user, session)
        return users
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=UserDTO, summary="Get user by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def read_user(id: int, current_user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get user by id

    Args:
        id: int
    """

    try:
        user: UserDTO = read(id, current_user, session)
        return user
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}", summary="Delete a user by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_user(id: int, user=Depends(get_current_user), session=Depends(get_session)):
    """
    Delete user by id
    
    Args:
        id: int
    """

    try:
        deleted = delete(id, user, session)

        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        
        return JSONResponse(status_code=200, content={"message": "User deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.patch("/{id}/data", summary= "Update username and/or password of a user by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_user_data(id: int, updated_user: UserLoginDTO = Body(), current_user=Depends(get_current_user), session=Depends(get_session)): 
    """
    Update username and/or password of a user by id
    
    Args:
        id: int
        updated_user: UserLoginDTO

    Returns:
        JSONResponse
    """

    try:
        user = update_data(id, updated_user, current_user, session)
        return JSONResponse(status_code=200, content={"message": "User data updated successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.patch("/{id}/permissions", summary= "Update permissions of a user by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_user_permissions(id: int, updated_user: UserPermissionsDTO = Body(), current_user=Depends(get_current_user), session=Depends(get_session)): 
    """
    Update permissions of user by id
    
    Args:
        id: int
        updated_user: UserPermissionsDTO

    Returns:
        JSONResponse
    """

    try:
        user = update_permissions(id, updated_user, current_user, session)
        return JSONResponse(status_code=200, content={"message": "User permissions updated successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))