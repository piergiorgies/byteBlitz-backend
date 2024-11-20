from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from app.auth_util.role import Role
from app.models import UserSignupDTO, UserLoginDTO, Token
from app.controllers.auth import signup as signup_controller, login as login_controller
from app.database import get_session
from app.auth_util.role_checker import RoleChecker

router = APIRouter(
    tags=["Authentication"],
    prefix="/auth"
)

@router.post("/signup", summary="Create a new user", response_description="User created")
async def signup(body: UserSignupDTO = Body(), session = Depends(get_session)) -> JSONResponse:
    """
    Create a new user

    Args: 
        body: UserSignupDTO
    
    Returns:
        JSONResponse: response
    """

    try:
        response, status_code = signup_controller(body, session)
        return JSONResponse(status_code=status_code, content=response)
    except HTTPException as http_exc:
        # Handle known HTTP exceptions raised within the controller
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )
    except Exception as e:
        # Handle unexpected errors
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )
    
@router.post("/login", summary="Login", response_description="User logged in", response_model=Token)
async def login(body: UserLoginDTO = Body(), session = Depends(get_session)):
    """
    Login a user

    Args: 
        body: UserLoginDTO
    
    Returns:
        JSONResponse: response
    """

    try:
        token: Token = login_controller(body, session)
        return token
        
    except HTTPException as http_exc:
        # Handle known HTTP exceptions raised within the controller
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )
    
# @router.post("/refresh", summary="Refresh token", response_description="Token refreshed", response_model=Token)
# async def refresh_token(token):

#     refresh_token_controller(token)
#     """
#     Refresh token

#     Returns:
#         JSONResponse: response
#     """

@router.get("/test", summary="Test", response_description="Test", dependencies=[Depends(RoleChecker([Role.ADMIN]))])
async def test():
    """
    Test

    Returns:
        JSONResponse: response
    """
    return JSONResponse(
        status_code=200,
        content={"detail": "Test successful"}
    )