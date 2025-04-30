from app.schemas import BaseResponse


class Statistics(BaseResponse):
    """
    Statistics DTO

    Attributes
        users (int): The number of users
        problems (int): The number of problems
        contests (int): The number of contests
        submissions (int): The number of submissions

    """
    users: int
    problems: int
    contests: int
    submissions: int