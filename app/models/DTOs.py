from pydantic import BaseModel, ConfigDict
from typing import Optional

from dataclasses import dataclass

# Request objects definition
class BaseRequest(BaseModel):
    model_config = ConfigDict()

@dataclass
class Token(BaseRequest):
    """
    Token DTO

    Attributes
        access_token (str): The access token
        refresh_token (str): The refresh token

    """
    access_token: str
    refresh_token: str

@dataclass
class UserLoginDTO(BaseRequest):
    """
    User Login DTO

    Attributes
        username (str): The username of the user
        password (str): The password of the user

    """
    username: str
    password: str

@dataclass
class UserSignupDTO(BaseRequest):
    """
    User Signup DTO

    Attributes
        username (str): The username of the user
        email (str): The email of the user
        password (str): The password of the user

    """
    username: str
    email: str
    password: str
