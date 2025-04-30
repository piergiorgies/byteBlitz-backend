from fastapi import APIRouter, Depends, HTTPException

from app.controllers.admin.problem import list_available_languages
from app.models.role import Role
from app.schemas import PaginationParams, get_pagination_params
from app.schemas.problem import ProblemRead
from app.util.jwt import get_current_user
from app.util.role_checker import RoleChecker
from app.controllers.problem import list_visible_problems, read
from app.schemas import ProblemListResponse
from app.database import get_session

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)


@router.get("/", response_model=ProblemListResponse, summary="List problems", dependencies=[Depends(RoleChecker([Role.USER]))])
async def list_problems(pagination: PaginationParams = Depends(get_pagination_params), session=Depends(get_session)):
    """
    List problems

    Returns:
        ProblemListResponse: problems
    """

    try:
        problems = list_visible_problems(pagination, session)
        return problems

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/{id}", response_model=ProblemRead, summary="Get problem by id", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def read_problem(id: int, user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get problem by id

    Args:
        id: int
    """

    try:
        problem: ProblemRead = read(id, user, session)
        return problem
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/languages/available", summary="Get the available languages", dependencies=[Depends(RoleChecker([Role.GUEST]))])
async def list_languages(session=Depends(get_session)):
    """
    Get all available languages

    Returns:
        JSONResponse
    """

    try:
        languages = list_available_languages(session)
        return languages
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
