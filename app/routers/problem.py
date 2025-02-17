from fastapi import APIRouter, Depends, HTTPException

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user
from app.controllers.problem import read
from app.schemas import get_pagination_params, PaginationParams, ProblemListResponse, ProblemRead
from app.database import get_session

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)

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
