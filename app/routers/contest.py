from fastapi import APIRouter, Depends, HTTPException
from app.models.role import Role
from app.controllers.contest import get_scoreboard, list_with_info, read_past, read_upcoming, read_ongoing, register_to_contest
from app.schemas import ContestScoreboard
from app.schemas import ContestRead, ContestInfos, UpcomingContest, PastContest, ContestUserInfo
from app.models.mapping import User
from app.database import get_session
from app.util.jwt import get_current_user
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
        contest: UpcomingContest = read_upcoming(id, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/ongoing", summary="Info about ongoing contest", dependencies=[Depends(RoleChecker([Role.USER]))])
async def get_ongoing_contest(id: int, user: User = Depends(get_current_user), session=Depends(get_session)):
    """
    Get ongoing contest info

    Args:
        id: int
    """
    try:
        contest: ContestRead = read_ongoing(id, user, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/{id}/register", summary="Register to a contest", dependencies=[Depends(RoleChecker([Role.USER]))])
async def register(id: int, user: User = Depends(get_current_user), session=Depends(get_session)):
    """
    Register to a contest

    Args:
        id: int
    """
    try:
        return register_to_contest(id, user, session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

    