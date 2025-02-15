from pydantic import BaseModel, ConfigDict
from dataclasses import dataclass

# Request objects definition
class BaseRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        )

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
    user_type_id: int | None = None

@dataclass
class ListResponse(BaseRequest):
    """
    List Response DTO

    Attributes
        data (list): The list of data
        count (int): The count of data

    """
    data: list
    count: int

@dataclass
class IdListDTO(BaseRequest):
    """
    Id List DTO

    Attributes
        ids (list[int]): The list of ids

    """
    ids: list[int]
