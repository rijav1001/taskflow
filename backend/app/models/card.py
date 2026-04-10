import uuid
from sqlalchemy import String, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    list_id: Mapped[str] = mapped_column(String, ForeignKey("lists.id"), nullable=False)
    order: Mapped[float] = mapped_column(Float, nullable=False)
    # pylint: disable=not-callable
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    list: Mapped["List"] = relationship("List", back_populates="cards")