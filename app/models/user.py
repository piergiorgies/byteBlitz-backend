from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK
from app.database import Base
from datetime import datetime
from typing import List
from app.models import *

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    registered_at: Mapped[datetime] = mapped_column()
    user_type_id: Mapped[str] = mapped_column(FK("user_types.id"))

    # connected field
    user_type: Mapped["UserType"] = relationship("UserType", back_populates="users")
    problems: Mapped[List["Problem"]] = relationship("Problem", back_populates="author")

