from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base


class Variable(Base):
    __tablename__ = "variable"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    data_type: Mapped[int] = mapped_column(Integer, nullable=False)
    base_type: Mapped[int] = mapped_column(Integer, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    transmission_mode: Mapped[int] = mapped_column(Integer, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), index=True, nullable=False)
    rw_mode: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    description: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    