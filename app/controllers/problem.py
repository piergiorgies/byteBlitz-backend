from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import get_object_by_id
from app.schemas import ProblemListResponse
from app.schemas import PaginationParams
from app.models.mapping import User, Problem, ProblemConstraint, ProblemTestCase
from app.schemas.problem import ProblemRead

def list_visible_problems(pagination: PaginationParams, session: Session) -> ProblemListResponse:
    """
    List problems

    Returns:
        ProblemListResponse: problems
    """
    # get all public problems that are not in a contest that is not finished

    try:
        query = session.query(Problem).filter(Problem.is_public == True)
        # apply search filter
        if pagination.search_filter:
            query = query.filter(Problem.title.ilike(f"%{pagination.search_filter}%"))

        # get total count        
        count = query.count()
        # apply pagination
        query = query.join(Problem.constraints)
        query = query.join(ProblemConstraint.language)
        query = query.order_by(Problem.id).offset(pagination.offset).limit(pagination.limit)

        problems = query.all()

        problems_info = []
        for problem in problems:
            languages = [constraint.language.name for constraint in problem.constraints]
            problems_info.append({
                "id": problem.id,
                "title": problem.title,
                "points": problem.points,
                "languages": languages,
                "is_public": problem.is_public
            })

        return ProblemListResponse(problems=problems_info, count=count)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    

def read(id: int, user: User, session: Session) -> ProblemRead:
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
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        query = session.query(ProblemConstraint).filter(ProblemConstraint.problem_id == problem.id)
        constraints : List[ProblemConstraint] = query.all()
        problem.constraints = constraints

        visible_test_cases = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem.id, ProblemTestCase.is_pretest == True).all()
        problem.test_cases = visible_test_cases

        query = session.query(ProblemTestCase)

        return ProblemRead.model_validate(obj=problem)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
