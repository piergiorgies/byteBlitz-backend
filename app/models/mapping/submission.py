from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String, DateTime, Boolean
from typing import Optional, List
from datetime import datetime
from app.database import Base
from . import *

class Submission(Base):
    __tablename__ = 'submissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submitted_code: Mapped[str] = mapped_column(String, nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, FK('problems.id', ondelete='cascade'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, FK('users.id'), nullable=False)
    language_id: Mapped[int] = mapped_column(Integer, FK('languages.id'), nullable=False)
    submission_result_id: Mapped[int] = mapped_column(Integer, FK('submission_results.id'), nullable=True)
    is_pretest_run: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # connected fields
    problem: Mapped['Problem'] = relationship('Problem', back_populates='submissions')
    user: Mapped['User'] = relationship('User', back_populates='submissions')
    language: Mapped['Language'] = relationship('Language', back_populates='submissions')
    contests: Mapped[List['Contest']] = relationship('Contest', secondary='contest_submissions', back_populates='submissions')
    test_cases: Mapped[List['SubmissionTestCase']] = relationship('SubmissionTestCase', back_populates='submission', cascade='all, delete', passive_deletes=True)
    result: Mapped['SubmissionResult'] = relationship('SubmissionResult', back_populates='submission')