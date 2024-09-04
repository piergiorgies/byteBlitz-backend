from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String
from typing import List
from app.database import Base
from . import *

class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo_path: Mapped[str] = mapped_column(String, nullable=False)

    # connected fields
    users: Mapped['List[User]'] = relationship('User', secondary='team_users', back_populates='teams')
    contests: Mapped['List[Contest]'] = relationship('Contest', secondary='contest_teams', back_populates='teams')