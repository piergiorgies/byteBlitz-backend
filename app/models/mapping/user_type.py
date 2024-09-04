from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Integer
from typing import List, Optional
from app.database import Base
from . import *

class UserType(Base):
    __tablename__ = 'user_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    permissions: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # connected fields
    users: Mapped[List['User']] = relationship('User', back_populates='user_type')