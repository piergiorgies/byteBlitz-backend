from app.models.base_dto import BaseRequest
from datetime import datetime

# class ContestDTO(BaseRequest):
#     """
#     Contest DTO

#     Attributes:
#         name (str): The name of the contest
#         description (str): The description of the contest
#         start_time (datetime): The start time of the contest
#         end_time (datetime): The end time of the contest

#     """
#     id: int | None = 0
#     name: str
#     description: str
#     start_datetime: datetime
#     end_datetime: datetime
#     users: list["ContestUserDTO"] | None = None
#     contest_problems: list["ContestProblemDTO"] | None = None
class ContestProblemDTO(BaseRequest):
    problem_id: int
    publication_delay: int

class ContestUserDTO(BaseRequest):
    id: int
    username: str

class ContestCreate(BaseRequest):
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    user_ids: list[int]
    problems: list["ContestProblemDTO"]


class ContestUpdate(BaseRequest):
    name: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    user_ids: list[int] | None = None
    problems: list["ContestProblemDTO"] | None = None

class ContestRead(BaseRequest):
    id: int
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    users: list["ContestUserDTO"] | None = None
    contest_problems: list["ContestProblemDTO"] | None = None

class ContestScoreboardDTO(BaseRequest):
    """
    Contest Scoreboard DTO

    Attributes:
        userteams (list[str]): oredered scoreboard rows
        problems (list[str]): ordered scoreboard columns
        scores (list[list[int]]): scores of each user/team for each problem (scoreboard cells)
    """
    userteams : list[str]
    problems : list[str]
    scores : list[list[int]]

class ContestSubmissionDTO(BaseRequest):
    """
    Contest Submission DTO

    Attributes:
        contest_id (int): The id of the contest
        submission_id (int): The id of the submission
    """
    id : int
    submission_id : int