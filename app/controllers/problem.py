from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List
from datetime import datetime

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.database import get_object_by_id
from app.schemas import ProblemRead, ProblemConstraint
from app.models.mapping import User, Problem, ProblemConstraint, Language


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

        is_admin_maintainer = RoleChecker.hasRole(user, Role.PROBLEM_MAINTAINER)
        if not is_admin_maintainer and not problem.is_public:
            raise HTTPException(status_code=404, detail="Problem not found")

        query = session.query(ProblemConstraint).filter(ProblemConstraint.problem_id == problem.id)
        constraints : List[ProblemConstraint] = query.all()
        problem.constraints = constraints
        print(constraints)

        return ProblemRead.model_validate(obj=problem)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

