import uuid
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    # pylint: disable=not-callable
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    boards: Mapped[list["Board"]] = relationship("Board", back_populates="owner")