from fastapi import APIRouter, Depends, HTTPException
from app.models.role import Role
from app.schemas import PaginationParams, get_pagination_params
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user
from app.controllers.user import read_me, get_profile_info, get_submission_history
from app.schemas import UserResponse, ProfileResponse, SubmissionHistory
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


@router.get("/profile/info", response_model=ProfileResponse, summary="Get information of the logged user", dependencies=[Depends(RoleChecker([Role.USER]))])
async def read_user_profile(current_user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get information of the logged user
    """

    try:
        response: ProfileResponse = get_profile_info(current_user, session)
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

@router.get("/sub_history", response_model=SubmissionHistory, summary="Get the submission history of the logged user", dependencies=[Depends(RoleChecker([Role.USER]))])
async def read_user_sub_history(pagination : PaginationParams = Depends(get_pagination_params), current_user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get the submission history of the logged user
    """

    try:
        response: SubmissionHistory = get_submission_history(pagination, current_user, session)
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))