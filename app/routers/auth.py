from fastapi import APIRouter, Depends, HTTPException, Body, Response
from fastapi.responses import JSONResponse
from app.schemas import LoginResponse, LoginRequest, ResetPasswordRequest, ChangeResetPasswordRequest
from app.controllers.auth import login as login_controller, reset_password as reset_pwd, change_reset_password as change_reset_pwd
from app.database import get_session

router = APIRouter(
    tags=["Authentication"],
    prefix="/auth"
)
    
@router.post("/login", summary="Login", response_description="User logged in", response_model=LoginResponse)
async def login(response: Response, body: LoginRequest = Body(), session = Depends(get_session)):
    """
    Login a user

    Args: 
        body: LoginRequest
    
    Returns:
        LoginResponse: response
    """

    try:
        result: LoginResponse = login_controller(body, session)
        response.set_cookie('token', result.access_token, httponly=True)
        return result
        
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )

@router.get("/logout", summary="Logout", response_description="User logged out")
def logout(response: Response) -> JSONResponse:
    """
    Logout a user clearing the cookies
    
    Returns:
        JSONResponse: response
    """
    try:
        response.delete_cookie('token', httponly=True)
        return JSONResponse(
            status_code=200,
            content={"detail": "Logout successful"},
            headers=response.headers
        )
        
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )
    
@router.post("/reset-password", summary="Reset Password", response_description="Password reset email sent")
def reset_password(body: ResetPasswordRequest = Body(), session = Depends(get_session)):
    """
    Reset the password of a user

    Args: 
        body: ResetPasswordRequest
    
    Returns:
        JSONResponse: response
    """
    try:
        reset_pwd(body, session)
        return JSONResponse(
            status_code=200,
            content={"detail": "Password reset email sent"}
        )
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )
    

@router.post("/change-reset-password", summary="Change Password", response_description="Password changed")
def change_reset_password(body: ChangeResetPasswordRequest = Body(), session = Depends(get_session)):
    """
    Change the password of a user
    
    Returns:
        JSONResponse: response
    """
    try:
        return change_reset_pwd(body, session)

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )