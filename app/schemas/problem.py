from app.schemas.base import BaseRequest, BaseResponse, BaseListResponse
from typing import List, Optional
from app.models import Difficulty

class ProblemTestCase(BaseRequest):
    input: str
    output: str
    points: int
    is_pretest: bool

class ProblemConstraint(BaseRequest):
    language_id: int
    memory_limit: int
    time_limit: int


class ProblemCreate(BaseRequest):
    title: str
    description: str
    points: int
    is_public: bool
    test_cases: List[ProblemTestCase]
    constraints: List[ProblemConstraint]
    difficulty: Difficulty

class ProblemUpdate(BaseRequest):
    title: Optional[str]
    description: Optional[str]
    points: Optional[int]
    is_public: Optional[bool]
    test_cases: Optional[List[ProblemTestCase]]
    constraints: Optional[List[ProblemConstraint]]
    difficulty: Optional[Difficulty]

class ProblemAuthor(BaseResponse):
    id: int
    username: str
class ProblemRead(BaseResponse):
    title: str
    description: str
    points: int
    is_public: bool
    author: ProblemAuthor
    difficulty: Difficulty
    test_cases: List[ProblemTestCase]
    constraints: List[ProblemConstraint]


class ProblemInfo(BaseResponse):
    id: int
    title: str
    points: int
    languages: List[str]
    is_public: bool

class ProblemListResponse(BaseListResponse):
    problems: List[ProblemInfo]
