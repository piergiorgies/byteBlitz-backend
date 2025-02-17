from fastapi import APIRouter, Depends, HTTPException, Body, Path
from fastapi.responses import JSONResponse
from typing import List

from app.util.jwt import get_current_user
from app.models.role import Role
from app.controllers.contest import create, list, read, delete, update
from app.controllers.contest import get_scoreboard, list_with_info, read_past, read_upcoming
from app.schemas import get_pagination_params, PaginationParams
from app.schemas import ContestScoreboard, ContestListResponse
from app.schemas import ContestCreate, ContestUpdate, ContestRead, ContestInfos

from app.database import get_session
from app.util.role_checker import RoleChecker

router = APIRouter(
    prefix="/contests",
    tags=["Contests"]
)

@router.get("/info", response_model=ContestInfos, summary="List contests info", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def list_contests_info(session=Depends(get_session)):
    """
    List contests info

    Returns:
        ContestsInfo: contests
    """

    try:
        contests = list_with_info(session)
        return contests
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/", response_model=ContestListResponse, summary="List contests", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def list_contests(pagination : PaginationParams = Depends(get_pagination_params), user = Depends(get_current_user), session=Depends(get_session)):
    """
    List contests
    
    Returns:
        JSONResponse: response
    """

    try:
        contests = list(pagination.limit, pagination.offset, pagination.search_filter, user, session)
        return contests
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


@router.get("/{id}", response_model=ContestRead, summary="Get contest by id", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def read_contest(id: int = Path(..., title="the Id of the contest"), user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get contest by id

    Args:
        id: int
    """

    try:
        contest: ContestRead = read(id, user, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


@router.post("/{id}/scoreboard", summary="Return the contest scoreboard", dependencies=[Depends(RoleChecker([Role.USER]))])
async def add_user_to_contest(id: int, session=Depends(get_session)):
    """
    Get the current scoreboard for a specific contest

    Args:
        id (int) : the id of the contest
    """

    try:
        scoreboard : ContestScoreboard = get_scoreboard(id, session)
        return scoreboard
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/past", summary="Info about past contest", dependencies=[Depends(RoleChecker([Role.USER]))])
async def get_past_contest(id: int, session=Depends(get_session)):
    """
    Get past contest info

    Args:
        id: int
    """

    try:
        contest: ContestRead = read_past(id, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}/upcoming", summary="Info about upcoming contest", dependencies=[Depends(RoleChecker([Role.USER]))])
async def get_upcoming_contest(id: int, session=Depends(get_session)):
    """
    Get upcoming contest info
    
    Args:
        id: int
    """
    try:
        contest: ContestRead = read_upcoming(id, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
