from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.problem import list, read

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
    
#endregion