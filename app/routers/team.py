from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.controllers.team import create, list, delete, read, add_user, remove_user, list_users, update

from app.models import TeamDTO, ListResponse, ListDTOBase
from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    prefix="/team",
    tags=["Team"]
)

#region Team

@router.post("/", summary="Create a team", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_team(team: TeamDTO = Body(), session = Depends(get_session)):
    """
    Create a team

    Args: 
        team: TeamDTO
    
    Returns:
        JSONResponse: response
    """
    try:
        team= create(team, session)
        # return created code
        return JSONResponse(status_code=201, content={"message": "Team created successfully"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

@router.get("/",  response_model=ListResponse,summary="List teams", dependencies=[Depends(RoleChecker(["admin","user"]))])
async def list_teams(body: ListDTOBase = Body(), session = Depends(get_session)):
    """
    List teams

    Args:
        body: ListDTOBase

    Returns:
        ListResponse: response
    """
    try:
        teams = list(body, session)
        return teams
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}", summary="Delete a team by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_team(id: int, session = Depends(get_session)):
    """
    Delete a team by id

    Args:
        id: int

    Returns:
        JSONResponse: response
    """
    try:
        team = delete(id, session)

        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return JSONResponse(status_code=200, content={"message": "Team deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}", response_model=TeamDTO, summary="Get team by id", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def read_team(id: int, session = Depends(get_session)):
    """
    Get team by id

    Args:
        id: int

    Returns:
        TeamDTO: team
    """
    try:
        team = read(id, session)
        return team
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.post("/{id}/users", summary="Add a user to a team", dependencies=[Depends(RoleChecker(["admin"]))])
async def add_user_to_team(id: int, user_id: int = Body(), session=Depends(get_session)):
    """
    Add a user to a team

    Args:
        id: int
        user_id: int
    """

    try:
        added = add_user(id, user_id, session)
        if not added:
            raise HTTPException(status_code=404, detail="User or contest not found")
        return JSONResponse(status_code=201, content={"message": "User added to contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.delete("/{id}/users", summary="Remove a user from a team", dependencies=[Depends(RoleChecker(["admin"]))])
async def remove_user_from_team(id: int, user_id: int = Body(), session=Depends(get_session)):
    """
    Remove a user from a team

    Args:
        id: int
        user_id: int
    """

    try:
        removed = remove_user(id, user_id, session)
        if not removed:
            raise HTTPException(status_code=404, detail="User or contest not found")
        return JSONResponse(status_code=200, content={"message": "User removed from contest successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}/users", summary="List users in a team", response_model=ListResponse, dependencies=[Depends(RoleChecker(["admin"]))])
async def list_users_in_team(id: int, session=Depends(get_session)):
    """
    List users in a team

    Args:
        id: int
    """

    try:
        users = list_users(id, session)
        return users
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.put("/{id}", summary="Update a team by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_team(id: int, team: TeamDTO = Body(), session=Depends(get_session)):
    """
    Update team by id

    Args:
        id: int
        team: TeamDTO
    """

    try:
        updated_team = update(id, team, session)
        return JSONResponse(status_code=200, content={"message": "Team updated successfully", "team": jsonable_encoder(updated_team)})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))