from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer
from app.database import Base
from app.models import *

class ContestProblem(Base):
    __tablename__ = 'contest_problems'

    contest_id : Mapped[int] = mapped_column(Integer, FK('contests.id'), nullable=False, primary_key=True)
    problem_id : Mapped[int] = mapped_column(Integer, FK('problems.id'), nullable=False, primary_key=True)
    publication_delay : Mapped[int] = mapped_column(Integer, nullable=False, default=0)