from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import List

from app.database import get_object_by_id, get_object_by_id_joined_with
from app.models.mapping import Submission, User, Problem, Language, Contest
from app.models.mapping import ContestSubmission, ContestProblem, SubmissionResult
from app.connections.rabbitmq import rabbitmq_connection
from app.schemas import SubmissionCreate, ProblemSubmissions, PaginationParams, SubmissionResponse

def create(submission_in: SubmissionCreate, session: Session, user: User):
    """
    Create a submission

    Args:
        submission (SubmissionCreate): The submission data
        session (Session): The database session
    
    Returns:
        created (bool): Whether the submission was created
    """
    
    try:        
        language: Language = session.query(Language).filter(Language.id == submission_in.language_id).first()
        _validate_submission(submission_in, session, user)

        # create the submission
        submission = Submission(
            submitted_code=submission_in.submitted_code,
            notes=submission_in.notes,
            problem_id=submission_in.problem_id,
            user_id=user.id,
            language_id=language.id,
            is_pretest_run=submission_in.is_pretest_run
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)

        # create the contest submission
        if submission_in.contest_id:
            contest_submission = ContestSubmission(
                contest_id=submission_in.contest_id,
                submission_id=submission.id
            )
            session.add(contest_submission)

        session.commit()

        body = {
            'code' : submission.submitted_code,
            'problem_id' : submission.problem_id,
            'language' : submission.language.name.strip(),
            'submission_id' : submission.id,
            'is_pretest_run' : submission.is_pretest_run,
        }
        # send the submission to the queue
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

def _validate_submission(submission_dto: SubmissionCreate, session: Session, user: User):
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
    
    # check if the problem is in a contest and if the contest is active
    contests = session.query(Contest).join(ContestProblem).filter(ContestProblem.problem_id == problem.id).all()
    
    # if at least one contest is active, the problem is in a contest
    there_are_active_contests = False
    if contests:
        for contest in contests:
            if contest.start_datetime < datetime.now() and contest.end_datetime > datetime.now():
                there_are_active_contests = True
                break

    if submission_dto.contest_id and there_are_active_contests:
        # check if the contest exists
        contest: Contest = get_object_by_id_joined_with(Contest, session, submission_dto.contest_id, [Contest.problems, Contest.users])
        if not contest:
            raise HTTPException(status_code=400, detail="Contest not found")
        
        # check if the problem is in the contest
        if contest.problems and problem not in contest.problems:
            raise HTTPException(status_code=400, detail="Problem not in contest")
        
        # check if problem has been published
        contest_problem : ContestProblem = session.query(ContestProblem).filter(ContestProblem.contest_id == contest.id,
                                                                                ContestProblem.problem_id == problem.id).first()
        if not contest_problem or contest_problem.publication_delay > (datetime.now() - contest_problem.contest.start_datetime).total_seconds() / 60:
            raise HTTPException(status_code=400, detail="Problem not published yet")
        
        # check if the user is in the contest
        if contest.users and user not in contest.users:
            raise HTTPException(status_code=400, detail="User not in contest")
        
        # check if the contest is active
        if contest.end_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Contest is over")
        
    # check if the user has submitted too many times in the last hour
    last_minute = datetime.now() - timedelta(minutes=1)

    try:
        submissions_count = session.query(Submission).filter(Submission.user_id == user.id,
                                                         Submission.created_at >= last_minute,
                                                         Submission.is_pretest_run == False).count()

        if submissions_count >= 5:
            raise HTTPException(status_code=400, detail="Too many submissions")
        
    except SQLAlchemyError as e:
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

def get_submission_results(session: Session):
    try:
        query = session.query(SubmissionResult)
        submission_results : List[SubmissionResult] = query.all()

        return submission_results

    except SQLAlchemyError as e:
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

def submission_by_problem(pagination: PaginationParams, problem_id: int, user: User, session: Session):
    try:
        query = session.query(Submission).filter(Submission.problem_id == problem_id,
                                                 Submission.user_id == user.id,
                                                 Submission.submission_result_id != None,
                                                 Submission.is_pretest_run == False)
        count = query.count()
        query = query.offset(pagination.offset).limit(pagination.limit).all()

        submissions = [SubmissionResponse.model_validate(obj=submission) for submission in query]

        result = ProblemSubmissions(count=count, submissions=submissions)
        return result

    except SQLAlchemyError as e:
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e