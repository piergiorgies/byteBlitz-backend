from app.models.base_dto import BaseRequest

class SubmissionDTO(BaseRequest):
    """
    Submission DTO

    Attributes:
        id (int | None): The submission ID
        notes (str | None): The submission notes
        problem_id (int): The problem ID
        user_id (int): The user ID
        language_id (int): The language ID
    """

    id: int | None = 0
    notes: str | None = None
    contest_id: int | None = None
    problem_id: int
    user_id: int
    language_id: int
    submitted_code: str

class SubmissionTestCaseDTO(BaseRequest):
    """
    Submission test case DTO

    Attributes:
        id (int): The test case ID
        number (int): The test case number
        notes (str): The test case notes
        memory (float): The test case memory
        time (float): The test case time
        result_id (int): The test case result ID
        submission_id (int): The test case submission ID
    """

    number: int
    notes: str
    memory: float
    time: float
    result_id: int

class ResultDTO(BaseRequest):
    """
    Result DTO

    Attributes:
        result_id (int): The result ID
    """
    
    result_id: int