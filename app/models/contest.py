from app.models.base_dto import BaseRequest
from datetime import datetime

class ContestDTO(BaseRequest):
    """
    Contest DTO

    Attributes:
        name (str): The name of the contest
        description (str): The description of the contest
        start_time (datetime): The start time of the contest
        end_time (datetime): The end time of the contest

    """
    id: int | None = None
    name: str = None
    description: str = None
    start_datetime: datetime = None
    end_datetime: datetime = None

class ContestUserDTO(BaseRequest):
    """
    Contest User DTO

    Attributes:
        contest_id (int): The id of the contest
        user_id (int): The id of the user
    """
    username: str = None
    score: int | None = None

class ContestTeamDTO(BaseRequest):
    """
    Contest Team DTO

    Attributes:
        contest_id (int): The id of the contest
        team_id (int): The id of the team
    """
    name: str = None
    score: int | None = None