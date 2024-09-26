from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String, Float
from typing import Optional
from app.database import Base
from . import *

class SubmissionTestCase(Base):
    """
    The submission test case model

    Attributes:
        id (int): The test case id
        number (int): The test case number
        notes (str): The test case notes
        memory (float): The test case memory
        time (float): The test case time
        input_name (str): The test case input name
        result_id (int): The test case result id
        submission_id (int): The test case submission id

        result (SubmissionResult): The submission result
        submission (Submission): The submission
    """

    __tablename__ = 'submission_test_cases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    memory: Mapped[float] = mapped_column(Float, nullable=False)
    time: Mapped[float] = mapped_column(Float, nullable=False)
    # input_name: Mapped[str] = mapped_column(String, nullable=False)
    result_id: Mapped[int] = mapped_column(Integer, FK('submission_results.id'), nullable=False)
    submission_id: Mapped[int] = mapped_column(Integer, FK('submissions.id'), nullable=False)

    # connected fields
    result: Mapped['SubmissionResult'] = relationship('SubmissionResult', back_populates='test_cases')
    submission: Mapped['Submission'] = relationship('Submission', back_populates='test_cases')