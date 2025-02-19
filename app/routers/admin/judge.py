from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import JudgeCreate, PaginationParams, get_pagination_params
from app.controllers.admin.judge import get_judges, create_judge, delete_judge
from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.database import get_session

router = APIRouter(
    tags=["Judge"],
    prefix="/admin"
)


@router.get("/judges", summary="Get the judge list", dependencies=[Depends(RoleChecker(Role.ADMIN))])
async def list_judges(pagination : PaginationParams = Depends(get_pagination_params), session=Depends(get_session)):
    """
    Get the judge list
    """

    try:
        return get_judges(pagination.limit, pagination.offset, pagination.search_filter, session)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.post("/judges", summary="Create a new judge", dependencies=[Depends(RoleChecker(Role.ADMIN))])
async def create(judge: JudgeCreate, session=Depends(get_session)):
    """
    Create a new judge
    """
    try:
        response, status_code = create_judge(judge, session)
        return JSONResponse(status_code=status_code, content=response)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.delete("/judges/{id}", summary="Delete a judge", dependencies=[Depends(RoleChecker(Role.ADMIN))])
async def delete(id: int, session=Depends(get_session)):
    """
    Delete a judge
    
    Args:
        id: int
    """
    try:
        delete_judge(id, session)
        return JSONResponse(status_code=200, content={"message": "Judge deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
