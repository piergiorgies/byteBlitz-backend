from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.problem import list, read, create, delete, update

from app.models import ListResponse, problem
from app.database import get_session
from app.models.base_dto import ListDTOBase
from app.models import ProblemDTO, ProblemTestCaseDTO

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)

#region Problem

#TODO: manage problem visibility --> admin: all problems, user: only public problems
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

@router.get("/{id}/testcases", response_model=ProblemTestCaseDTO, summary= "List problem testcases by problem id", dependencies=[Depends(RoleChecker(["admin"]))])
async def list_problem_test_cases(id: int, body: ListDTOBase = Body(), session=Depends(get_session)):
    """
    List all test cases by problem id
    
    Args:
        id: int
    
    Returns:
        JSONResponse
    """

    try:
        problem_test_cases = list_test_cases(id, body, session)
        return problem_test_cases
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}/testcases/{id}", response_model=ProblemTestCaseDTO, summary= "Get a specific testcase by id", dependencies=[RoleChecker(["admin"])])
async def get_specific_test_case(problemID: int, testcaseID: int, session=Depends(get_session)):
    """
    Get specific test case by id
    
    Args:
        problemID: int
        testcaseID: int
    
    Returns:
        JSONRresponse: response
    """

    try:
        test_case = get_test_case(problemID, testcaseID, session)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/{id}/testcases", summary= "Create problem test case", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_problem_test_case(problemID: int, problem_test_case : ProblemTestCaseDTO, session=Depends(get_session)):
    """
    Create a problem test case
    
    Args:
        problemID: int
        problem_test_case: ProblemTestCaseDTO
    
    Returns:
        JSONResponse: response
    """

    try:
        problem_test_case = create_test_case(problem_test_case, session)
        return JSONResponse(status_code=201, content={"message": "Problem test case created successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO: Valutare se aggiungere un endpoint per la rimozione completa di tutti i testcases
@router.delete("/{id}/testcases/{id}", summary= "Delete problem test case", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_problem_test_case(problemID: int, testcaseID: int, session=Depends(get_session)):
    """
    Delete a problem test case by id
    
    Args:
        problemID: int
        testcaseID: int
    
    Returns:
        JSONResponse: response
    """

    try:
        deleted = delete_test_case(problemID, testcaseID, session)
        if not deleted:
            raise HTTPException(status_code=404, detail="Problem or testcase not found")
        
        return JSONResponse(status_code=200, content={"message": "Test case removed successfully"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.put("/{id}/testcases/{id}", summary= "Update a testcase by id", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_problem_test_case(problemID: int, testcaseID: int, test_case: ProblemTestCaseDTO = Body(), session=Depends(get_session)):
    """
    Update a problem test case by id
    
    Args:
        problemID: int
        testcaseID: id
        test_case: ProblemTestCaseDTO
        
    Returns:
        JSONResponse: response
    """
    try:
        test_case = update_test_case(problemID, testcaseID, session)
        return JSONResponse(status_code=200, content={"message": "Problem test case updated"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
#endregion