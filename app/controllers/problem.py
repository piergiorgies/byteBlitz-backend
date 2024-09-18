from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ListDTOBase, ListResponse, User, Problem
from app.models.problem import ProblemDTO

#region Problem

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
        is_user = user.user_type.code == "user"

        builder = QueryBuilder(Problem, session, body.limit, body.offset)
        if is_user:
            tmp_query = builder.getQuery().filter(Problem.is_public == True)
            problems: List[Problem] = tmp_query.all()
            count = tmp_query.count()
            #TODO: fix (user when body has limit)
        else:
            problems: List[Problem] = builder.getQuery().all()
            count = builder.getCount()

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

    try:
        problem: Problem = get_object_by_id(Problem, session, id)
        #TODO: visibility rules
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return ProblemDTO.model_validate(obj=problem)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create(problemDTO: ProblemDTO, user: User, session: Session) -> ProblemDTO:
    """
    Create a problem
    
    Args:
        problem: ProblemDTO
        session: Session
    
    Returns: 
        ProblemDTO: problem
    """

    try:
        problem = session.query(Problem).filter(Problem.title == problemDTO.title).first()
        if problem:
            raise HTTPException(status_code=409, detail="Problem title already exists")
        if problemDTO.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")

        problem = Problem(
            title=problemDTO.title,
            description=problemDTO.description,
            points=problemDTO.points,
            is_public=problemDTO.is_public,
            author_id=user.id
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
              
def delete(id: int, session: Session) -> bool:
    """
    Delete problem by id

    Args: 
        id: int
    
    Returns:
        deleted: bool
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
    
def update(id: int, problem_update: ProblemDTO, session: Session) -> ProblemDTO:
    """
    Update problem by id

    Args:
        id (int):
        contest (ProblemDTO):

    Returns:
        problem (ProblemDTO):
    """

    try:
        problem: Problem = get_object_by_id(Problem, session, id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        problem = session.query(Problem).filter(Problem.title == problem_update.title).first() #TODO: is a list
        if problem and problem.id != problem_update.id:
            raise HTTPException(status_code=409, detail="Problem title already exists")
        if problem_update.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")
        
        problem.name = problem_update.name
        contest.description = contest_update.description
        contest.start_datetime = contest_update.start_datetime
        contest.end_datetime = contest_update.end_datetime

        session.commit()
        return ProblemDTO.model_validate(obj=contest)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region ProblemTestCase
#TODO: everything

#list all for a specific problem
#read single for a specific problem
#create
#update
#delete

#endregion

#region ProblemConstraint
#TODO: everything

#list for a specific problem
#read for a specific problem and a specific language
#create
#update
#delete

#endregion