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
