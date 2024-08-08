from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from app.database import Base
from app.models import *

class UserType(Base):
    __tablename__ = "user_types"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    permissions: Mapped[str] = mapped_column()
    
    # connected field
    users: Mapped[List["User"]] = relationship("User", back_populates="user_type")