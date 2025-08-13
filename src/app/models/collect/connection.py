from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base


class Connection(Base):
    __tablename__ = "connection"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("template.id"), index=True, nullable=False)
    plc_type_id: Mapped[int] = mapped_column(ForeignKey("plc_type.id"), index=True, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    station_number: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    
    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    