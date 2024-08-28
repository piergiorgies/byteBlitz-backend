from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String
from typing import List
from database import Base
from . import *

class Language(Base):
    __tablename__ = 'languages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    file_extension: Mapped[str] = mapped_column(String, nullable=False)

    # connected fields
    submissions: Mapped[List['Submission']] = relationship('Submission', back_populates='language')
    constraints: Mapped[List['ProblemConstraint']] = relationship('ProblemConstraint', back_populates='language')