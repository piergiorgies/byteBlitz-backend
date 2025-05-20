from app.schemas.base import BaseRequest, BaseResponse
from dataclasses import dataclass

@dataclass
class LoginRequest(BaseRequest):
    """
    
    Login DTO

    Attributes
        username (str): The username of the user
        password (str): The password of the user


    """

    username: str
    password: str

@dataclass
class LoginResponse(BaseResponse):
    """

    Login Response DTO

    Attributes
        access_token (str): The access token of the user

    """
    access_token: str


@dataclass
class ResetPasswordRequest(BaseRequest):
    """
    
    Reset Password DTO

    Attributes
        email (str): The email of the user

    """

    email: str


@dataclass
class ChangeResetPasswordRequest(BaseRequest):
    """
    
    Change Reset Password DTO

    Attributes
        token (str): The token of the user
        password (str): The new password of the user

    """

    token: str
    password: str

@dataclass
class ChangePasswordRequest(BaseRequest):
    """
    
    Change Password DTO

    Attributes
        old_password (str): The old password of the user
        new_password (str): The new password of the user

    """

    old_password: str
    new_password: str