from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.util.role_checker import JudgeChecker
from app.database import get_session
from app.controllers.judge import get_versions, get_problem_info, accept, save_total as save_total_judge
from app.schemas import SubmissionTestCaseResult, SubmissionCompleteResult
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
    

@router.post("/submissions/{id}", summary="Accept the result of a submission", dependencies=[Depends(JudgeChecker())])
async def accept_submission(id: int, body: SubmissionTestCaseResult = Body(), session = Depends(get_session)):
    """
    Accept the result of a submission

    Args:
        id (int): The submission id
        body (SubmissionTestCase): The submission test case data

    Returns:
        JSONResponse: The response
    """
    try:
        accepted = await accept(id, body, session)
        
        return JSONResponse(content={"message": "submission accepted successfully"}, status_code=200)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/submissions/{id}/total", summary="Get the total score of a submission", dependencies=[Depends(JudgeChecker())])
async def save_total(id: int, result_id: SubmissionCompleteResult = Body(), session = Depends(get_session)):
    """
    Get the total test case of a submission

    Args:
        id (int): The submission id

    Returns:
        JSONResponse: The response
    """
    try:
        await save_total_judge(id, result_id, session)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
