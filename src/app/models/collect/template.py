from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db.database import Base


class Template(Base):
    __tablename__ = "template"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    product_model: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    product_model_type: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    connect_num: Mapped[int] = mapped_column(Integer, default=0)
    element_num: Mapped[int] = mapped_column(Integer, default=0)
    
    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    