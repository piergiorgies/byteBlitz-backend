from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String, DateTime
from typing import Optional, List
from datetime import datetime
from app.database import Base
from . import *

class Contest(Base):
    __tablename__ = 'contests'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String, nullable=False)
    description : Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_datetime : Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime : Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_public : Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    is_registration_open : Mapped[bool] = mapped_column(Integer, nullable=False, default=False)

    # connected fields
    problems : Mapped[List['Problem']] = relationship('Problem', secondary='contest_problems', back_populates='contests', cascade='all, delete', passive_deletes=True)
    contest_problems : Mapped[List['ContestProblem']] = relationship('ContestProblem', back_populates='contest', cascade='all, delete', passive_deletes=True, overlaps='problems, contests')
    users : Mapped[List['User']] = relationship('User', secondary='contest_users', back_populates='contests', cascade='all, delete', passive_deletes=True)
    submissions: Mapped[List['Submission']] = relationship('Submission', secondary='contest_submissions', back_populates='contests', cascade='all, delete', passive_deletes=True)
    teams: Mapped[List['Team']] = relationship('Team', secondary='contest_teams', back_populates='contests')