from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.models.role import Role
from app.controllers.submission import create, get_submission_results

from app.schemas import SubmissionCreate
from app.database import get_session
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
