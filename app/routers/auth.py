import requests
from fastapi import APIRouter, Depends, HTTPException, Body, Response
from fastapi.responses import JSONResponse, RedirectResponse
from app.models import Role
from app.schemas import (
    LoginResponse, LoginRequest, ResetPasswordRequest, 
    ChangeResetPasswordRequest, ChangePasswordRequest
)
from app.controllers.auth import (
    login as login_controller,
    reset_password as reset_pwd,
    change_reset_password as change_reset_pwd,
    create_github_user,
    change_pwd
)

from app.database import get_session
from app.config import settings
from app.util.jwt import get_current_user
from app.util.role_checker import RoleChecker


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
async def logout(response: Response) -> JSONResponse:
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
async def reset_password(body: ResetPasswordRequest = Body(), session = Depends(get_session)):
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
async def change_reset_password(body: ChangeResetPasswordRequest = Body(), session = Depends(get_session)):
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

@router.get("/github", summary="Github Login", response_description="Redirect to Github login page")
async def github_login():
    """Redirects the user to GitHub OAuth authorization page."""
    GITHUB_CLIENT_ID = settings.GITHUB_CLIENT_ID
    GITHUB_REDIRECT_URI = settings.GITHUB_REDIRECT_URI
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=user:email"
    return {"auth_url": github_auth_url}

@router.get("/github/callback", summary="Github Login Callback", response_description="Github login callback")
async def github_callback(code: str, session = Depends(get_session)):
    """
    Github login callback
    
    Returns:
        JSONResponse: response
    """

    try:

        user_json = _get_github_user_infos(code)
        result: LoginResponse = create_github_user(user_json=user_json, session=session)
        response = RedirectResponse(url=settings.APP_DOMAIN + f"/")
        response.set_cookie('token', result.access_token, httponly=True)
        return response
        
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )

def _get_github_user_infos(code: str):
    """
    Get the user infos from Github
    """

    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
        },
    )

    token_json = token_response.json()
    access_token = token_json["access_token"]

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_json = user_response.json()

    if user_json["email"] is None:
        # Fetch user emails
        user_emails_response = requests.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_emails_json = user_emails_response.json()

        # get the primary email
        for email in user_emails_json:
            if email["primary"]:
                user_json["email"] = email["email"]
                break



    return user_json
    
@router.post("/change-password", summary="Change Password", dependencies=[Depends(RoleChecker([Role.USER]))])
def change_password(body: ChangePasswordRequest = Body(), user = Depends(get_current_user), session = Depends(get_session)):
    """
    Change the password of a user
    
    Returns:
        JSONResponse: response
    """
    try:
        return change_pwd(body, user, session)

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(e)}
        )

