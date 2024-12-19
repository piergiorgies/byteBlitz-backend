from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK, Integer
from app.database import Base
from . import *

class ContestUser(Base):
    __tablename__ = 'contest_users'

    contest_id : Mapped[int] = mapped_column(Integer, FK('contests.id', ondelete='cascade'), nullable=False, primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, FK('users.id', ondelete='cascade'), nullable=False, primary_key=True)
    score : Mapped[int] = mapped_column(Integer, nullable=False, default=0)
