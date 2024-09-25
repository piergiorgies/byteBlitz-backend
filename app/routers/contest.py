from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List

from app.controllers.contest import create, list, read, delete, update
from app.controllers.contest import add_users, remove_users, list_users
from app.controllers.contest import add_teams, remove_teams, list_teams
from app.controllers.contest import list_problems, add_problems, remove_problems, update_problem

from app.models import ContestDTO, ListDTOBase, ListResponse, ContestProblemDTO, IdListDTO
from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    prefix="/contests",
    tags=["Contests"]
)

#region Contest

@router.post("/", summary="Create a contest", dependencies=[Depends(RoleChecker(["admin"]))])
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
    
@router.get("/", response_model=ListResponse, summary="List contests", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def list_contests(body: ListDTOBase = Body(), session=Depends(get_session)):
    """
    List contests
    
    Returns:
        JSONResponse: response
    """

    try:
        contests = list(body, session)
        return contests
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=ContestDTO, summary="Get contest by id", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def read_contest(id: int, session=Depends(get_session)):
    """
    Get contest by id

    Args:
        id: int
    """

    try:
        contest: ContestDTO = read(id, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}", summary="Delete a contest by id", dependencies=[Depends(RoleChecker(["admin"]))])
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
    
@router.put("/{id}", summary="Update a contest by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_contest(id: int, contest: ContestDTO = Body(), session=Depends(get_session)):
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

#region Contest User

@router.post("/{id}/users", summary="Add a list of user to a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def add_user_to_contest(id: int, user_ids: IdListDTO = Body(), session=Depends(get_session)):
    """
    Add a user to a contest

    Args:
        id: int
        user_id: int
    """

    try:
        # add user to contest
        added = add_users(id, user_ids.ids, session)
        if not added:
            raise HTTPException(status_code=404, detail="Users or contest not found")

        return JSONResponse(status_code=201, content={"message": "Users added to contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.delete("/{id}/users", summary="Remove a list of user from a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def remove_user_from_contest(id: int, user_ids: IdListDTO = Body(), session=Depends(get_session)):
    """
    Remove a user from a contest

    Args:
        id: int
        user_id: int
    """

    try:
        # remove user from contest
        removed = remove_users(id, user_ids.ids, session)
        if not removed:
            raise HTTPException(status_code=404, detail="Users or contest not found")

        return JSONResponse(status_code=200, content={"message": "Users removed from contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}/users", response_model=ListResponse, summary="List users in a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def list_users_in_contest(id: int, session=Depends(get_session)):
    """
    List users in a contest

    Args:
        id: int
    """

    try:
        # list users in contest
        users = list_users(id, session)
        return users
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Contest Team

@router.post("/{id}/teams", summary="Add a list of team to a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def add_team_to_contest(id: int, team_ids: IdListDTO = Body(), session=Depends(get_session)):
    """
    Add a team to a contest

    Args:
        id: int
        team_id: int
    """

    try:
        # add team to contest
        added = add_teams(id, team_ids.ids, session)
        if not added:
            raise HTTPException(status_code=404, detail="Team or contest not found")

        return JSONResponse(status_code=201, content={"message": "Team added to contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}/teams", summary="Remove a list of team from a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def remove_team_from_contest(id: int, team_ids: IdListDTO = Body(), session=Depends(get_session)):
    """
    Remove a team from a contest

    Args:
        id: int
        team_id: int
    """

    try:
        # remove team from contest
        removed = remove_teams(id, team_ids.ids, session)
        if not removed:
            raise HTTPException(status_code=404, detail="Team or contest not found")

        return JSONResponse(status_code=200, content={"message": "Team removed from contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/teams", response_model=ListResponse, summary="List teams in a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def list_teams_in_contest(id: int, session=Depends(get_session)):
    """
    List teams in a contest

    Args:
        id: int
    """

    try:
        # list teams in contest
        teams = list_teams(id, session)
        return teams
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Contest Problem

@router.post("/{id}/problems", summary="Add a list of problems to a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def add_problem_to_contest(id: int, contest_problems: List[ContestProblemDTO] = Body(), session=Depends(get_session)):
    """
    Add a problem to a contest

    Args:
        id: int
        problem_id: int
    """

    try:
        # add problem to contest
        added = add_problems(id, contest_problems, session)
        if not added:
            raise HTTPException(status_code=404, detail="Problem or contest not found")

        return JSONResponse(status_code=201, content={"message": "Problem added to contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.delete("/{id}/problems", summary="Remove a problem from a contest", dependencies=[Depends(RoleChecker(["admin"]))])
async def remove_problem_from_contest(id: int, problem_ids: IdListDTO = Body(), session=Depends(get_session)):
    """
    Remove a problem from a contest

    Args:
        id: int
        problem_id: int
    """

    try:
        # remove problem from contest
        removed = remove_problems(id, problem_ids.ids, session)
        if not removed:
            raise HTTPException(status_code=404, detail="Problem or contest not found")

        return JSONResponse(status_code=200, content={"message": "Problem removed from contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}/problems", response_model=ListResponse, summary="List problems in a contest", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def list_problems_in_contest(id: int, session=Depends(get_session)):
    """
    List problems in a contest

    Args:
        id: int
    """

    try:
        # list problems in contest
        problems = list_problems(id, session)
        return problems
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.patch("/{id}/problems", summary="Update publication delay of a contest problem", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_problem_publication_delay(id: int, body: ContestProblemDTO = Body(), session=Depends(get_session)):
    """
    Update publication delay of a problem in a contest

    Args:
        id: int
        problem_id: int
        publication_delay: int
    """

    try:
        # update publication delay of problem in contest
        updated = update_problem(id, body, session)
        if not updated:
            raise HTTPException(status_code=404, detail="Problem or contest not found")

        return JSONResponse(status_code=200, content={"message": "Problem publication delay updated successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
#endregion

