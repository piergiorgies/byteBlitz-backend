from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime, timedelta
import json

from app.database import get_object_by_id, get_object_by_id_joined_with
from app.models import SubmissionDTO
from app.models.mapping import Submission, User, Problem, Language, Contest
from app.models.mapping import ContestSubmission, SubmissionTestCase, ContestProblem, SubmissionResult, SubmissionTestCase
from app.models import SubmissionTestCaseDTO
from app.connections.rabbitmq import rabbitmq_connection

def create(submission_dto: SubmissionDTO, session: Session, user: User):
    """
    Create a submission

    Args:
        submission (SubmissionDTO): The submission data
        session (Session): The database session
    
    Returns:
        created (bool): Whether the submission was created
    """
    
    try:        
        language: Language = session.query(Language).filter(Language.id == submission_dto.language_id).first()
        _validate_submission(submission_dto, session, user)
        
        # create the submission
        submission = Submission(
            submitted_code=submission_dto.submitted_code,
            notes=submission_dto.notes,
            problem_id=submission_dto.problem_id,
            user_id=user.id,
            language_id=language.id
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

        body = {
            'code' : submission.submitted_code,
            'problem_id' : submission.problem_id,
            'language' : submission.language.name.strip(),
            'submission_id' : submission.id
        }
        # send the submission to the queue
        submission_dto.id = submission.id
        rabbitmq_connection.try_send_to_queue('submissions', body)

        return True
    
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise e

def _validate_submission(submission_dto: SubmissionDTO, session: Session, user: User):
    # check if the problem exists
    problem: Problem = get_object_by_id(Problem, session, submission_dto.problem_id)
    if not problem:
        raise HTTPException(status_code=400, detail="Problem not found")
    
    # check if the language exists
    language: Language = session.query(Language).filter(Language.id == submission_dto.language_id).first()
    if not language:
        raise HTTPException(status_code=400, detail="Language not found")
    
    # check if the problem has constraints for this language
    if language.id not in [x.language_id for x in problem.constraints]:
        raise HTTPException(status_code=400, detail="Language not supported by problem")
    
    if submission_dto.contest_id:
        # check if the contest exists
        contest: Contest = get_object_by_id_joined_with(Contest, session, submission_dto.contest_id, [Contest.problems, Contest.users])
        if not contest:
            raise HTTPException(status_code=400, detail="Contest not found")
        
        # check if the problem is in the contest
        if contest.problems and problem not in contest.problems:
            raise HTTPException(status_code=400, detail="Problem not in contest")
        
        # check if problem has been published
        contest_problem : ContestProblem = session.query(ContestProblem).filter(ContestProblem.contest_id == contest.id, ContestProblem.problem_id == problem.id).first()
        if not contest_problem or contest_problem.publication_delay > (datetime.now() - Contest.start_datetime).total_seconds() / 60:
            raise HTTPException(status_code=400, detail="Problem not published yet")
        
        # check if the user is in the contest
        if contest.users and user not in contest.users:
            raise HTTPException(status_code=400, detail="User not in contest")
        
        # check if the contest is active
        if contest.end_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Contest is over")
        
        
    # check if the user has submitted too many times in the last hour
    last_hour = datetime.now() - timedelta(hours=1)
    submissions_count = session.query(Submission).filter(Submission.user_id == user.id, Submission.created_at >= last_hour).count()

    if submissions_count >= 15:
        raise HTTPException(status_code=400, detail="Too many submissions")

def accept(submission_id: int, submission_test_case: SubmissionTestCaseDTO, session: Session):
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
