from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.models.role import Role
from app.controllers.submission import create, get_submission_results, submission_by_problem

from app.schemas import SubmissionCreate
from app.database import get_session
from app.schemas import ProblemSubmissions, PaginationParams, get_pagination_params
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

@router.get("/results", summary="Return a list of the saved possible states of a submission",  dependencies=[Depends(RoleChecker([Role.USER]))])
async def get_submission_result_types(session = Depends(get_session)):
    """
    Return a list of the saved possible states of a submission

    Returns:
        JSONResponse: The response
    """

    try:
        return get_submission_results(session)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", summary="Submit a solution to a problem",  dependencies=[Depends(RoleChecker([Role.USER]))])
async def submit_solution(submission: SubmissionCreate = Body(), session = Depends(get_session), user = Depends(get_current_user)):
    """
    Submit a solution to a problem

    Args:
        submission (SubmissionDTO): The submission data

    Returns:
        JSONResponse: The response
    """
    try:
        submission = create(submission, session, user)

        return JSONResponse(content={"message": "submission sent successfully"}, status_code=201)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/problem/{problem_id}", response_model=ProblemSubmissions, summary="Get all submissions sent", dependencies=[Depends(RoleChecker([Role.USER]))])
async def get_submissions_by_problem(problem_id: int, pagination: PaginationParams = Depends(get_pagination_params), user = Depends(get_current_user), session = Depends(get_session)):
    """
    Get all submissions sent

    Args:
        problem_id (int): The problem id

    Returns:
        JSONResponse: The response
    """

    try:
        return submission_by_problem(pagination, problem_id, user, session)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
