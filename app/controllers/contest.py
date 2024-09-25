from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ContestDTO, Contest, ListDTOBase, ListResponse
from app.models import User, ContestUserDTO
from app.models import Team, ContestTeamDTO
from app.models import Problem, ContestProblemDTO, ContestProblem

#region Contest
def create(contest: ContestDTO, session: Session) -> ContestDTO:
    """
    Create a contest
    
    Args:
        session: Session
        contest: ContestDTO
    
    Returns:
        ContestDTO: contest
    """
    try:
        if contest.start_datetime > contest.end_datetime:
            raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")
        
        contest = Contest(
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime
        )

        session.add(contest)
        session.commit()

        return contest
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def list(body: ListDTOBase, session: Session) -> ListResponse:
    """
    List contests
    
    Args:
        session: Session
    
    Returns:
        [ContestDTO]: contests
    """
    try:
        builder = QueryBuilder(Contest, session, body.limit, body.offset)
        contests: List[Contest] = builder.getQuery().all()
        count = builder.getCount()
        return {"data": [ContestDTO.model_validate(obj=obj) for obj in contests], "count": count}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read(id: int, session: Session) -> ContestDTO:
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
        
        return ContestDTO.model_validate(obj=contest)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
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
    
def update(id: int, contest_update: ContestDTO, session: Session) -> ContestDTO:
    """
    Update contest by id

    Args:
        id: int
        contest: ContestDTO

    Returns:
        ContestDTO: contest
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        if contest.start_datetime > contest.end_datetime:
            raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")
        
        contest.name = contest_update.name
        contest.description = contest_update.description
        contest.start_datetime = contest_update.start_datetime
        contest.end_datetime = contest_update.end_datetime

        session.commit()
        return ContestDTO.model_validate(obj=contest)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Contest User

def add_users(id: int, user_ids: List[int], session: Session) -> bool:
    """
    Add user to contest

    Args:
        id: int
        user_id: int

    Returns:
        bool: added
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        for user_id in user_ids:
            user: User = get_object_by_id(User, session, user_id)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user in contest.users:
                raise HTTPException(status_code=400, detail="User already in contest")

            contest.users.append(user)
        
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
    
def remove_users(id: int, user_ids: List[int], session: Session) -> bool:
    """
    Remove user from contest

    Args:
        id: int
        user_id: int
    
    Returns:
        bool: removed
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        for user_id in user_ids:
            user: User = get_object_by_id(User, session, user_id)

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user not in contest.users:
                raise HTTPException(status_code=404, detail="User not found in contest")

            contest.users.remove(user)
        
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
    
def list_users(id: int, session: Session) -> ListResponse:
    """
    List users in a contest

    Args:
        id: int
    
    Returns:
        ListResponse: users
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        return {"data": [ContestUserDTO.model_validate(obj=user) for user in contest.users], "count": len(contest.users)}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Contest Team

def add_teams(id: int, team_ids: List[int], session: Session) -> bool:
    """
    Add team to contest

    Args:
        id: int
        team_id: int
    
    Returns:
        bool: added
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        for team_id in team_ids:
            team: Team = get_object_by_id(Team, session, team_id)

            if not team:
                raise HTTPException(status_code=404, detail="Team not found")

            if team in contest.teams:
                raise HTTPException(status_code=400, detail="Team already in contest")

            contest.teams.append(team)
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
    
def remove_teams(id: int, team_ids: List[int], session: Session) -> bool:
    """
    Remove team from contest

    Args:
        id: int
        team_id: int

    Returns:
        bool: removed
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        for team_id in team_ids:
            team: Team = get_object_by_id(Team, session, team_id)

            if not team:
                raise HTTPException(status_code=404, detail="Team not found")

            if team not in contest.teams:
                raise HTTPException(status_code=404, detail="Team not found in contest")

            contest.teams.remove(team)
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
    
def list_teams(id: int, session: Session) -> ListResponse:
    """
    List teams in a contest

    Args:
        id: int

    Returns:
        ListResponse: teams
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        return {"data": [ContestTeamDTO.model_validate(obj=team) for team in contest.teams], "count": len(contest.teams)}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Contest Problem

def add_problems(id: int, body: List[ContestProblemDTO], session: Session) -> bool:
    """
    Add problem to contest

    Args:
        id: int
        problem_id: int

    Returns:
        bool: added
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        problem: Problem = get_object_by_id(Problem, session, body.id)

        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        duration = (contest.end_datetime - contest.start_datetime).total_seconds()

        if duration < (body.publication_delay * 60):
            raise HTTPException(status_code=400, detail="Problem publication delay is greater than contest duration")

        if problem in contest.problems:
            raise HTTPException(status_code=400, detail="Problem already in contest")
        
        contest_problem = ContestProblem(contest_id=id, problem_id=body.id, publication_delay=body.publication_delay)

        session.add(contest_problem)
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
    
def remove_problems(id: int, problem_ids: List[int], session: Session) -> bool:
    """
    Remove problem from contest

    Args:
        id: int
        problem_id: int

    Returns:
        bool: removed
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        for problem_id in problem_ids:
            problem: Problem = get_object_by_id(Problem, session, problem_id)

            if not problem:
                raise HTTPException(status_code=404, detail="Problem not found")

            if problem not in contest.problems:
                raise HTTPException(status_code=404, detail="Problem not found in contest")

            contest.problems.remove(problem)
        
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

def list_problems(id: int, session: Session) -> ListResponse:
    """
    List problems in a contest

    Args:
        id: int

    Returns:
        ListResponse: problems
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        return {"data": [ContestProblemDTO.model_validate(obj=problem) for problem in contest.problems], "count": len(contest.problems)}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def update_problem(id: int, body: ContestProblemDTO, session: Session) -> bool:
    """
    Update problems in a contest

    Args:
        id: int
        body: ContestProblemDTO

    Returns:
        bool: updated
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        problem: Problem = get_object_by_id(Problem, session, body.id)

        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        if problem not in contest.problems:
            raise HTTPException(status_code=404, detail="Problem not found in contest")

        duration = (contest.end_datetime - contest.start_datetime).total_seconds()

        if duration < (body.publication_delay * 60):
            raise HTTPException(status_code=400, detail="Problem publication delay is greater than contest duration")

        contest_problem = session.query(ContestProblem).filter(ContestProblem.contest_id == id, ContestProblem.problem_id == body.id).first()
        
        contest_problem.publication_delay = body.publication_delay

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
    
#endregion

