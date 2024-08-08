from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey as FK
from datetime import datetime
from app.models import *


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    memory_limit: Mapped[int] = mapped_column()
    time_limit: Mapped[int] = mapped_column()
    points: Mapped[int] = mapped_column()
    is_public: Mapped[bool] = mapped_column()
    config_version_number: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    author_id: Mapped[str] = mapped_column("creator_id", FK("users.id"))

    # connected field
    author: Mapped["User"] = relationship("User", back_populates="problems")