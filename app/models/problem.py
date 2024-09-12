from app.models.base_dto import BaseRequest
from datetime import datetime

class ProblemDTO(BaseRequest):
    """
    Problem DTO

    Attributes:
        id (int): The id of the problem
        title (str): The title of the problem
        description (str): The description of the problem
        points (int): The amount of points of the problem
        is_public (bool): The visibility of the problem
        config_version_number (int): The configuration number of the problem
    """
    id : int | None = None
    title: str = None
    description: str | None = None
    points: int
    is_public: bool | None

#TODO: config_version_number viene aggiornato ogni volta che il problema, una sua constraint
# o un suo testcase ecc... (ci siamo capiti) viene modificato/creato

class ProblemTestCaseDTO(BaseRequest):
    pass
    #TODO: everything

class ProblemConstraintDTO(BaseRequest):
    pass
    #TODO: everything