from datetime import UTC, datetime

from sqlalchemy import DateTime, String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db.database import Base


class Resource(Base):
    __tablename__ = "resource"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("resource.id"), index=True, nullable=True, default=None)
    
    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    