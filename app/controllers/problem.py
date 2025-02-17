from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List
from datetime import datetime

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.database import get_object_by_id
from app.schemas import ProblemListResponse, ProblemCreate, ProblemUpdate, ProblemInfo, ProblemRead, ProblemConstraint, ProblemTestCase
from app.models.mapping import User, Problem, ProblemTestCase, ProblemConstraint, Language, ContestProblem, Contest

def list(limit: int, offset: int, searchFilter: str, user: User, session: Session) -> ProblemListResponse:
    """
    List problems according to visibility with correct counting in SQLAlchemy.
    
    Args:
        limit (int): Number of problems per page.
        offset (int): Pagination offset.
        searchFilter (str): Search keyword.
        user (User): Logged-in user.
        session (Session): Database session.

    Returns:
        ListResponse: Contains problem list and total count.
    """

    try:
        is_admin_maintainer = RoleChecker.hasRole(user, Role.PROBLEM_MAINTAINER)

        # Base query for problem filtering
        query = session.query(Problem)

        # Apply visibility filters
        if not is_admin_maintainer:
            query = query.filter(Problem.is_public == True)

        # Apply search filter
        if searchFilter:
            query = query.filter(Problem.title.ilike(f"%{searchFilter}%"))

        # If user is NOT admin/maintainer, filter problems that are ONLY in ended contests
        if not is_admin_maintainer:
            query = query.join(ContestProblem).join(Contest).filter(Contest.end_datetime < datetime.now())

        # Get total count BEFORE applying limit & offset
        total_count = session.query(func.count()).select_from(query.subquery()).scalar()

        # Apply pagination
        problems = query.distinct().limit(limit).offset(offset).all()

        return {
            "data": [ProblemInfo.model_validate(obj=problem) for problem in problems],
            "count": total_count
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
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

def create(problemDTO: ProblemCreate, user: User, session: Session):
    """
    Create a problem along with its test cases
    
    Args:
        problemDTO (ProblemCreate): the problem data including test cases and constraints
        user (User): the user creating the problem
        session (Session): SQLAlchemy session
    
    Returns: 
        Problem: the created problem
    """
    try:
        # Check if a problem with the same title already exists
        existing_problem = session.query(Problem).filter(Problem.title == problemDTO.title).first()
        if existing_problem:
            raise HTTPException(status_code=409, detail="Problem title already exists")
        
        if problemDTO.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")
        
        # Build constraints from the provided DTO
        constraints = []
        for constraint in problemDTO.constraints:
            constraints.append(
                ProblemConstraint(
                    language_id=constraint.language_id,
                    memory_limit=constraint.memory_limit,
                    time_limit=constraint.time_limit
                )
            )
        
        # Create the problem instance
        problem = Problem(
            title=problemDTO.title,
            description=problemDTO.description,
            points=problemDTO.points,
            is_public=problemDTO.is_public,
            author_id=user.id,
            constraints=constraints
        )
        
        session.add(problem)
        # Flush to get the problem.id assigned without committing yet
        session.flush()
        
        # Create test cases if provided
        for test_case_dto in problemDTO.test_cases:
            if test_case_dto.points < 0:
                raise HTTPException(status_code=400, detail="Points cannot be negative")
            
            # Retrieve the last test case number for the problem
            last_test_case = (
                session.query(ProblemTestCase)
                .filter(ProblemTestCase.problem_id == problem.id)
                .order_by(ProblemTestCase.number.desc())
                .first()
            )
            test_case_number = last_test_case.number + 1 if last_test_case else 1
            
            # For pretests, override points to 0
            test_case_points = test_case_dto.points if not test_case_dto.is_pretest else 0
            
            # Increment the problem's version number (if the method exists)
            problem.increment_version_number()
            
            # Create the test case instance.
            # Assuming `notes` is an attribute; if not, remove it.
            test_case = ProblemTestCase(
                number=test_case_number,
                notes=getattr(test_case_dto, "notes", None),  # Use None if 'notes' is not provided
                input=test_case_dto.input,
                output=test_case_dto.output,
                points=test_case_points,
                is_pretest=test_case_dto.is_pretest,
                problem_id=problem.id
            )
            session.add(test_case)
        
        session.commit()
        return problem
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
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
    
def update(id: int, problem_update: ProblemUpdate, session: Session) -> ProblemUpdate:
    """
    Update problem by id along with its constraints and test cases

    Args:
        id (int): the problem id
        problem_update (ProblemUpdate): the updated problem data including constraints and test cases
        session (Session): SQLAlchemy session

    Returns:
        ProblemUpdate: the updated problem data
    """
    try:
        # Retrieve the problem by id
        problem: Problem = get_object_by_id(Problem, session, id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Check for duplicate title
        problem_title_check: Problem = (
            session.query(Problem)
            .filter(Problem.title == problem_update.title)
            .first()
        )
        if problem_title_check and problem_title_check.id != id:
            raise HTTPException(status_code=409, detail="Problem title already exists")
        
        # Validate problem points
        if problem_update.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")
        
        # Update basic problem fields
        problem.title = problem_update.title
        problem.description = problem_update.description
        problem.points = problem_update.points
        problem.is_public = problem_update.is_public

        # Increment version for any change
        problem.increment_version_number()

        # --- Update Constraints ---
        found = set()
        for constraint in problem.constraints:
            new_constraint = next(
                (x for x in problem_update.constraints if x.language_id == constraint.language_id),
                None
            )
            if new_constraint is None:
                continue

            found.add(new_constraint.language_id)
            constraint.time_limit = new_constraint.time_limit
            constraint.memory_limit = new_constraint.memory_limit

        constraints_to_add = [x for x in problem_update.constraints if x.language_id not in found]
        if constraints_to_add:
            problem.constraints.extend([
                ProblemConstraint(
                    language_id=constraint.language_id,
                    memory_limit=constraint.memory_limit,
                    time_limit=constraint.time_limit
                ) for constraint in constraints_to_add
            ])

        last_test_case = (
            session.query(ProblemTestCase)
            .filter(ProblemTestCase.problem_id == problem.id)
            .order_by(ProblemTestCase.number.desc())
            .first()
        )
        next_test_case_number = last_test_case.number + 1 if last_test_case else 1

        for test_case_dto in problem_update.test_cases:
            # Validate test case points
            if test_case_dto.points < 0:
                raise HTTPException(status_code=400, detail="Points cannot be negative")
            
            # If an ID is provided, update the existing test case.
            if getattr(test_case_dto, "id", None):
                test_case: ProblemTestCase = get_object_by_id(ProblemTestCase, session, test_case_dto.id)
                if not test_case:
                    raise HTTPException(status_code=404, detail=f"Test case with id {test_case_dto.id} not found")
                if test_case.problem_id != problem.id:
                    raise HTTPException(status_code=404, detail="Problem and test case do not match")
                
                # For pretests, force points to 0.
                test_case_points = test_case_dto.points if not test_case_dto.is_pretest else 0

                test_case.notes = test_case_dto.notes
                test_case.input = test_case_dto.input
                test_case.output = test_case_dto.output
                test_case.points = test_case_points
                test_case.is_pretest = test_case_dto.is_pretest

            # Otherwise, create a new test case.
            else:
                # Assign a number and then increment for the next new test case.
                test_case_number = next_test_case_number
                next_test_case_number += 1

                test_case_points = test_case_dto.points if not test_case_dto.is_pretest else 0

                new_test_case = ProblemTestCase(
                    number=test_case_number,
                    notes=getattr(test_case_dto, "notes", None),
                    input=test_case_dto.input,
                    output=test_case_dto.output,
                    points=test_case_points,
                    is_pretest=test_case_dto.is_pretest,
                    problem_id=problem.id
                )
                session.add(new_test_case)

        session.commit()
        # Validate and return the updated problem using your DTO validation method.
        return ProblemUpdate.model_validate(obj=problem)

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def list_available_languages(session: Session):
    """
    List problems according to visibility
    
    Args:
        limit (int):
        offset (int):
        user (User):
        session (Session):
    
    Returns:
        [ListResponse]: list of problems
    """

    try:
        query = session.query(Language)
        languages : List[Language] = query.all()

        return languages
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
