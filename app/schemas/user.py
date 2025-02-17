from app.schemas import BaseRequest, BaseResponse
from datetime import datetime

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

class UserListResponse(BaseResponse):
    """
    User List Response DTO

    Attributes
        users (List[UserResponse]): A list of users

    """
    data: list[UserResponse]
    count: int
