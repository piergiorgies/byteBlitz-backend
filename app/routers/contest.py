from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List

from app.auth_util.jwt import get_current_user
from app.models.role import Role
from app.controllers.contest import create, list, read, delete, update
from app.controllers.contest import get_scoreboard
# from app.controllers.contest import list_problems
from app.models.params import pagination_params
from app.models import ContestScoreboardDTO, ListResponse, IdListDTO
from app.models import ContestCreate, ContestUpdate, ContestRead

from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    prefix="/contests",
    tags=["Contests"]
)

#region Contest

@router.post("/", summary="Create a contest", dependencies=[Depends(RoleChecker([Role.CONTEST_MAINTAINER]))])
async def create_contest(contest: ContestCreate = Body(), session=Depends(get_session)):
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
        return JSONResponse(status_code=201, content={"message": "Contest created successfully", "id": contest.id})
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/", response_model=ListResponse, summary="List contests", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def list_contests(pagination : dict = Depends(pagination_params), user = Depends(get_current_user), session=Depends(get_session)):
    """
    List contests
    
    Returns:
        JSONResponse: response
    """

    try:
        contests = list(pagination["limit"], pagination["offset"], pagination["search"], user, session)
        return contests
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=ContestRead, summary="Get contest by id", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def read_contest(id: int, user=Depends(get_current_user), session=Depends(get_session)):
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

@router.delete("/{id}", summary="Delete a contest by id", dependencies=[Depends(RoleChecker([Role.CONTEST_MAINTAINER]))])
async def delete_contest(id: int, session=Depends(get_session)):
    """
    Delete contest by id

    Args:
        id: int
    """

    try:
        deleted = delete(id, session)

        if not deleted:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        return JSONResponse(status_code=200, content={"message": "Contest deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.put("/{id}", summary="Update a contest by id", dependencies=[Depends(RoleChecker([Role.CONTEST_MAINTAINER]))])
async def update_contest(id: int, contest: ContestUpdate = Body(), session=Depends(get_session)):
    """
    Update contest by id

    Args:
        id: int
        contest: ContestDTO
    """

    try:
        contest = update(id, contest, session)
        # return created code
        return JSONResponse(status_code=200, content={"message": "Contest updated successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
#endregion

#region Contest Scoreboard

@router.post("/scoreboard", summary="Add a list of user to a contest", dependencies=[Depends(RoleChecker([Role.CONTEST_MAINTAINER]))])
async def add_user_to_contest(id: int, user_ids: IdListDTO = Body(), session=Depends(get_session)):
    """
    Get the current scoreboard for a specific contest

    Args:
        id (int) : the id of the contest
    """

    try:
        scoreboard : ContestScoreboardDTO = get_scoreboard(id, session)
        return scoreboard
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


# @router.get("/{contest_id}/scoreboardV2", response_model=List[ContestScoreboardDTO])
# async def get_scoreboard(contest_id: int, session = Depends(get_session)):
#     try:
#         # Query the contest_scoreboard view
#         scoreboard: ContestScoreboardDTO = get_scoreboardV2(contest_id, session)

#         if not scoreboard:
#             raise HTTPException(status_code=404, detail="Scoreboard not found for this contest")

#         return scoreboard

#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An error occurred while fetching the scoreboard: " + str(e))
#endregion

#region Contest Team

# @router.post("/{id}/teams", summary="Add a list of team to a contest", dependencies=[Depends(RoleChecker(["admin"]))])
# async def add_team_to_contest(id: int, team_ids: IdListDTO = Body(), session=Depends(get_session)):
#     """
#     Add a team to a contest

#     Args:
#         id: int
#         team_id: int
#     """

#     try:
#         # add team to contest
#         added = add_teams(id, team_ids.ids, session)
#         if not added:
#             raise HTTPException(status_code=404, detail="Team or contest not found")

#         return JSONResponse(status_code=201, content={"message": "Team added to contest successfully"})
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

# @router.delete("/{id}/teams", summary="Remove a list of team from a contest", dependencies=[Depends(RoleChecker(["admin"]))])
# async def remove_team_from_contest(id: int, team_ids: IdListDTO = Body(), session=Depends(get_session)):
#     """
#     Remove a team from a contest

#     Args:
#         id: int
#         team_id: int
#     """

#     try:
#         # remove team from contest
#         removed = remove_teams(id, team_ids.ids, session)
#         if not removed:
#             raise HTTPException(status_code=404, detail="Team or contest not found")

#         return JSONResponse(status_code=200, content={"message": "Team removed from contest successfully"})
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

# @router.get("/{id}/teams", response_model=ListResponse, summary="List teams in a contest", dependencies=[Depends(RoleChecker(["admin"]))])
# async def list_teams_in_contest(id: int, session=Depends(get_session)):
#     """
#     List teams in a contest

#     Args:
#         id: int
#     """

#     try:
#         # list teams in contest
#         teams = list_teams(id, session)
#         return teams
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion


# @router.get("/{id}/problems", response_model=ListResponse, summary="List problems in a contest", dependencies=[Depends(RoleChecker([Role.GUEST]))])
# async def list_problems_in_contest(id: int, user=Depends(get_current_user), session=Depends(get_session)):
#     """
#     List problems in a contest

#     Args:
#         id: int
#     """

#     try:
#         # list problems in contest
#         problems = list_problems(id, user, session)
#         return problems
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


