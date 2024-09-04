from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, String, Integer, Boolean
from typing import List, Optional
from app.database import Base
from . import *

class ProblemTestCase(Base):
    __tablename__ = 'problem_test_cases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    input_name: Mapped[str] = mapped_column(String, nullable=False)
    output_name: Mapped[str] = mapped_column(String, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    is_pretest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    problem_id: Mapped[int] = mapped_column(Integer, FK('problems.id'), nullable=False)
    
    # connected fields
    problem = relationship('Problem', back_populates='test_cases')
    