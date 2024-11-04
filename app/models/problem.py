from numbers import Number
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
    """
    id : int | None = None
    title : str = None
    description : str | None = None
    points : int
    is_public : bool | None

class ProblemTestCaseDTO(BaseRequest):
    """
    Problem Test Case DTO

    Attributes:
        id (int): The id of the test case
        notes (str): Some additional notes for the test case
        input_name (str): The name of the input file for the test case
        output_name (str): The name of the output file with the expected results
        points (int): The amount of points given for solving this test case
        is_pretest (bool): If the test case is a pre-test or not
    """
    id : int = None
    notes : str | None = None
    input : str
    output : str
    points : int
    is_pretest : bool | None = False

class ProblemConstraintDTO(BaseRequest):
    """
    Problem Constraint DTO

    Attributes:
        problem_id (int): The id of the problem
        language_id (int): The id of the programming language chosen
        memory_limit (int): The memory limit (expressed in MB)
        time_limit (int): The time limit (expressed in ms)

    """
    problem_id : int = None
    language_id : int = None
    memory_limit : int
    time_limit : int