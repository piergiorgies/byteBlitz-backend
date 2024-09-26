from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import TeamDTO, Team, ListDTOBase, ListResponse
from app.models import User, TeamUserDTO


 #region Team
def create(team: TeamDTO, session: Session) -> TeamDTO:
    """
    Create a team
    
    Args:
        session: Session
        team: teamDTO
    
    Returns:
        TeamDTO: team
    """
    try:
        existing_team = session.query(Team).filter(Team.name == team.name).one_or_none()
        if existing_team:
            raise HTTPException(status_code=409, detail="Team already exists")
        
        new_team = Team(
            name=team.name,
            logo_path=team.logo_path if team.logo_path else "default/logo/path.png"  # Fornisci un valore predefinito se logo_path è None
        )

        session.add(new_team)
        session.commit()

        return new_team
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def read(team_id: int, session: Session) -> TeamDTO:
    """
    Get team by id
    
    Args:
        team_id: int
        session: Session

    Returns:
        TeamDTO: team
    """
    try:
        team: Team = get_object_by_id(Team, session, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return TeamDTO.model_validate(obj=team)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def list(body: ListDTOBase, session: Session) -> ListResponse:
    """
    List teams
    
    Args:
        session: Session
        body: ListDTOBase
    
    Returns:
        ListResponse: response
    """
    try:
        builder = QueryBuilder(Team, session, body.limit, body.offset)
        contests: List[Team] = builder.getQuery().all()
        count = builder.getCount()
        return {"data": [TeamDTO.model_validate(obj=obj) for obj in contests], "count": count}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def delete(team_id: int, session: Session) -> bool:
    """
    Delete a team
    
    Args:
        session: Session
        team_id: int
    
    Returns:
        bool: success
    """
    try:
        team: Team = get_object_by_id(Team, session, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        session.delete(team)
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

def add_users(team_id: int, user_ids: List[int], session: Session) -> bool:
    """
    Add user to team

    Args:
        team_id: int
        user_id: int

    Returns:
        bool: added
    """

    try:
        team: Team = get_object_by_id(Team, session, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        for user_id in user_ids:
            user: User = get_object_by_id(User, session, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user in team.users:
                raise HTTPException(status_code=400, detail="User already in team")

            team.users.append(user)

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
    
def remove_users(team_id: int, user_ids: List[int], session: Session) -> bool:
    """
    Remove users from team

    Args:
        team_id: int
        user_ids: List[int]
    
    Returns:
        bool: removed
    """

    try:
        team: Team = get_object_by_id(Team, session, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        for user_id in user_ids:
            user: User = get_object_by_id(User, session, user_id)
            if not user:
                raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

            if user not in team.users:
                raise HTTPException(status_code=400, detail=f"User with id {user_id} not in team")

            team.users.remove(user)
        
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
    
def list_users(team_id: int, session: Session) -> ListResponse:
    """
    List users in a team

    Args:
        team_id: int
    
    Returns:
        ListResponse: users
    """

    try:
        team: Team = get_object_by_id(Team, session, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return {"data": [TeamUserDTO.model_validate(obj=user) for user in team.users], "count": len(team.users)}

    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


def update(team_id: int, team_update: TeamDTO, session: Session) -> TeamDTO:
    """
    Update team by id

    Args:
        team_id: int
        team_update: TeamDTO

    Returns:
        TeamDTO: updated team
    """

    try:
        team: Team = get_object_by_id(Team, session, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Check if there is an existing team with the same name
        existing_team = session.query(Team).filter(Team.name == team_update.name, Team.id != team_id).one_or_none()
        if existing_team:
            raise HTTPException(status_code=409, detail="Team with this name already exists")
        
        team.name = team_update.name
        if team_update.logo_path is not None:
            team.logo_path = team_update.logo_path
        #team.logo_path = team_update.logo_path

        session.commit()
        return TeamDTO.model_validate(obj=team)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))