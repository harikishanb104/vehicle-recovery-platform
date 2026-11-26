"""A recovery agency using the platform."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """One recovery agency.

    Cameras, staff, and owned cases all belong to a tenant. An agency
    may see its own cases at every status, plus pending cases that no
    agency owns yet. It must not see another agency's active or closed work.
    """

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    cameras: Mapped[list["Camera"]] = relationship(back_populates="tenant")
    owned_cases: Mapped[list["Case"]] = relationship(
        back_populates="owner_tenant",
        foreign_keys="Case.tenant_id",
    )
    scanned_cases: Mapped[list["Case"]] = relationship(
        back_populates="scanned_by_tenant",
        foreign_keys="Case.scanned_by_tenant_id",
    )
