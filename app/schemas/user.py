from app.schemas.base import BaseRequest, BaseResponse, BaseListResponse
from datetime import datetime
from typing import Dict

class UserCreate(BaseRequest):
    """
    User Create DTO

    Attributes
        username (str): The username of the user
        email (str): The email of the user
        password (str): The password of the user
        user_type_id (int): The user type id of the user

    """
    username: str
    email: str
    password: str
    user_type_id: int | None = None

class UserUpdate(BaseRequest):
    """
    User Update DTO

    Attributes
        username (str): The username of the user
        email (str): The email of the user
        password (str): The password of the user
        user_type_id (int): The user type id of the user

    """
    username: str | None = None
    email: str | None = None
    password: str | None = None
    user_type_id: int | None = None

class UserResponse(BaseResponse):
    """
    User Response DTO

    Attributes
        id (int): The id of the user
        username (str): The username of the user
        email (str): The email of the user
        created_at (datetime): The date and time the user was created
        updated_at (datetime): The date and time the user was last updated

    """
    id: int
    username: str
    email: str
    registered_at: datetime
    user_type_id: int

class UserListResponse(BaseListResponse):
    """
    User List Response DTO

    Attributes
        users (List[UserResponse]): A list of users

    """
    users: list[UserResponse]

class ProfileResponse(BaseResponse):
    acceptance: float
    total_year_sub: int
    submission_map: Dict[datetime, int]
    email: str
    username: str
    registered_at: datetime
    has_password: bool
    

class SubmissionRecord(BaseResponse):
    created_at: datetime
    problem_id: int
    problem_title: str
    result_code: str
    execution_time: float
    memory: int
    language_name: str

class SubmissionHistory(BaseListResponse):
    submissions: list[SubmissionRecord]
