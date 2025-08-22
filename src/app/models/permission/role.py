from datetime import UTC, datetime

from sqlalchemy import DateTime, String, ForeignKey, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db.database import Base
from .resource import role_resource


user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), index=True, nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="roles", init=False)
    public_type: Mapped[int] = mapped_column(Integer, nullable=False)
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_role,
        back_populates="roles",
        lazy="noload",
        default_factory=list
    )
    resources: Mapped[list["Resource"]] = relationship(
        "Resource",
        secondary=role_resource,
        back_populates="roles",
        lazy="selectin",
        default_factory=list
    )
    description: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    
    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)

