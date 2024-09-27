from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.user import list

from app.database import get_session
from app.models import ListResponse, ListDTOBase

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)

@router.get("/", response_model=ListResponse, summary="List users", dependencies=[Depends(RoleChecker(["admin"]))])
async def list_users(body: ListDTOBase = Body(),  user=Depends(get_current_user), session=Depends(get_session)):
    """
    List users
    
    Returns:
        JSONResponse: response
    """

    try:
        users = list(body, user, session)
        return users
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO: from here
# @router.get("/{id}", response_model=ProblemDTO, summary="Get problem by id", dependencies=[Depends(RoleChecker(["admin"]))])
# async def read_problem(id: int, user=Depends(get_current_user), session=Depends(get_session)):
#     """
#     Get problem by id

#     Args:
#         id: int
#     """

#     try:
#         problem: ProblemDTO = read(id, user, session)
#         return problem
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

# @router.delete("/{id}", summary="Delete a problem by id", dependencies=[Depends(RoleChecker(["admin"]))])
# async def delete_problem(id: int, session=Depends(get_session)):
#     """
#     Delete contest by id
    
#     Args:
#         id: int
#     """

#     try:
#         deleted = delete(id, session)

#         if not deleted:
#             raise HTTPException(status_code=404, detail="Problem not found")
        
#         return JSONResponse(status_code=200, content={"message": "Problem deleted successfully"})
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

# @router.put("/{id}", summary= "Update a problem by id", dependencies=[Depends(RoleChecker(["admin"]))])
# async def update_problem(id: int, problem: ProblemDTO = Body(), session=Depends(get_session)): 
#     """
#     Update problem by id
    
#     Args:
#         id: int
#         problem: ProblemDTO

#     Returns:
#         JSONResponse
#     """

#     try:
#         problem = update(id, problem, session)
#         return JSONResponse(status_code=200, content={"message": "Problem update successfully"})
    
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#TODO:
#  [GET] list all users
#  [GET] read single user
#  [DELETE] delete a single user
#  [PUT] update a single user