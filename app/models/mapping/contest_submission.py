from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String
from typing import List
from app.database import Base
from . import *

class ContestSubmission(Base):
    __tablename__ = 'contest_submissions'

    contest_id : Mapped[int] = mapped_column(Integer, FK('contests.id'), nullable=False, primary_key=True)
    submission_id : Mapped[int] = mapped_column(Integer, FK('submissions.id'), nullable=False, primary_key=True)