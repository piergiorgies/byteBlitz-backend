from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from app.controllers.contest import create, list, read, delete, update
from app.controllers.contest import add_user, remove_user, list_users, add_team, remove_team, list_teams
from app.models import ContestDTO, ListDTOBase, ListResponse
from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    prefix="/contests",
    tags=["Contests"]
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
        contests = list(body, session)
        return contests
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=ContestDTO, summary="Get contest by id", dependencies=[Depends(RoleChecker(["user"]))])
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

@router.delete("/{id}", summary="Delete a contest by id", dependencies=[Depends(RoleChecker(["user"]))])
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
    
@router.put("/{id}", summary="Update a contest by id", dependencies=[Depends(RoleChecker(["user"]))])
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
        return JSONResponse(status_code=201, content={"message": "Contest updated successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.post("/{id}/users", summary="Add a user to a contest", dependencies=[Depends(RoleChecker(["user"]))])
async def add_user_to_contest(id: int, user_id: int = Body(), session=Depends(get_session)):
    """
    Add a user to a contest

    Args:
        id: int
        user_id: int
    """

    try:
        # add user to contest
        added = add_user(id, user_id, session)
        if not added:
            raise HTTPException(status_code=404, detail="User or contest not found")

        return JSONResponse(status_code=201, content={"message": "User added to contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.delete("/{id}/users", summary="Remove a user from a contest", dependencies=[Depends(RoleChecker(["user"]))])
async def remove_user_from_contest(id: int, user_id: int = Body(), session=Depends(get_session)):
    """
    Remove a user from a contest

    Args:
        id: int
        user_id: int
    """

    try:
        # remove user from contest
        removed = remove_user(id, user_id, session)
        if not removed:
            raise HTTPException(status_code=404, detail="User or contest not found")

        return JSONResponse(status_code=200, content={"message": "User removed from contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}/users", response_model=ListResponse, summary="List users in a contest", dependencies=[Depends(RoleChecker(["user"]))])
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
    
@router.post("/{id}/teams", summary="Add a team to a contest", dependencies=[Depends(RoleChecker(["user"]))])
async def add_team_to_contest(id: int, team_id: int = Body(), session=Depends(get_session)):
    """
    Add a team to a contest

    Args:
        id: int
        team_id: int
    """

    try:
        # add team to contest
        added = add_team(id, team_id, session)
        if not added:
            raise HTTPException(status_code=404, detail="Team or contest not found")

        return JSONResponse(status_code=201, content={"message": "Team added to contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}/teams", summary="Remove a team from a contest", dependencies=[Depends(RoleChecker(["user"]))])
async def remove_team_from_contest(id: int, team_id: int = Body(), session=Depends(get_session)):
    """
    Remove a team from a contest

    Args:
        id: int
        team_id: int
    """

    try:
        # remove team from contest
        removed = remove_team(id, team_id, session)
        if not removed:
            raise HTTPException(status_code=404, detail="Team or contest not found")

        return JSONResponse(status_code=200, content={"message": "Team removed from contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/teams", response_model=ListResponse, summary="List teams in a contest", dependencies=[Depends(RoleChecker(["user"]))])
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