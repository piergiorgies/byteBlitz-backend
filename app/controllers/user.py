from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ListDTOBase, ListResponse, User, UserDTO

def list(body: ListDTOBase, user: User, session: Session) -> ListResponse:
    """
    List all users
    
    Args:
        body (ListDTOBase):
        user (User):
        session (Session):
    
    Returns:
        [ListResponse]: list of users
    """
    #TODO: show password hash or not ?? join user_type_id with code ??
    try:
        builder = QueryBuilder(User, session, body.limit, body.offset)
        users: List[User] = builder.getQuery().all()
        count = builder.getCount()
        return {"data": [UserDTO.model_validate(obj=obj) for obj in users], "count": count}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
#TODO: from here
# def read(id: int, user: User, session: Session) -> ProblemDTO:
#     """
#     Get problem by id according to visibility

#     Args:
#         id (int):
#         user (User):
#         session (Session):

#     Returns:
#         ProblemDTO: problem
#     """

#     try:
#         problem: Problem = get_object_by_id(Problem, session, id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")
        
#         is_user = user.user_type.code == "user"
#         if is_user and not problem.is_public:
#             raise HTTPException(status_code=404, detail="Problem not found")

#         return ProblemDTO.model_validate(obj=problem)
    
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
              
# def delete(id: int, session: Session) -> bool:
#     """
#     Delete problem by id

#     Args: 
#         id: int
    
#     Returns:
#         deleted: bool
#     """

#     try:
#         problem: Problem = get_object_by_id(Problem, session, id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")
        
#         session.delete(problem)
#         session.commit()
#         return True
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
# def update(id: int, problem_update: ProblemDTO, session: Session) -> ProblemDTO:
#     """
#     Update problem by id

#     Args:
#         id (int):
#         problem_update (ProblemDTO):

#     Returns:
#         problem (ProblemDTO):
#     """

#     try:
#         problem : Problem = get_object_by_id(Problem, session, id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")
#         problem_title_check : Problem = session.query(Problem).filter(Problem.title == problem_update.title).first()
#         if problem_title_check and problem_title_check.id != id:
#             raise HTTPException(status_code=409, detail="Problem title already exists")
#         if problem_update.points < 0:
#             raise HTTPException(status_code=400, detail="Points cannot be negative")
        
#         problem.title=problem_update.title
#         problem.description=problem_update.description
#         problem.points=problem_update.points
#         problem.is_public=problem_update.is_public

#         problem.increment_version_number()

#         session.commit()
#         return ProblemDTO.model_validate(obj=problem)
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO:
#  [GET] list all users
#  [GET] read single user
#  [DELETE] delete a single user
#  [PUT] update a single user