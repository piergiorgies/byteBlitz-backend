from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from sqlalchemy import or_
from app.models.mapping import Contest, User, Problem, ContestProblem
from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.schemas import ContestCreate, ContestRead, ContestUpdate, ContestListResponse, ContestBase
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
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
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
        for i in range(len(contest.user_ids)):
            user: User = get_object_by_id(User, session, contest.user_ids[i])
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
        contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")

        if contest_update.start_datetime and contest_update.end_datetime:
            if contest_update.start_datetime > contest_update.end_datetime:
                raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")

        if contest_update.name:
            contest.name = contest_update.name

        if contest_update.description:
            contest.description = contest_update.description

        if contest_update.start_datetime:
            contest.start_datetime = contest_update.start_datetime

        if contest_update.end_datetime:
            contest.end_datetime = contest_update.end_datetime

        if contest_update.is_public is not None:
            contest.is_public = contest_update.is_public
        
        if contest_update.is_registration_open is not None:
            contest.is_registration_open = contest_update.is_registration_open

        if contest_update.user_ids is not None:
            users = session.query(User).filter(User.id.in_(contest_update.user_ids)).all()
            if len(users) != len(contest_update.user_ids):
                raise HTTPException(status_code=404, detail="One or more users not found")
            contest.users = users

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
                else:
                    contest.contest_problems.append(
                        ContestProblem(
                            contest_id=contest.id,
                            problem_id=item.problem_id,
                            publication_delay=item.publication_delay
                        )
                    )

        session.commit()
        session.refresh(contest)
        return ContestRead.model_validate(obj=contest)

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
        is_admin_maintainer = RoleChecker.hasRole(user, Role.CONTEST_MAINTAINER)
        query = session.query(Contest)
        if not is_admin_maintainer:
            is_user = RoleChecker.hasRole(user, Role.USER)
            if is_user:
                query = query.filter(
                    or_(
                        Contest.users.any(User.id == user.id),
                        Contest.end_datetime <= datetime.now()
                    )
                )
            else:
                query = query.filter(Contest.end_datetime <= datetime.now())

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