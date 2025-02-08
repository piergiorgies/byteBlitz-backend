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
    id: int | None = 0
    name: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    users: list["ContestUserDTO"] | None = None
    problems: list["ContestProblemDTO"] | None = None

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

class ContestUserDTO(BaseRequest):
    """
    Contest User DTO

    Attributes:
        contest_id (int): The id of the contest
        user_id (int): The id of the user
        score (int): The score of a user
    """
    id : int | None = 0
    username: str
    
class ContestTeamDTO(BaseRequest):
    """
    Contest Team DTO

    Attributes:
        contest_id (int): The id of the contest
        team_id (int): The id of the team
    """
    id : int | None = 0
    name: str
    score: int | None = 0

class ContestProblemDTO(BaseRequest):
    """
    Contest Problem DTO

    Attributes:
        contest_id (int): The id of the contest
        problem_id (int): The id of the problem
    """
    id : int
    title: str | None = None
    publication_delay: int | None = 0

class ContestSubmissionDTO(BaseRequest):
    """
    Contest Submission DTO

    Attributes:
        contest_id (int): The id of the contest
        submission_id (int): The id of the submission
    """
    id : int
    submission_id : int