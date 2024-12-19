from app.models.base_dto import BaseRequest
from datetime import datetime

class JudgeCreateDTO(BaseRequest):
    """
    Judge DTO

    Attributes:
        id (int): The id of the judge
        name (str): The name of the judge
        description (str): The description of the judge
        url (str): The url of the judge
    """
    name: str
    key: str

class JudgeDTO(BaseRequest):
    """
    Judge DTO

    Attributes
        name (str): The name of the judge
        key (str): hashed password

    """
    id: int
    name: str
    last_connection: datetime
    status: bool