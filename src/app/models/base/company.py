from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.db.database import Base
from ..permission.resource import company_resource
from ..user import User
from ..permission.role import Role


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    users: Mapped[list["User"]] = relationship("User", back_populates="company", foreign_keys=[User.company_id], init=False)
    roles: Mapped[list["Role"]] = relationship("Role", back_populates="company", foreign_keys=[Role.company_id], init=False)
    is_end_user: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("company.id"), index=True, nullable=True, default=None)
    province: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    city: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    area: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    address: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    email: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    resources: Mapped[list["Resource"]] = relationship(
        "Resource",
        secondary=company_resource,
        back_populates="companies",
        lazy="selectin",
        default_factory=list
    )
    smart_hardwares = relationship("SmartHardware", back_populates="company")

    update_user: Mapped[int | None] = mapped_column(ForeignKey("user.id"), index=True, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    