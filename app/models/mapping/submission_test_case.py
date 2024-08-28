from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String
from typing import Optional
from database import Base
from . import *

class SubmissionTestCase(Base):
    __tablename__ = 'submission_test_cases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    memory: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    input_name: Mapped[str] = mapped_column(String, nullable=False)
    result_id: Mapped[int] = mapped_column(Integer, FK('submission_results.id'), nullable=False)
    submission_id: Mapped[int] = mapped_column(Integer, FK('submissions.id'), nullable=False)

    # connected fields
    result: Mapped['SubmissionResult'] = relationship('SubmissionResult', back_populates='test_cases')
    submission: Mapped['Submission'] = relationship('Submission', back_populates='test_cases')