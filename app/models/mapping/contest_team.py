from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String
from typing import List
from database import Base
from . import *

class ContestTeam(Base):
    __tablename__ = 'contest_teams'

    contest_id: Mapped[int] = mapped_column(Integer, FK('contests.id'), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, FK('teams.id'), primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)