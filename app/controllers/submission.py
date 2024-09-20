from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import pika

from app.database import get_object_by_id
from app.models import SubmissionDTO, Submission, User, Problem, Language, Contest, ContestSubmission, SubmissionTestCase
from app.models import ContestSubmission, SubmissionTestCase, SubmissionTestCaseDTO, SubmissionResult
from app.config import rabbitmq_connection

def create(submission_dto: SubmissionDTO, session: Session):
    """
    Create a submission

    Args:
        submission (SubmissionDTO): The submission data
        session (Session): The database session
    
    Returns:
        created (bool): Whether the submission was created
    """

    try:

        # check if the user exists
        user: User = get_object_by_id(User, session, submission_dto.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # check if the problem exists
        problem: Problem = get_object_by_id(Problem, session, submission_dto.problem_id)
        if not problem:
            raise HTTPException(status_code=400, detail="Problem not found")
        
        # check if the language exists
        language: Language = get_object_by_id(Language, session, submission_dto.language_id)
        if not language:
            raise HTTPException(status_code=400, detail="Language not found")
        
        if submission_dto.contest_id:
            # check if the contest exists
            contest: Contest = get_object_by_id(Contest, session, submission_dto.contest_id)
            if not contest:
                raise HTTPException(status_code=400, detail="Contest not found")
            
            # check if the problem is in the contest
            if contest.problems and problem not in contest.problems:
                raise HTTPException(status_code=400, detail="Problem not in contest")
            
        
        # TODO: Implement a sort of submission rate limiting
        
        # create the submission
        submission = Submission(
            submitted_code=submission_dto.submitted_code,
            notes=submission_dto.notes,
            problem_id=submission_dto.problem_id,
            user_id=submission_dto.user_id,
            language_id=submission_dto.language_id
        )
        
        session.add(submission)
        session.commit()
        session.refresh(submission)

        # create the contest submission
        if submission_dto.contest_id:
            contest_submission = ContestSubmission(
                contest_id=submission_dto.contest_id,
                submission_id=submission.id
            )
            session.add(contest_submission)

        session.commit()

        # send the submission to the queue
        rabbitmq_connection.try_send_to_queue('submissions', 'stocazzo')

        return True
    
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise e


def accept(submission_id: int, submission_test_case: SubmissionTestCaseDTO, session: Session):
    try:
        # check if the submission exists
        submission: Submission = get_object_by_id(Submission, session, submission_id)
        if not submission:
            raise HTTPException(status_code=400, detail="Submission not found")
        
        result: SubmissionResult = get_object_by_id(SubmissionResult, session, submission_test_case.result_id)

        submission_test_case = SubmissionTestCase(
            submission=submission,
            result=result,
            number=submission_test_case.number,
            notes=submission_test_case.notes,
            memory=submission_test_case.memory,
            time=submission_test_case.time
        )

        session.add(submission_test_case)
        session.commit()
        

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
