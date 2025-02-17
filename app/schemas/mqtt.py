from app.schemas.base import BaseRequest

class Row(BaseRequest):
    """
    Row DTO

    Attributes:
        name (str): The name of the user/team
        score (int): The score of the user/team
    """
    n: str
    p: int

class ScoreboardDTO(BaseRequest):
    """
    Scoreboard DTO

    Attributes:
        classifica (list[Row]): The list of the rows of the scoreboard

    """
    classifica: list[Row]
    
class NotificationDTO(BaseRequest):
    """
    Notification DTO

    Attributes:
        message (str): The message of the notification
    """
    message: str

