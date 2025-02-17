from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.models.role import Role
from app.controllers.submission import create

from app.schemas import SubmissionCreate
from app.database import get_session
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

@router.post("/", summary="Submit a solution to a problem",  dependencies=[Depends(RoleChecker([Role.USER]))])
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
