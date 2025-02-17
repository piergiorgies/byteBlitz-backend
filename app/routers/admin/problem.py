from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import ProblemCreate, ProblemUpdate
from app.controllers.admin.problem import create, delete, update, list_available_languages
from app.database import get_session
from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user

router = APIRouter(
    prefix="/admin/problems",
    tags=["Admin Problem"],
)


@router.post("/", summary="Create a problem", dependencies=[Depends(RoleChecker([Role.PROBLEM_MAINTAINER]))])
async def create_problem(problem: ProblemCreate = Body(), user=Depends(get_current_user), session=Depends(get_session)):
    """
    Create a problem
    
    Args:
        problem: ProblemDTO
    
    returns:
        JSONResponse: response
    """

    try:
        problem = create(problem, user, session)
        return JSONResponse(status_code=201, content={"message": "Problem created successfully", "created_id": problem.id})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.delete("/{id}", summary="Delete a problem by id", dependencies=[Depends(RoleChecker([Role.PROBLEM_MAINTAINER]))])
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

@router.put("/{id}", summary= "Update a problem by id", dependencies=[Depends(RoleChecker([Role.PROBLEM_MAINTAINER]))])
async def update_problem(id: int, problem: ProblemUpdate = Body(), session=Depends(get_session)): 
    """
    Update problem by id
    
    Args:
        id: int
        problem: ProblemDTO

    Returns:
        JSONResponse
    """

    try:
        problem = update(id, problem, session)
        return JSONResponse(status_code=200, content={"message": "Problem update successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/languages/available", summary="Get the available languages", dependencies=[Depends(RoleChecker([Role.PROBLEM_MAINTAINER]))])
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

