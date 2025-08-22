from datetime import UTC, datetime

from sqlalchemy import DateTime, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db.database import Base


company_resource= Table(
    "company_resource",
    Base.metadata,
    Column("company_id", ForeignKey("company.id"), primary_key=True),
    Column("resource_id", ForeignKey("resource.id"), primary_key=True),
)


role_resource = Table(
    "role_resource",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), primary_key=True),
    Column("resource_id", ForeignKey("resource.id"), primary_key=True),
)


class Resource(Base):
    __tablename__ = "resource"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("resource.id"), index=True, nullable=True, default=None)
    companies: Mapped[list["Company"]] = relationship(
        "Company",
        secondary=company_resource,
        back_populates="resources",
        lazy="selectin",
        default_factory=list
    )
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_resource,
        back_populates="resources",
        lazy="selectin",
        default_factory=list
    )
    
    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
