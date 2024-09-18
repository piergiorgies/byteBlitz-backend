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

    id: int | None = None
    notes: str | None = None
    contest_id: int | None = None
    problem_id: int = None
    user_id: int = None
    language_id: int = None

    