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
