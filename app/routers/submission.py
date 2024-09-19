from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.controllers.submission import create

from app.models.submission import SubmissionDTO
from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

@router.post("/", summary="Submit a solution to a problem", dependencies=[Depends(RoleChecker(["admin"]))])
async def submit_solution(submission: SubmissionDTO = Body(), session = Depends(get_session)):
    """
    Submit a solution to a problem

    Args:
        submission (SubmissionDTO): The submission data

    Returns:
        JSONResponse: The response
    """
    try:
        submission = create(submission, session)

        return JSONResponse(content={"message": "submission sent successfully"}, status_code=201)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
