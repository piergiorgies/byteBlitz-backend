from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from app.auth_util.role_checker import RoleChecker
from app.auth_util.jwt import get_current_user
from app.controllers.problem import list, read

from app.models import ListResponse
from app.database import get_session
from app.models.base_dto import ListDTOBase
from app.models import ProblemDTO

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)

#region Problem

#TODO: manage problem visibility --> admin: all problems, user: only public problems
@router.get("/", response_model=ListResponse, summary="List problems", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def list_problems(body: ListDTOBase = Body(), session=Depends(get_session), user=Depends(get_current_user)):
    """
    List problems
    
    Returns:
        JSONResponse: response
    """

    # try:
    #     contests = list(body, user, session)
    #     return contests
    
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.get("/{id}", response_model=ProblemDTO, summary="Get problem by id", dependencies=[Depends(RoleChecker(["admin", "user"]))])
async def read_problem(id: int, session=Depends(get_session), user=Depends(get_current_user)):
    """
    Get problem by id

    Args:
        id: int
    """

    # try:
    #     contest: ContestDTO = read(id, session)
    #     return contest
    
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
#endregion

#TODO: gestione delle api tra le entità correlate in maniera GRANULARE
# es. per creare un problema esistono due (minimo) endpoint:
# 1. creazione del problema
# 2. creazione delle problem_constraints
# ecc...