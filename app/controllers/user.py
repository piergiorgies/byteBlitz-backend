from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, select, case
from fastapi import HTTPException

from app.database import get_object_by_id
from app.schemas import UserResponse, ProfileResponse, PaginationParams, SubmissionHistory, SubmissionRecord
from app.models.mapping import User, Submission, SubmissionResult, Problem, Language, SubmissionTestCase


def read_me(current_user: User, session: Session) -> UserResponse:
    """
    Read the information of the logged user
    
    Args: 
        session (Session):
    
    Returns:
        UserDTO: user
    """
    
    try:
        user: User = get_object_by_id(User, session, current_user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(obj=user)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def get_profile_info(current_user: User, session: Session) -> ProfileResponse:
    """
    Get the profile information of the logged user
    
    Args: 
        session (Session):
    
    Returns:
        UserDTO: user
    """
    
    try:
        start_of_year = datetime(datetime.now().year, 1, 1)
        stmt = (
            select(
                func.date(Submission.created_at).label("submission_date"),
                func.count(Submission.id).label("submission_count")
            )
            .where(
                Submission.created_at >= start_of_year,
                Submission.user_id == current_user.id
            )
            .group_by(func.date(Submission.created_at))
            .order_by(func.date(Submission.created_at))
        )

        results = session.execute(stmt).all()

        submission_count_by_date = {result.submission_date: result.submission_count for result in results}
        total_year_sub = sum(submission_count_by_date.values())

        # get the acceptance rate (submission.result.code == 'AC' / all submissions)
        stmt = (
            select(
                func.count(Submission.id).label("total_submissions"),
                func.sum(
                    case(
                        (Submission.result.has(SubmissionResult.code == 'AC'), 1),
                        else_=0
                    )
                ).label("accepted_submissions")
            )
            .where(Submission.user_id == current_user.id)
        )

        result = session.execute(stmt).one()
        total = result.total_submissions or 0
        accepted = result.accepted_submissions or 0

        # Avoid division by zero
        acceptance_rate = (accepted / total) if total else 0.0

        return ProfileResponse(
            total_year_sub = total_year_sub,
            submission_map=submission_count_by_date,
            acceptance=acceptance_rate,
            email=current_user.email,
            username=current_user.username,
            registered_at=current_user.registered_at,
            has_password=current_user.password_hash != ''
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def get_submission_history(pagination: PaginationParams, current_user: User, session: Session) -> SubmissionHistory:
    """
    Get the submission history of the logged user
    
    Args: 
        session (Session):
    
    Returns:
        UserDTO: user
    """
    
    try:
        stmt = (
            select(
                Submission.created_at,
                Submission.problem_id,
                Problem.title.label("problem_title"),
                SubmissionResult.code.label("result_code"),
                func.max(SubmissionTestCase.time).label("execution_time"),
                func.max(SubmissionTestCase.memory).label("memory"),
                Language.name.label("language_name")
            )
            .join(Problem, Submission.problem)
            .join(SubmissionResult, Submission.result)
            .join(Language, Submission.language)
            .join(SubmissionTestCase, SubmissionTestCase.submission_id == Submission.id)
            .where(Submission.user_id == current_user.id, Submission.is_pretest_run == False)
            .group_by(
                Submission.id,
                Submission.created_at,
                Submission.problem_id,
                Problem.title,
                SubmissionResult.code,
                Language.name
            )
            .order_by(Submission.created_at.desc())
        )
        count_stmt = (
            select(func.count(func.distinct(Submission.id)))
            .join(SubmissionTestCase, SubmissionTestCase.submission_id == Submission.id)
            .where(Submission.user_id == current_user.id, Submission.is_pretest_run == False)
        )
        total_count = session.execute(count_stmt).scalar_one()

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        results = session.execute(stmt).all()

        return SubmissionHistory(
            count=total_count,
            submissions=[SubmissionRecord.model_validate(obj=result) for result in results]
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
