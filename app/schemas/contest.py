from datetime import datetime
from app.schemas.base import BaseRequest, BaseResponse, BaseListResponse
from app.schemas.problem import ProblemInfo
from typing import Optional, List

class ContestCreate(BaseRequest):
    """
    
    Contest Create DTO

    Attributes
        name (str): The name of the contest
        description (str): The description of the contest
        start_datetime (datetime): The start date of the contest
        end_datetime (datetime): The end date of the contest
        problems (List[ContestProblem]): The problems of the contest
        users (List[int]): The users of the contest

    """

    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    problems: List["ContestProblem"]
    users: List[int]

class ContestUpdate(BaseRequest):
    """
    
    Contest Update DTO

    Attributes
        name (str): The name of the contest
        description (str): The description of the contest
        start_datetime (datetime): The start date of the contest
        end_datetime (datetime): The end date of the contest
        problems (List[ContestProblem]): The problems of the contest
        users (List[int]): The users of the contest

    """

    name: Optional[str]
    description: Optional[str]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    problems: Optional[List["ContestProblem"]]
    users: Optional[List[int]]

class ContestProblem(BaseRequest):
    """
    
    Problem Contest DTO

    Attributes
        problem_id (int): The id of the problem
        publication_delay (int): The publication delay of the problem

    """

    problem_id: int
    publication_delay: int


class ContestBase(BaseResponse):
    """
    
    Contest Base DTO

    Attributes
        id (int): The id of the contest
        name (str): The name of the contest
        description (str): The description of the contest
        start_datetime (datetime): The start date of the contest
        end_datetime (datetime): The end date of the contest

    """

    id: int
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
class ContestRead(ContestBase):
    """
    
    Contest Read DTO

    Attributes
        id (int): The id of the contest
        name (str): The name of the contest
        description (str): The description of the contest
        start_datetime (datetime): The start date of the contest
        end_datetime (datetime): The end date of the contest
        problems (List[ContestProblem]): The problems of the contest
        users (List[int]): The users of the contest

    """
    contest_problems: List["ContestProblem"]
    users: List[int]

class ContestListResponse(BaseListResponse):
    """
    
    Contest List Response DTO

    Attributes
        contests (List[ContestRead]): The contests

    """
    contests: List[ContestBase]


class ContestScoreboard(BaseResponse):
    userteams: List[str]
    problems: List[str]
    scores: List[List[int]]

class ContestInfo(BaseResponse):
    id: int
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    duration: int
    n_problems: int
    n_participants: int
    n_submissions: int

class ContestInfos(BaseResponse):
    past: List[ContestInfo]
    ongoing: List[ContestInfo]
    upcoming: List[ContestInfo]

class ContestUserInfo(BaseResponse):
    username: str

class PastContest(BaseResponse):
    id: int
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    duration: int
    n_problems: int
    scoreboard: ContestScoreboard
    users: List[ContestUserInfo]

class UpcomingContest(BaseResponse):
    id: int
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    duration: int
    n_participants: int
    n_problems: int
    problems: List["ProblemInfo"]
