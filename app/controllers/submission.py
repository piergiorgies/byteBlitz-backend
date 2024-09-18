from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.database import get_object_by_id
from app.models import SubmissionDTO, Submission, User, Problem, Language, Contest, ContestSubmission, SubmissionTestCase


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

        return True
    
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise e

