from fastapi import APIRouter, Body, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from app.schemas import ContestCreate, ContestUpdate, ContestListResponse, ContestRead, PaginationParams, get_pagination_params
from app.controllers.admin.contest import create, delete, update
from app.database import get_session
from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.schemas import ContestListResponse
from app.controllers.admin.contest import list, read
from app.util.jwt import get_current_user

router = APIRouter(
    prefix="/admin/contests",
    tags=["Admin Contest"]
)

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
        return JSONResponse(status_code=201, content={"message": "Contest created successfully", "id": contest.id})
        
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

@router.get("/", response_model=ContestListResponse, summary="List contests", dependencies=[Depends(RoleChecker([Role.CONTEST_MAINTAINER]))])
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


@router.get("/{id}", response_model=ContestRead, summary="Get contest by id", dependencies=[Depends(RoleChecker([Role.CONTEST_MAINTAINER]))])
async def read_contest(id: int = Path(..., title="the Id of the contest"), session=Depends(get_session)):
    """
    Get contest by id

    Args:
        id: int
    """

    try:
        contest: ContestRead = read(id, session)
        return contest
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))