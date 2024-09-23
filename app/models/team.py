from app.models.base_dto import BaseRequest
from datetime import datetime

class TeamDTO(BaseRequest):
    """
    Team DTO

    Attributes:
        name (str): The name of the team
        logo_path (str): The path to the logo of the team

    """
    id: int | None = None
    name: str
    logo_path: str | None = None

class TeamUserDTO(BaseRequest):
    """
    Team User DTO

    Attributes:
        team_id (int): The id of the team
        user_id (int): The id of the user
    """
    id : int | None = None
    username: str = None
