from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer, String, DateTime
from app.database import Base
from datetime import datetime
from typing import List
from . import *

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    salt: Mapped[str] = mapped_column(String, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    user_type_id: Mapped[int] = mapped_column(Integer, FK('user_types.id'), nullable=False)

    # connected fields
    user_type: Mapped['UserType'] = relationship('UserType', back_populates='users')
    created_problems: Mapped[List['Problem']] = relationship('Problem', back_populates='author')
    submissions: Mapped[List['Submission']] = relationship('Submission', back_populates='user')
    contests: Mapped[List['Contest']] = relationship('Contest', secondary='contest_users', back_populates='users')
    teams: Mapped[List['Team']] = relationship('Team', secondary='team_users', back_populates='users')

