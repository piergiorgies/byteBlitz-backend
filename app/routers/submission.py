from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.auth_util.role import Role
from app.controllers.submission import create, accept, save_total

from app.models import SubmissionDTO, SubmissionTestCaseDTO, ResultDTO
from app.database import get_session
from app.auth_util.role_checker import RoleChecker, JudgeChecker
from app.auth_util.jwt import get_current_user

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

@router.post("/", summary="Submit a solution to a problem",  dependencies=[Depends(RoleChecker([Role.USER]))])
async def submit_solution(submission: SubmissionDTO = Body(), session = Depends(get_session), user = Depends(get_current_user)):
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


@router.post("/{id}", summary="Accept the result of a submission", dependencies=[Depends(JudgeChecker())])
async def accept_submission(id: int, body: SubmissionTestCaseDTO = Body(), session = Depends(get_session)):
    """
    Accept the result of a submission

    Args:
        id (int): The submission id
        body (SubmissionTestCase): The submission test case data

    Returns:
        JSONResponse: The response
    """
    try:
        accepted = accept(id, body, session)
        
        return JSONResponse(content={"message": "submission accepted successfully"}, status_code=200)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/{id}/total", summary="Get the total score of a submission", dependencies=[Depends(JudgeChecker())])
async def save_total(id: int, result_id: ResultDTO = Body(), session = Depends(get_session)):
    """
    Get the total test case of a submission

    Args:
        id (int): The submission id

    Returns:
        JSONResponse: The response
    """
    try:
        save_total(id, result_id, session)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")