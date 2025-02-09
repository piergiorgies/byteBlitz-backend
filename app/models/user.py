from app.models.base_dto import BaseRequest
from datetime import datetime

class UserDTO(BaseRequest):
    """
    User DTO

    Attributes:
        id (int): The id of the user
        username (str): The username of the user
        email (str): The email of the user
        registered_at (datetime): The date and time of the registration
        user_type_id (int) : The id of the the user type
    """
    id : int | None = None
    username : str
    email : str
    registered_at : datetime | None = None
    user_type_id : int

class UserPermissionsDTO(BaseRequest):
    """
    User Permissions DTO

    Attributes:
        user_type_id (int) : The id of the the user type
    """
    user_type_id : int