from datetime import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.mapping import User, Problem, ProblemConstraint, ProblemTestCase, Language
from app.schemas import ProblemListResponse, ProblemInfo, ProblemCreate, ProblemUpdate, ProblemRead
from app.database import get_object_by_id



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
        query = session.query(Problem)

        if searchFilter:
            query = query.filter(Problem.title.ilike(f"%{searchFilter}%"))

        count = query.count()

        problems = query.distinct().limit(limit).offset(offset).all()
        
        problem_infos: List[ProblemInfo] = []

        for problem in problems:
            languages = [constraint.language.name for constraint in problem.constraints]
            problem_infos.append(ProblemInfo(
                id=problem.id,
                title=problem.title,
                points=problem.points,
                languages=languages,
                is_public=problem.is_public,
                difficulty=problem.difficulty
            ))

        return ProblemListResponse(
            count=count,
            problems=problem_infos
        )

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
        
        # Build constraints from the provided DTO using the SQLAlchemy model
        constraints = [
            ProblemConstraint(
                language_id=constraint.language_id,
                memory_limit=constraint.memory_limit,
                time_limit=constraint.time_limit
            )
            for constraint in problemDTO.constraints
        ]
        
        # Create the problem instance and assign the constraints
        problem = Problem(
            title=problemDTO.title,
            description=problemDTO.description,
            points=problemDTO.points,
            is_public=problemDTO.is_public,
            author_id=user.id,
            difficulty=problemDTO.difficulty,
            constraints=constraints,  # This assumes a relationship is defined on Problem
        )
        
        session.add(problem)
        session.flush()  # Flush to get problem.id assigned before creating test cases

        # Create test cases if provided, using a local counter for numbering
        test_case_number = 1
        for test_case_dto in problemDTO.test_cases:
            if test_case_dto.points < 0:
                raise HTTPException(status_code=400, detail="Points cannot be negative")
            
            # For pretests, override points to 0
            test_case_points = 0 if test_case_dto.is_pretest else test_case_dto.points
            
            # Increment problem version (if this is intended to happen per test case)
            problem.increment_version_number()
            
            # Create the test case instance. Use getattr to retrieve notes if available.
            test_case = ProblemTestCase(
                number=test_case_number,
                notes=getattr(test_case_dto, "notes", None),
                input=test_case_dto.input,
                output=test_case_dto.output,
                points=test_case_points,
                is_pretest=test_case_dto.is_pretest,
                problem_id=problem.id
            )
            session.add(test_case)
            test_case_number += 1

        session.commit()
        return problem

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
 
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

def update(id: int, problem_update: ProblemUpdate, session: Session):
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
        
        # Check for duplicate title if a new title is provided
        if problem_update.title is not None:
            duplicate_problem = (
                session.query(Problem)
                .filter(Problem.title == problem_update.title)
                .first()
            )
            if duplicate_problem and duplicate_problem.id != id:
                raise HTTPException(status_code=409, detail="Problem title already exists")
            problem.title = problem_update.title
        
        # Update other basic fields if provided
        if problem_update.description is not None:
            problem.description = problem_update.description
        if problem_update.points is not None:
            if problem_update.points < 0:
                raise HTTPException(status_code=400, detail="Points cannot be negative")
            problem.points = problem_update.points
        if problem_update.is_public is not None:
            problem.is_public = problem_update.is_public

        if problem_update.difficulty is not None:
            problem.difficulty = problem_update.difficulty

        # Increment version for any change
        problem.increment_version_number()

        # --- Update Constraints ---
        if problem_update.constraints is not None:
            # Keep track of which language_ids were updated
            updated_lang_ids = set()
            # Update existing constraints if a matching language_id is found.
            for constraint in problem.constraints:
                new_constraint = next(
                    (c for c in problem_update.constraints if c.language_id == constraint.language_id),
                    None
                )
                if new_constraint:
                    updated_lang_ids.add(new_constraint.language_id)
                    constraint.time_limit = new_constraint.time_limit
                    constraint.memory_limit = new_constraint.memory_limit

            # Add new constraints that are not already present.
            constraints_to_add = [
                c for c in problem_update.constraints if c.language_id not in updated_lang_ids
            ]
            if constraints_to_add:
                problem.constraints.extend([
                    ProblemConstraint(
                        language_id=c.language_id,
                        memory_limit=c.memory_limit,
                        time_limit=c.time_limit
                    )
                    for c in constraints_to_add
                ])

        # Delete the saved test cases
        session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem.id).delete()

        # --- Update Test Cases ---
        if problem_update.test_cases is not None:
            # Determine the next test case number from existing test cases.
            last_test_case = (
                session.query(ProblemTestCase)
                .filter(ProblemTestCase.problem_id == problem.id)
                .order_by(ProblemTestCase.number.desc())
                .first()
            )
            next_test_case_number = last_test_case.number + 1 if last_test_case else 1

            for test_case_dto in problem_update.test_cases:
                if test_case_dto.points < 0:
                    raise HTTPException(status_code=400, detail="Points cannot be negative")
                
                # If an id is provided, update the existing test case.
                if getattr(test_case_dto, "id", None):
                    test_case: ProblemTestCase = get_object_by_id(ProblemTestCase, session, test_case_dto.id)
                    if not test_case:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Test case with id {test_case_dto.id} not found"
                        )
                    if test_case.problem_id != problem.id:
                        raise HTTPException(
                            status_code=404,
                            detail="Problem and test case do not match"
                        )
                    
                    # For pretests, force points to 0.
                    test_case_points = 0 if test_case_dto.is_pretest else test_case_dto.points
                    test_case.notes = getattr(test_case_dto, "notes", None)
                    test_case.input = test_case_dto.input
                    test_case.output = test_case_dto.output
                    test_case.points = test_case_points
                    test_case.is_pretest = test_case_dto.is_pretest

                # Otherwise, create a new test case.
                else:
                    test_case_points = 0 if test_case_dto.is_pretest else test_case_dto.points
                    new_test_case = ProblemTestCase(
                        number=next_test_case_number,
                        notes=getattr(test_case_dto, "notes", None),
                        input=test_case_dto.input,
                        output=test_case_dto.output,
                        points=test_case_points,
                        is_pretest=test_case_dto.is_pretest,
                        problem_id=problem.id
                    )
                    session.add(new_test_case)
                    next_test_case_number += 1

        
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
        print(constraints)

        return ProblemRead.model_validate(obj=problem)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
