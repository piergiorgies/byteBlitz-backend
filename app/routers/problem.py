from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.problem import list, read, create, delete

from app.models import ListResponse, problem
from app.database import get_session
from app.models.base_dto import ListDTOBase
from app.models import ProblemDTO

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)

#region Problem

#TODO: manage problem visibility --> admin: all problems, user: only public problems
@router.get("/", response_model=ListResponse, summary="List problems", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def list_problems(body: ListDTOBase = Body(),  user=Depends(get_current_user), session=Depends(get_session)):
    """
    List problems
    
    Returns:
        JSONResponse: response
    """

    try:
        problems = list(body, user, session)
        return problems
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=ProblemDTO, summary="Get problem by id", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def read_problem(id: int, user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get problem by id

    Args:
        id: int
    """

    try:
        problem: ProblemDTO = read(id, user, session)
        return problem
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/", summary="Create a problem", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_problem(problem: ProblemDTO = Body(), session=Depends(get_session)):
    """
    Create a problem
    
    Args:
        problem: ProblemDTO
    
    returns:
        JSONResponse: response
    """

    try:
        problem = create(problem, session)
        return JSONResponse(status_code=201, content={"message": "Problem created successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}", summary="Delete a problem by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_problem(id: int, session=Depends(get_session)):
    """
    Delete contest by id
    
    Args:
        id: int
    """

    try:
        deleted = delete(id, session)

        if not deleted:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return JSONResponse(status_code=200, content={"message": "Problem deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
#endregion