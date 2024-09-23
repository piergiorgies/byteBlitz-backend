from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.problem import list, read, create, delete, update
from app.controllers.problem import list_test_cases, read_test_case, create_test_case, delete_test_case, update_test_case
from app.controllers.problem import list_constraints, read_constraint, create_constraint, delete_constraint, update_constraint

from app.models import ListResponse
from app.database import get_session
from app.models.base_dto import ListDTOBase
from app.models import ProblemDTO, ProblemTestCaseDTO, ProblemConstraintDTO

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)

#region Problem

@router.get("/", response_model=ListResponse, summary="List problems", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def list_problems(body: ListDTOBase = Body(),  user=Depends(get_current_user), session=Depends(get_session)):
    """
    List problems
    
    Returns:
        JSONResponse: response
    """

    try:
        problems = list(body, user, session)
        return problems
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=ProblemDTO, summary="Get problem by id", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def read_problem(id: int, user=Depends(get_current_user), session=Depends(get_session)):
    """
    Get problem by id

    Args:
        id: int
    """

    try:
        problem: ProblemDTO = read(id, user, session)
        return problem
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/", summary="Create a problem", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_problem(problem: ProblemDTO = Body(), user=Depends(get_current_user), session=Depends(get_session)):
    """
    Create a problem
    
    Args:
        problem: ProblemDTO
    
    returns:
        JSONResponse: response
    """

    try:
        problem = create(problem, user, session)
        return JSONResponse(status_code=201, content={"message": "Problem created successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO: CANCELLAZIONE CON LISTA
@router.delete("/{id}", summary="Delete a problem by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_problem(id: int, session=Depends(get_session)):
    """
    Delete contest by id
    
    Args:
        id: int
    """

    try:
        deleted = delete(id, session)

        if not deleted:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return JSONResponse(status_code=200, content={"message": "Problem deleted successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.put("/{id}", summary= "Update a problem by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_problem(id: int, problem: ProblemDTO = Body(), session=Depends(get_session)): 
    """
    Update problem by id
    
    Args:
        id: int
        problem: ProblemDTO

    Returns:
        JSONResponse
    """

    try:
        problem = update(id, problem, session)
        return JSONResponse(status_code=200, content={"message": "Problem update successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Probem Test Cases

@router.get("/{id}/testcases", response_model=ProblemTestCaseDTO, summary= "List problem testcases", dependencies=[Depends(RoleChecker(["admin"]))])
async def list_problem_test_cases(id: int, session=Depends(get_session)):
    """
    List all test cases for a specific problem
    
    Args:
        id (int): the id of the related problem 
    """

    try:
        problem_test_cases = list_test_cases(id, session)
        return problem_test_cases
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/testcase", response_model=ProblemTestCaseDTO, summary= "Get a specific testcase by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def get_specific_test_case(id: int, test_case_id : int = Body(), session=Depends(get_session)):
    """
    Get a specific test case
    
    Args:
        id (int): the id of the related problem
        test_case_id (int) : the id of the test case
    """

    try:
        test_case = read_test_case(id, test_case_id, session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/{id}/testcases", summary= "Create problem test case", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_problem_test_case(id: int, problem_test_case : ProblemTestCaseDTO = Body(), session=Depends(get_session)):
    """
    Create a problem test case
    
    Args:
        id (int): the id of the related problem
        problem_test_case (ProblemTestCaseDTO):
    """

    try:
        created = create_test_case(id, problem_test_case, session)
        return JSONResponse(status_code=201, content={"message": "Problem test case created successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO: CANCELLAZIONE CON LISTA
@router.delete("/{id}/testcases", summary= "Delete problem test case by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_problem_test_case(id: int, test_case_id : int = Body(), session=Depends(get_session)):
    """
    Delete a problem test case
    
    Args:
        id (int): the id of the related problem
        test_case_id (int) : the id of the test case
    """
    try:
        deleted = delete_test_case(id, test_case_id, session)
        if not deleted:
            raise HTTPException(status_code=404, detail="Problem test case or problem not found")
        
        return JSONResponse(status_code=200, content={"message": "Problem test case removed successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.put("/{id}/testcases", summary= "Update problem test case by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_problem_test_case(id: int, test_case: ProblemTestCaseDTO = Body(), session=Depends(get_session)):
    """
    Update a problem test case
    
    Args:
        id (int): the id of the related problem
        test_case (ProblemTestCaseDTO): the updated testcase
    """

    try:
        updated = update_test_case(id, test_case, session)
        return JSONResponse(status_code=200, content={"message": "Problem test case updated"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

#region Problem Constraints

@router.get("/{id}/constraints", response_model=ProblemConstraintDTO, summary= "List problem constraints", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def list_problem_constraints(id: int, session=Depends(get_session)):
    """
    List all constraints for a specific problem
    
    Args:
        id (int): the id of the related problem 
    """
    
    try:
        problem_constraints = list_constraints(id, session)
        return problem_constraints
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/constraint", response_model=ProblemConstraintDTO, summary= "Get a specific constraint by language", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def get_specific_constraint(id: int, language_id : int = Body(), session=Depends(get_session)):
    """
    Get a specific constraint by language
    
    Args:
        id (int): the id of the related problem
        language_id (int): the id of the language
    """

    try:
        problem_constaint = read_constraint(id, language_id, session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/{id}/constraints", summary= "Create problem constraint", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_problem_constraint(id: int, problem_constraint : ProblemConstraintDTO = Body(), session=Depends(get_session)):
    """
    Create a problem constraint
    
    Args:
        id (int): the id of the related problem
        problem_constraint (ProblemConstraintDTO): the constraint to create
    """

    try:
        created = create_constraint(id, problem_constraint, session)
        return JSONResponse(status_code=201, content={"message": "Problem constraint created successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO: CANCELLAZIONE CON LISTA
@router.delete("/{id}/constraints", summary= "Delete problem constraint by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_problem_constraint(id: int, language_id : int = Body(), session=Depends(get_session)):
    """
    Delete a problem constraint
    
    Args:
        id (int): the id of the related problem
        language_id (int): the id of the language
    """

    try:
        deleted = delete_constraint(id, language_id, session)
        if not deleted:
            raise HTTPException(status_code=404, detail="Problem constraint or programming language not found")
        
        return JSONResponse(status_code=200, content={"message": "Problem constraint removed successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.put("/{id}/constraints", summary= "Update problem constraint by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_problem_constraint(id: int, constraint: ProblemConstraintDTO = Body(), session=Depends(get_session)):
    """
    Update a problem constraint
    
    Args:
        id (int): the id of the related problem
        constraint (ProblemConstraintDTO): the updated constraint
    """

    try:
        updated = update_constraint(id, constraint, session)
        return JSONResponse(status_code=200, content={"message": "Problem constraint updated"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion