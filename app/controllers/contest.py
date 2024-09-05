from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder
from app.models import ContestDTO, Contest, ListDTOBase, ListResponse

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
        if contest.start_time > contest.end_time:
            raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")
        

        contest = Contest(
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_time,
            end_datetime=contest.end_time
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