from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.database import QueryBuilder, get_object_by_id
from app.models import ListDTOBase, ListResponse, User, Problem, ProblemTestCase
from app.models.problem import ProblemDTO, ProblemTestCaseDTO, ProblemConstraintDTO

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
        problemDTO: ProblemDTO
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
        problem_update (ProblemDTO):

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
        
        #TODO: from here
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

#region Problem Test Cases
#TODO: sto scrivendo a macchinetta. verificare quali controlli sono necessari.
def list_test_cases(id: int, session: Session) -> ListResponse:
    """
   List all test cases for a specific problem
    
    Args:
        id (int): the id of the related problem
        session (Session):
    
    Returns:
        [ListResponse]: list of test cases
    """

    try:
        test_cases: List[ProblemTestCase] = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == id).all()
        return {"data" : [ProblemTestCaseDTO.model_validate(obj=obj) for obj in test_cases]}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read_test_case(id: int, session: Session) -> ProblemTestCaseDTO:
    """
    Get test case by id

    Args:
        id (int):
        session (Session):

    Returns:
        ProblemTestCaseDTO: test case
    """

    try:
        test_case = get_object_by_id(ProblemTestCase, session, id)
        if not test_case:
            raise HTTPException(status_code=404, detail= "Problem test case not found")
        return ProblemTestCaseDTO.model_validate(obj=test_case)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create_test_case(problemTestCaseDTO: ProblemTestCaseDTO, problem_id: int, session: Session) -> ProblemTestCaseDTO:
    """
    Create test case
    
    Args:
        problemTestCaseDTO (ProblemTestCaseDTO):
        problem_id (int):
        session (Session): 
    
    Returns: 
        ProblemTestCaseDTO: test case
    """
    
    try:
        last_test_case = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem_id).order_by(ProblemTestCase.number.desc()).first()
        test_case_number = last_test_case.number + 1 if last_test_case else 1        
        test_case_points = problemTestCaseDTO.points if not problemTestCaseDTO.is_pretest else 0

        problemTestCase = ProblemTestCase(
            number=test_case_number,
            notes=problemTestCaseDTO.notes,
            input_name=problemTestCaseDTO.input_name,
            output_name=problemTestCaseDTO.output_name,
            points=test_case_points,
            is_pretest=problemTestCaseDTO.is_pretest
        )
        
        problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        problem.increment_version_number()

        session.add(problemTestCase)
        session.commit()

        return problemTestCase

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def delete_test_case(id: int, session: Session) -> bool:
    """
    Delete test case by id

    Args:
        id (int):
        session (Session): 
    
    Returns:
        deleted: bool
    """
    pass
    
def update_test_case(id: int, test_case_update: ProblemTestCaseDTO, session: Session) -> ProblemTestCaseDTO:
    """
    Update test case by id

    Args:
        id (int):
        test_case_update (ProblemTestCaseDTO):
        session (Session): 

    Returns:
        ProblemTestCaseDTO: test case
    """
    pass

#endregion

#region Problem Constraints

def list_constraints(id: int, session: Session) -> ListResponse:
    """
   List all constraints for a specific problem
    
    Args:
        id (int): the id of the related problem
        session (Session):
    
    Returns:
        [ListResponse]: list of constraints
    """
    #TODO: everything
    pass
    # try:
    #     test_cases: List[ProblemTestCase] = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == id).all()
    #     return {"data" : [ProblemTestCaseDTO.model_validate(obj=obj) for obj in test_cases]}
    
    # except SQLAlchemyError as e:
    #     raise HTTPException(status_code=500, detail="Database error: " + str(e))
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read_constraint(id: int, session: Session) -> ProblemConstraintDTO:
    """
    Get constraint by id

    Args:
        id (int):
        session (Session):

    Returns:
        ProblemConstraintDTO: constraint
    """
    #TODO: everything
    pass
    # try:
    #     test_case = get_object_by_id(ProblemTestCase, session, id)
    #     if not test_case:
    #         raise HTTPException(status_code=404, detail= "Problem test case not found")
    #     return ProblemTestCaseDTO.model_validate(obj=test_case)
    
    # except SQLAlchemyError as e:
    #     raise HTTPException(status_code=500, detail="Database error: " + str(e))
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create_constraint(problemConstraintDTO: ProblemConstraintDTO, problem_id: int, session: Session) -> ProblemConstraintDTO:
    """
    Create constraint
    
    Args:
        problemConstraintDTO (ProblemConstraintDTO):
        problem_id (int):
        session (Session): 
    
    Returns: 
        ProblemConstraintDTO: constraint
    """
    #TODO: everything
    pass
    # try:
    #     last_test_case = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem_id).order_by(ProblemTestCase.number.desc()).first()
    #     test_case_number = last_test_case.number + 1 if last_test_case else 1        
    #     test_case_points = problemTestCaseDTO.points if not problemTestCaseDTO.is_pretest else 0

    #     problemTestCase = ProblemTestCase(
    #         number=test_case_number,
    #         notes=problemTestCaseDTO.notes,
    #         input_name=problemTestCaseDTO.input_name,
    #         output_name=problemTestCaseDTO.output_name,
    #         points=test_case_points,
    #         is_pretest=problemTestCaseDTO.is_pretest
    #     )
        
    #     problem = get_object_by_id(Problem, session, problem_id)
    #     if not problem:
    #         raise HTTPException(status_code=404, detail="Problem not found")
    #     problem.increment_version_number()

    #     session.add(problemTestCase)
    #     session.commit()

    #     return problemTestCase

    # except SQLAlchemyError as e:
    #     session.rollback()
    #     raise HTTPException(status_code=500, detail="Database error: " + str(e))
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     session.rollback()
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def delete_constraint(id: int, session: Session) -> bool:
    """
    Delete constraint by id

    Args:
        id (int):
        session (Session): 
    
    Returns:
        deleted: bool
    """
    pass
    
def update_constraint(id: int, constraint_update: ProblemConstraintDTO, session: Session) -> ProblemConstraintDTO:
    """
    Update constraint by id

    Args:
        id (int):
        constraint_update (ProblemConstraintDTO):
        session (Session): 

    Returns:
        ProblemConstraintDTO: constraint
    """
    pass

#endregion