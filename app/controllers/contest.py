from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder
from app.models import ContestDTO, Contest, ListDTOBase, ListResponse
from app.models import User, ContestUserDTO
from app.models import Team, ContestTeamDTO

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
        contests: List[Contest] = builder.get()
        count = builder.count()
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
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
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
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
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
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
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
    
def add_user(id: int, user_id: int, session: Session) -> bool:
    """
    Add user to contest

    Args:
        id: int
        user_id: int

    Returns:
        bool: added
    """

    try:
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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
    
def remove_user(id: int, user_id: int, session: Session) -> bool:
    """
    Remove user from contest

    Args:
        id: int
        user_id: int
    
    Returns:
        bool: removed
    """

    try:
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        user = session.query(User).filter(User.id == user_id).first()
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
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        return {"data": [ContestUserDTO.model_validate(obj=user) for user in contest.users], "count": len(contest.users)}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def add_team(id: int, team_id: int, session: Session) -> bool:
    """
    Add team to contest

    Args:
        id: int
        team_id: int
    
    Returns:
        bool: added
    """

    try:
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        team = session.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

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
    
def remove_team(id: int, team_id: int, session: Session) -> bool:
    """
    Remove team from contest

    Args:
        id: int
        team_id: int

    Returns:
        bool: removed
    """

    try:
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        team = session.query(Team).filter(Team.id == team_id).first()
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
        contest: Contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        return {"data": [ContestTeamDTO.model_validate(obj=team) for team in contest.teams], "count": len(contest.teams)}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))