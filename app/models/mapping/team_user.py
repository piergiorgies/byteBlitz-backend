from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey as FK, Integer, DateTime
from app.database import Base
from datetime import datetime

class TeamUser(Base):
    __tablename__ = 'team_users'

    team_id: Mapped[int] = mapped_column(Integer, FK('teams.id'), nullable=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, FK('users.id'), nullable=False,primary_key=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)