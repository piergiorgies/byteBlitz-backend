from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String, Boolean, DateTime
from datetime import datetime
from typing import Optional, List
from app.database import Base
from . import *


class Problem(Base):
    __tablename__ = 'problems'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    config_version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, FK('users.id'), nullable=False)

    # connected fields
    author: Mapped['User'] = relationship('User', back_populates='created_problems')
    constraints: Mapped[List['ProblemConstraint']] = relationship('ProblemConstraint', back_populates='problem', cascade='all, delete', passive_deletes=True)
    test_cases: Mapped[List['ProblemTestCase']] = relationship('ProblemTestCase', back_populates='problem', cascade='all, delete', passive_deletes=True)
    contests: Mapped[List['Contest']] = relationship('Contest', secondary='contest_problems', back_populates='problems')
    submissions: Mapped[List['Submission']] = relationship('Submission', back_populates='problem', cascade='all, delete', passive_deletes=True)

    def increment_version_number(self):
        self.config_version_number += 1