from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String
from typing import Optional, List
from database import Base
from . import *

class SubmissionResult(Base):
    __tablename__ = 'submission_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # connected fields
    test_cases: Mapped[List['SubmissionTestCase']] = relationship('SubmissionTestCase', back_populates='result')
    submission: Mapped['Submission'] = relationship('Submission', back_populates='result')