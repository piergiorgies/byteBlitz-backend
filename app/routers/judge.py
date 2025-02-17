from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.util.role_checker import JudgeChecker, RoleChecker
from app.database import get_session
from app.controllers.judge import get_versions, get_problem_info, get_judges, create_judge, delete_judge
from app.schemas import get_pagination_params, PaginationParams, JudgeCreate
from app.models.role import Role
from app.util.role_checker import get_judge


router = APIRouter(
    tags=["Judge"],
)

@router.get("/problem_versions", summary="Get the problem versions", dependencies=[Depends(JudgeChecker())])
async def get_problem_versions(session=Depends(get_session), judge=Depends(get_judge)):
    """
    Get the problem versions
    """

    try:
        # get the problem versions
        problems = get_versions(session, judge)
        return problems
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/problems/config/{id}", summary="Get the problem configuration", dependencies=[Depends(JudgeChecker())])
async def get_problem_config(id: int, session=Depends(get_session), judge=Depends(get_judge)):
    """
    Get the problem configuration
    
    Args:
        id: int
    """

    try:
        # get the problem configuration
        problem = get_problem_info(id, session, judge)
        return problem
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/judges", summary="Get the judge list", dependencies=[Depends(RoleChecker(Role.ADMIN))])
async def list_judges(pagination : PaginationParams = Depends(get_pagination_params), session=Depends(get_session)):
    """
    Get the judge list
    """

    try:
        # get the judge list
        return get_judges(pagination["limit"], pagination["offset"], pagination["search"], session)
    
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
        # create the judge
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
        # delete the judge
        delete_judge(id, session)
        return JSONResponse(status_code=200, content={"message": "Judge deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))