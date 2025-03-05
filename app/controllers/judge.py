from fastapi import HTTPException
from hashlib import sha256
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.mapping import Problem, User, UserType
from app.database import get_object_by_id_joined_with
from app.models.role import Role
from app.models.mapping import Submission, SubmissionResult, SubmissionTestCase, SubmissionTestCase
from app.schemas import JudgeResponse, JudgeCreate, JudgeListResponse, JudgeProblem, Constraint, TestCase, SubmissionTestCaseResult
from app.database import get_object_by_id
from app.schemas.submission import WSResult
from app.util.websocket import websocket_manager

#regiorn Judge

def get_versions(session: Session, judge: User):
    """
    Get the problem versions
    """

    try:
        problems = session.query(Problem).all()
        response = {}
        for problem in problems:
            response[problem.id] = problem.config_version_number

        judge.registered_at = datetime.now()
        session.commit()

        return response
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def get_problem_info(id: int, session: Session, judge: User):
    """
    Get the problem configuration
    
    Args:
        id: int
    """

    try:
        # problem: Problem = get_object_by_id_joined_with(Problem, session, id, [Problem.constraints])
        problem: Problem = get_object_by_id(Problem, session, id)

        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        # serialize the problem
        problem_dto = JudgeProblem.model_validate(obj=problem)
        problem_dto.constraints = []
        for constraint in problem.constraints:
            problem_dto.constraints.append(
                Constraint(
                    language_name=constraint.language.name, 
                    language_id=constraint.language_id, 
                    memory_limit=constraint.memory_limit, 
                    time_limit=constraint.time_limit
                )
            )
        # problem_dto.constraints = [Constraint.model_validate(obj=constraint) for constraint in problem.constraints]
        problem_dto.test_cases = [TestCase.model_validate(obj=test_case) for test_case in problem.test_cases]

        judge.registered_at = datetime.now()
        session.commit()
        
        return problem_dto
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

async def accept(submission_id: int, submission_test_case: SubmissionTestCaseResult, session: Session):
    try:
        # check if the submission exists
        submission: Submission = get_object_by_id(Submission, session, submission_id)
        if not submission:
            raise HTTPException(status_code=400, detail="Submission not found")
        
        result: SubmissionResult = get_object_by_id(SubmissionResult, session, submission_test_case.result_id)

        if not result:
            raise HTTPException(status_code=400, detail="Result not found")

        submission_test_case = SubmissionTestCase(
            submission=submission,
            result=result,
            result_id=submission_test_case.result_id,
            number=submission_test_case.number,
            notes=submission_test_case.notes,
            memory=submission_test_case.memory,
            time=submission_test_case.time
        )

        session.add(submission_test_case)
        session.commit()

        ws_message = WSResult.model_validate(obj=submission_test_case)
        await websocket_manager.send_message(submission.user_id, ws_message.model_dump())

    except SQLAlchemyError as e:
        session.rollback()
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise e

def save_total(submission_id: int, result: SubmissionResult, session: Session):
    try:
        # check if the submission exists
        submission: Submission = get_object_by_id(Submission, session, submission_id)
        if not submission:
            raise HTTPException(status_code=400, detail="Submission not found")
        
        submission_result: SubmissionResult = get_object_by_id(SubmissionResult, session, result.result_id)
        if not submission_result:
            raise HTTPException(status_code=400, detail="Result not found")
        
        test_submissions = submission.test_cases
        
        submission.result = submission_result

        session.commit()
        

    except SQLAlchemyError as e:
        session.rollback()
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise e
