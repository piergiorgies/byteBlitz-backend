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
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime

class ContestUserDTO(BaseRequest):
    """
    Contest User DTO

    Attributes:
        contest_id (int): The id of the contest
        user_id (int): The id of the user
    """
    id : int | None = None
    username: str = None
    score: int | None = 0

class ContestTeamDTO(BaseRequest):
    """
    Contest Team DTO

    Attributes:
        contest_id (int): The id of the contest
        team_id (int): The id of the team
    """
    id : int | None = None
    name: str = None
    score: int | None = 0

class ContestProblemDTO(BaseRequest):
    """
    Contest Problem DTO

    Attributes:
        contest_id (int): The id of the contest
        problem_id (int): The id of the problem
    """
    id : int = None
    title: str | None = None
    publication_delay: int | None = 0