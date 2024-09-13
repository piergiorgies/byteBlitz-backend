from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ListDTOBase, ListResponse, User, Problem
from app.models.problem import ProblemDTO

def list(body: ListDTOBase, user: User, session: Session) -> ListResponse:
    """
    List problems according to visibility
    
    Args:
        body (ListDTOBase):
        user (User):
        session (Session):
    
    Returns:
        [ListResponse]: list of problems
    """

    try:
        builder = QueryBuilder(Problem, session, body.limit, body.offset)
        problems: List[Problem] = builder.getQuery().all()
        count = builder.getCount()
        #TODO: visibility (public or not)
        return {"data": [ProblemDTO.model_validate(obj=obj) for obj in problems], "count": count}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read(id: int, user: User, session: Session) -> ProblemDTO:
    """
    Get problem by id according to visibility

    Args:
        id (int):
        user (User):
        session (Session):

    Returns:
        ProblemDTO: problem
    """

    #TODO: everything
    # try:
    #     contest: Contest = session.query(Contest).filter(Contest.id == id).first()
    #     if not contest:
    #         raise HTTPException(status_code=404, detail="Contest not found")
        
    #     return ContestDTO.model_validate(obj=contest)
    
    # except SQLAlchemyError as e:
    #     raise HTTPException(status_code=500, detail="Database error: " + str(e))
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO: create to be tested.
def create(problemDTO: ProblemDTO, session: Session) -> ProblemDTO:
    """
    Create a problem
    
    Args:
        problem: ProblemDTO
        session: Session
    
    Returns: 
        ProblemDTO: problem
    """

    try:
        if problemDTO.points < 0: #TODO: define minimum/maximum points
            raise HTTPException(status_code=400, detail="Points cannot be negative.")

        problem = Problem(
            title=problemDTO.title,
            description=problemDTO.description,
            points=problemDTO.points,
            is_public=problemDTO.is_public
        )

        session.add(problem)
        session.commit()

        return problem
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
              
#TODO: def delete to be tested
def delete(id: int, session: Session) -> bool:
    """
    Delete problem by id

    Args: 
        id: int
    
    Returns:
        bool: deleted
    """

    try:
        problem: Problem = get_object_by_id(Problem, session, id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        session.delete(problem)
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