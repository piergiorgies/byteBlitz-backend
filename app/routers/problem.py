from fastapi import APIRouter, Depends, HTTPException

from app.models.role import Role
from app.schemas import PaginationParams, get_pagination_params
from app.util.role_checker import RoleChecker
from app.controllers.problem import list_visible_problems
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