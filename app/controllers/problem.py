from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List
from datetime import datetime

from app.schemas import ProblemListResponse
from app.schemas import PaginationParams, get_pagination_params
from app.models.mapping import User, Problem, ProblemConstraint, Language, Contest

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