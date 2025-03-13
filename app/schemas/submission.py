from app.schemas.base import BaseRequest, BaseResponse, BaseListResponse
from typing import List
from datetime import datetime

class SubmissionCreate(BaseRequest):
    """
    Submission Create DTO

    Attributes:
        problem_id (int): The problem ID
        user_id (int): The user ID
        language_id (int): The language ID
        submitted_code (str): The submitted code
    """
    problem_id: int
    language_id: int
    submitted_code: str
    contest_id: int | None = None
    notes: str
    is_pretest_run: bool


class SubmissionResponse(BaseResponse):
    """
    Submission Response DTO

    Attributes:
        id (int): The submission ID
        problem_id (int): The problem ID
        user_id (int): The user ID
        language_id (int): The language ID
        submitted_code (str): The submitted code
        created_at (datetime): The date and time the submission was created
        updated_at (datetime): The date and time the submission was last updated
    """
    id: int
    problem_id: int
    user_id: int
    language_id: int
    submission_result_id: int
    submitted_code: str
    created_at: datetime
    score: int

class SubmissionTestCaseResult(BaseRequest):
    result_id: int
    number: int
    notes: str
    memory: int
    time: float

class SubmissionCompleteResult(BaseResponse):
    result_id: int
    stderr: str

class WSResult(BaseRequest):
    type: str
    result_id: int
    number: int
    notes: str
    memory: float
    time: float


class ProblemSubmissions(BaseListResponse):
    submissions: List[SubmissionResponse]