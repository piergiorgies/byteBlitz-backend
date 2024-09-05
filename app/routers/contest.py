from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from app.controllers.contest import create, list as list_controller
from app.models import ContestDTO, ListDTOBase, ListResponse
from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    prefix="/contests",
    tags=["contests"]
)

@router.post("/", summary="Create a contest", dependencies=[Depends(RoleChecker(["user"]))])
async def create_contest(contest: ContestDTO = Body(), session=Depends(get_session)):
    """
    Create a contest
    
    Args:
        contest: ContestDTO
    
    Returns:
        JSONResponse: response
    """

    try:
        contest = create(contest, session)
        # return created code
        return JSONResponse(status_code=201, content={"message": "Contest created successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/", response_model=ListResponse, summary="List contests", dependencies=[Depends(RoleChecker(["user"]))])
async def list_contests(body: ListDTOBase = Body(), session=Depends(get_session)):
    """
    List contests
    
    Returns:
        JSONResponse: response
    """

    try:
        contests = list_controller(body, session)
        return contests
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    