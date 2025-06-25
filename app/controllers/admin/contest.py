from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from sqlalchemy import or_
from app.models.mapping import Contest, User, Problem, ContestProblem, ContestSubmission, Submission, SubmissionResult, SubmissionTestCase
from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.schemas import (ContestCreate, ContestRead, ContestUpdate, ContestListResponse,
    ContestBase, PaginationParams, ContestSubmissionRow, ContestSubmissions,
    SubmissionInfo, TestCaseResult)
from app.database import get_object_by_id

def read(id: int, session: Session) -> ContestRead:
    """
    Get contest by id
    
    Args:
        id: int

    Returns:
        ContestDTO: contest
    """

    try:
        query = session.query(Contest).filter(Contest.id == id)
        query.join(Contest.contest_problems)
        contest = query.first()

        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        users = [user.id for user in contest.users]
        problems = [
            {
                "problem_id": problem.problem_id,
                "publication_delay": problem.publication_delay
            }
            for problem in contest.contest_problems
        ]

        contest = ContestRead(
            id=contest.id,
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
            is_public=contest.is_public,
            is_registration_open=contest.is_registration_open,
            users=users,
            contest_problems=problems
        )

        return ContestRead.model_validate(obj=contest)  
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create(contest: ContestCreate, session: Session):
    """
    Create a contest
    
    Args:
        session: Session
        contest: ContestDTO
    
    Returns:
        ContestDTO: contest
    """
    try:
        if contest.start_datetime >= contest.end_datetime:
            raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")
        
        created_contest = Contest(
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
            is_public=contest.is_public,
            is_registration_open=contest.is_registration_open,
        )
        for i in range(len(contest.users)):
            user: User = get_object_by_id(User, session, contest.users[i])
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            created_contest.users.append(user)
        
        for i in range(len(contest.problems)):
            problem: Problem = get_object_by_id(Problem, session, contest.problems[i].problem_id)
            if not problem:
                raise HTTPException(status_code=404, detail="Problem not found")
            contest_problem = ContestProblem(
                contest_id=created_contest.id,
                problem_id=problem.id,
                publication_delay=contest.problems[i].publication_delay
            )
            created_contest.contest_problems.append(contest_problem)

        session.add(created_contest)
        session.commit()
        session.refresh(created_contest)

        return created_contest
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def delete(id: int, session: Session) -> bool:
    """
    Delete contest by id

    Args:
        id: int
    
    Returns:
        bool: deleted
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        session.delete(contest)
        session.commit()
        return True
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def update(id: int, contest_update: ContestUpdate, session: Session):
    """
    Update contest by id

    Args:
        id: int
        contest_update: ContestUpdate
        session: Session

    Returns:
        ContestRead: Updated contest
    """
    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")

        # Validate datetime
        if contest_update.start_datetime and contest_update.end_datetime:
            if contest_update.start_datetime > contest_update.end_datetime:
                raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")

        # Update fields
        for field in ["name", "description", "start_datetime", "end_datetime", "is_public", "is_registration_open"]:
            if hasattr(contest_update, field) and getattr(contest_update, field) is not None:
                setattr(contest, field, getattr(contest_update, field))

        # Update users
        if contest_update.users is not None:
            contest.users.clear()
            for user_id in contest_update.users:
                user = get_object_by_id(User, session, user_id)
                if not user:
                    raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
                contest.users.append(user)  # Append new users

        # Update problems
        if contest_update.problems is not None:
            session.query(ContestProblem).filter(ContestProblem.contest_id == contest.id).delete()

            problem_ids = [p.problem_id for p in contest_update.problems]
            problems = session.query(Problem).filter(Problem.id.in_(problem_ids)).all()

            if len(problems) != len(problem_ids):
                raise HTTPException(status_code=404, detail="One or more problems not found")

            contest_duration = (contest.end_datetime - contest.start_datetime).total_seconds()
            for item in contest_update.problems:
                if item.publication_delay > contest_duration / 60:
                    raise HTTPException(status_code=400, detail="Problem publication delay is greater than contest duration")

                contest.contest_problems.append(
                    ContestProblem(
                        contest_id=contest.id,
                        problem_id=item.problem_id,
                        publication_delay=item.publication_delay
                    )
                )

        session.commit()
        session.refresh(contest)
        # return the update status code
        return JSONResponse(status_code=200, content={"message": "Contest updated successfully"})

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def list(limit : int, offset : int, searchFilter: str, user : User, session : Session) -> ContestListResponse:
    """
    List contests
    
    Args:
        limit: limit in sql query
        offset: offset in sql query
        user: User
        session: Session
    
    Returns:
        [ContestDTO]: contests
    """
    try:

        query = session.query(Contest)

        if searchFilter:
            query = query.filter(Contest.name.ilike(f"%{searchFilter}%"))
        query.join(Contest.contest_problems)
        count = query.count()
        query = query.limit(limit).offset(offset)
        contests : List[Contest] = query.all()

        return ContestListResponse(
            contests=[ContestBase.model_validate(obj=contest) for contest in contests],
            count=count
        )
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def get_submissions(id: int, pagination: PaginationParams, session: Session) -> ContestSubmissions:
    """
    Get contest submissions by id

    Args:
        id: int
        session: Session

    Returns:
        List[ContestSubmissionRow]: List of contest submissions
    """
    try:
        contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        # join Submission, User, Contest
        query = session.query(ContestSubmission).filter(ContestSubmission.contest_id == id)
        query = query.join(Submission).join(Contest).join(User).join(SubmissionResult).order_by(Submission.created_at.desc())
        count = query.count()
        
        if pagination.search_filter:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{pagination.search_filter}%"),
                    Submission.code.ilike(f"%{pagination.search_filter}%")
                )
            )
        query = query.limit(pagination.limit).offset(pagination.offset)
        submissions: List[ContestSubmission] = query.all()
        if not submissions:
            return ContestSubmissions(submissions=[], count=0)
        contest_submissions = []
        for cs in submissions:
            contest_submissions.append(
                ContestSubmissionRow(
                    id=cs.submission.id,
                    user_id=cs.submission.user.id,
                    username=cs.submission.user.username,
                    problem_id=cs.submission.problem_id,
                    problem_title=cs.submission.problem.title,
                    status=cs.submission.result.code,
                    created_at=cs.submission.created_at,
                    score=cs.submission.score,
                )

            )
        return ContestSubmissions(submissions=contest_submissions, count=count)
        

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

def get_submission_info(id: int, session: Session) -> SubmissionInfo:
    """
    Get contest submission info by id

    Args:
        id: int
        session: Session

    Returns:
        SubmissionInfo: submission info
    """
    try:
        submission: Submission = get_object_by_id(Submission, session, id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        query = session.query(SubmissionTestCase).join(SubmissionResult).filter(SubmissionTestCase.submission_id == id)
        test_case_results = query.all()
        if not test_case_results:
            raise HTTPException(status_code=404, detail="Test case results not found for this submission")
        
        test_case_results_list = [
            TestCaseResult(
                result_code=test_case_result.result.code,
                number=test_case_result.number,
                notes=test_case_result.notes,
                memory=test_case_result.memory,
                time=test_case_result.time,
            ) for test_case_result in test_case_results
        ]

        submission = SubmissionInfo(
            id=submission.id,
            problem_id=submission.problem_id,
            code=submission.submitted_code,
            test_case_results=test_case_results_list,
        )
        
        return SubmissionInfo.model_validate(obj=submission)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
