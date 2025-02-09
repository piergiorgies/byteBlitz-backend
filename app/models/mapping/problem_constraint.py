from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String
from typing import Optional
from app.database import Base
from . import *

class ProblemConstraint(Base):
    __tablename__ = 'problem_constraints'

    problem_id: Mapped[int] = mapped_column(Integer, FK('problems.id', ondelete='cascade'), primary_key=True)
    language_id: Mapped[int] = mapped_column(Integer, FK('languages.id', ondelete='cascade'), primary_key=True)
    memory_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)

    # connected fields
    problem: Mapped['Problem'] = relationship('Problem', back_populates='constraints')
    language: Mapped['Language'] = relationship('Language', back_populates='constraints')

    @property
    def language_name(self) -> str:
        return self.language.name