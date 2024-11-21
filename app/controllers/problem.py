from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.auth_util.role import Role
from app.auth_util.role_checker import RoleChecker
from app.database import get_object_by_id, get_object_by_id_joined_with
from app.models import ListResponse, User, Problem, ProblemTestCase, ProblemConstraint, Language, JudgeDTO
from app.models.problem import ProblemDTO, ProblemTestCaseDTO, ProblemConstraintDTO, TestCaseDTO, ConstraintDTO, ProblemJudgeDTO

#region Problem

def list(limit : int, offset : int, user: User, session: Session) -> ListResponse:
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
        is_admin_maintainer = RoleChecker.hasRole(user, Role.PROBLEM_MAINTAINER)
        query = session.query(Problem)
        if not is_admin_maintainer: 
            query = query.filter(Problem.is_public == True)

        count = query.count()
        query = query.limit(limit).offset(offset)

        problems : List[Problem] = query.all()

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
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        is_admin_maintainer = RoleChecker.hasRole(user, Role.PROBLEM_MAINTAINER)
        if not is_admin_maintainer and not problem.is_public:
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
        problem : Problem = get_object_by_id(Problem, session, id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        problem_title_check : Problem = session.query(Problem).filter(Problem.title == problem_update.title).first()
        if problem_title_check and problem_title_check.id != id:
            raise HTTPException(status_code=409, detail="Problem title already exists")
        if problem_update.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")
        
        problem.title=problem_update.title
        problem.description=problem_update.description
        problem.points=problem_update.points
        problem.is_public=problem_update.is_public

        problem.increment_version_number()

        session.commit()
        return ProblemDTO.model_validate(obj=problem)
    
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

def list_test_cases(problem_id: int, session: Session) -> ListResponse:
    """
   List all test cases for a specific problem
    
    Args:
        problem_id (int): the id of the related problem
        session (Session):
    
    Returns:
        [ListResponse]: list of test cases
    """

    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        query = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem_id)
        test_cases: List[ProblemTestCase] = query.all()
        count : int = query.count()
        return {"data" : [ProblemTestCaseDTO.model_validate(obj=obj) for obj in test_cases], "count" : count}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read_test_case(problem_id: int, test_case_id : int, session: Session) -> ProblemTestCaseDTO:
    """
    Get test case by id

    Args:
        problem_id (int):  the id of the related problem
        test_case_id ():  the id of the test case
        session (Session):

    Returns:
        ProblemTestCaseDTO: test case
    """

    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        test_case = get_object_by_id(ProblemTestCase, session, test_case_id)
        if not test_case:
            raise HTTPException(status_code=404, detail= "Test case not found")
        if test_case.problem_id != problem.id:
            raise HTTPException(status_code=404, detail= "Problem or Test case not found")
        return ProblemTestCaseDTO.model_validate(obj=test_case)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create_test_case(problem_id: int, problemTestCaseDTO: ProblemTestCaseDTO, session: Session) -> ProblemTestCaseDTO:
    """
    Create test case
    
    Args:
        problem_id (int): the id of the related problem
        problemTestCaseDTO (ProblemTestCaseDTO): the test case to create
        session (Session): 
    
    Returns: 
        ProblemTestCaseDTO: test case
    """
    
    try:
        problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        if problemTestCaseDTO.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")
        
        problem.increment_version_number()

        last_test_case = session.query(ProblemTestCase).filter(ProblemTestCase.problem_id == problem_id).order_by(ProblemTestCase.number.desc()).first()
        test_case_number = last_test_case.number + 1 if last_test_case else 1        
        test_case_points = problemTestCaseDTO.points if not problemTestCaseDTO.is_pretest else 0

        problemTestCase = ProblemTestCase(
            number=test_case_number,
            notes=problemTestCaseDTO.notes,
            input_name=problemTestCaseDTO.input_name,
            output_name=problemTestCaseDTO.output_name,
            input=problemTestCaseDTO.input,
            output=problemTestCaseDTO.output,
            points=test_case_points,
            is_pretest=problemTestCaseDTO.is_pretest,
            problem_id=problem_id
        )
        
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

def delete_test_cases(problem_id: int, test_case_ids: List[int], session: Session) -> bool:
    """
    Delete test case by id

    Args:
        problem_id (int): the id of the related problem
        test_case_ids (int): the ids of the test cases
        session (Session): 
    
    Returns:
        deleted: bool
    """

    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        for test_case_id in test_case_ids:
            test_case : ProblemTestCase = get_object_by_id(ProblemTestCase, session, test_case_id)
            if not test_case:
                raise HTTPException(status_code=404, detail="Test case not found")
            if test_case.problem_id != problem.id:
                raise HTTPException(status_code=404, detail= "Problem or Test case not found")
            problem.increment_version_number()
            session.delete(test_case)
        
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
    
def update_test_case(problem_id: int, test_case_update: ProblemTestCaseDTO, session: Session) -> ProblemTestCaseDTO:
    """
    Update test case by id

    Args:
        problem_id (int): the id of the related problem
        test_case_update (ProblemTestCaseDTO): the updated test case
        session (Session): 

    Returns:
        ProblemTestCaseDTO: test case
    """

    try: 
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        test_case: ProblemTestCase = get_object_by_id(ProblemTestCase, session, test_case_update.id)
        if not test_case:
            raise HTTPException(status_code=404, detail="Test case not found")
        if test_case.problem_id != problem.id:
            raise HTTPException(status_code=404, detail= "Problem or Test case not found")
        if test_case_update.points < 0:
            raise HTTPException(status_code=400, detail="Points cannot be negative")
        
        problem.increment_version_number()

        test_case_points = test_case_update.points if not test_case_update.is_pretest else 0

        test_case.notes = test_case_update.notes
        test_case.input_name = test_case_update.input_name
        test_case.output_name = test_case_update.output_name
        test_case.points = test_case_points
        test_case.is_pretest = test_case_update.is_pretest

        session.commit()
        return ProblemTestCaseDTO.model_validate(obj=test_case)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Problem Constraints

def list_constraints(problem_id: int, user: User, session: Session) -> ListResponse:
    """
   List all constraints for a specific problem
    
    Args:
        problem_id (int): the id of the related problem
        session (Session):
    
    Returns:
        [ListResponse]: list of constraints
    """

    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        is_admin_maintainer = RoleChecker.hasRole(user, Role.PROBLEM_MAINTAINER)
        if not problem or (not is_admin_maintainer and not problem.is_public):
            raise HTTPException(status_code=404, detail="Problem not found")
        
        query = session.query(ProblemConstraint).filter(ProblemConstraint.problem_id == problem_id)
        constraints : List[ProblemConstraint] = query.all()
        count : int = query.count()
        return {"data" : [ProblemConstraintDTO.model_validate(obj=obj) for obj in constraints], "count" : count}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read_constraint(problem_id: int, language_id: int, user: User, session: Session) -> ProblemConstraintDTO:
    """
    Get constraint by id

    Args:
        problem_id (int): the id of the related problem
        language_id (int): the id of the language
        session (Session):

    Returns:
        ProblemConstraintDTO: constraint
    """
    
    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        is_admin_maintainer = RoleChecker.hasRole(user, Role.PROBLEM_MAINTAINER)
        if not problem or (not is_admin_maintainer and not problem.is_public):
            raise HTTPException(status_code=404, detail="Problem not found")
        
        constraint : ProblemConstraint = session.query(ProblemConstraint).filter(ProblemConstraint.problem_id == problem_id,
                                                             ProblemConstraint.language_id == language_id).first()
        if not constraint:
            raise HTTPException(status_code=404, detail= "Problem constraint not found")
        return ProblemConstraintDTO.model_validate(obj=constraint)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create_constraint(problem_id: int, problemConstraintDTO: ProblemConstraintDTO, session: Session) -> ProblemConstraintDTO:
    """
    Create constraint
    
    Args:
        problem_id (int): the id of the related problem
        problemConstraintDTO (ProblemConstraintDTO): the constraint to create
        session (Session): 
    
    Returns: 
        ProblemConstraintDTO: constraint
    """
    
    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        language : Language = get_object_by_id(Language, session, problemConstraintDTO.language_id)
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")
        if problemConstraintDTO.memory_limit <= 0:
            raise HTTPException(status_code=400, detail="Memory limit must be positive")
        if problemConstraintDTO.time_limit <= 0:
            raise HTTPException(status_code=400, detail="Time limit must be positive")
        
        problem.increment_version_number()

        problemConstraint = ProblemConstraint(
            problem_id=problem_id,
            language_id=problemConstraintDTO.language_id,
            memory_limit=problemConstraintDTO.memory_limit,
            time_limit=problemConstraintDTO.time_limit
        )

        session.add(problemConstraint)
        session.commit()

        return problemConstraint

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def delete_constraints(problem_id: int, language_ids: List[int], session: Session) -> bool:
    """
    Delete constraint by id

    Args:
        problem_id (int): the id of the related problem
        language_ids (int): the ids of the languages
        session (Session): 
    
    Returns:
        deleted: bool
    """

    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        for language_id in language_ids:
            constraint : ProblemConstraint = session.query(ProblemConstraint).filter(ProblemConstraint.problem_id == problem_id,
                                                            ProblemConstraint.language_id == language_id).first()
            if not constraint:
                raise HTTPException(status_code=404, detail= "Problem constraint not found")
            problem.increment_version_number()
            session.delete(constraint)
        
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
    
def update_constraint(problem_id: int, constraint_update: ProblemConstraintDTO, session: Session) -> ProblemConstraintDTO:
    """
    Update constraint by id

    Args:
        problem_id (int): the id of the related problem
        constraint_update (ProblemConstraintDTO): the updated constraint
        session (Session): 

    Returns:
        ProblemConstraintDTO: constraint
    """
    
    try:
        problem : Problem = get_object_by_id(Problem, session, problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        language : Language = get_object_by_id(Language, session, constraint_update.language_id)
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")
        constraint : ProblemConstraint = session.query(ProblemConstraint).filter(ProblemConstraint.problem_id == problem_id,
                                                            ProblemConstraint.language_id == constraint_update.language_id).first()
        if not constraint:
            raise HTTPException(status_code=404, detail= "Problem constraint not found")
        if constraint_update.memory_limit <= 0:
            raise HTTPException(status_code=400, detail="Memory limit must be positive")
        if constraint_update.time_limit <= 0:
            raise HTTPException(status_code=400, detail="Time limit must be positive")
        
        problem.increment_version_number()

        constraint.memory_limit = constraint_update.memory_limit
        constraint.time_limit = constraint_update.time_limit

        session.commit()
        return ProblemConstraintDTO.model_validate(obj=constraint)
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#regiorn Judge

def get_versions(session: Session):
    """
    Get the problem versions
    """

    try:
        problems = session.query(Problem).where(Problem.is_public == True).all()
        response = {}
        for problem in problems:
            response[problem.id] = problem.config_version_number

        return response
         
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def get_problem_info(id: int, session: Session):
    """
    Get the problem configuration
    
    Args:
        id: int
    """

    try:
        problem: Problem = get_object_by_id_joined_with(Problem, session, id, [Problem.constraints])

        if not problem or not problem.is_public:
            raise HTTPException(status_code=404, detail="Problem not found")

        # serialize the problem
        problem_dto = ProblemJudgeDTO.model_validate(obj=problem)
        problem_dto.constraints = [ConstraintDTO.model_validate(obj=constraint) for constraint in problem.constraints]
        problem_dto.test_cases = [TestCaseDTO.model_validate(obj=test_case) for test_case in problem.test_cases]

        return problem_dto
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


#endregion