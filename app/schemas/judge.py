from app.schemas import BaseRequest, BaseResponse
from datetime import datetime

class JudgeCreate(BaseRequest):
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

class JudgeResponse(BaseRequest):
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

class JudgeListResponse(BaseResponse):
    """
    Judge List Response DTO

    Attributes
        judges (List[JudgeResponse]): A list of judges

    """
    judges: list[JudgeResponse]

class Constraint(BaseResponse):
    language_id: int
    memory_limit: int
    time_limit: int

class TestCase(BaseResponse):
    input: str
    output: str
    points: int
    is_pretest: bool
class JudgeProblem(BaseResponse):
    id : int
    config_version_number: int
    constraints: list[Constraint]
    test_cases: list[TestCase]

