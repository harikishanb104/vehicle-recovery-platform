"""A VIN being tracked for recovery."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import CaseStatus


class Case(Base, TimestampMixin):
    """One open recovery effort for a VIN.

    scanned_by_tenant_id records which agency's camera caused the case
    to be opened. That is history, not ownership. tenant_id and
    assigned_user_id stay empty while the case is pending_claim, because
    any agency's staff may claim it. After a claim they point at exactly
    one tenant and one agent.

    A closed case keeps its owner. A second open case for the same VIN
    is rejected: the vehicle can be assigned to only one agency at a time.
    The agent who claims a case must belong to the tenant that receives it.
    The database cannot check that across two rows; the claim use case will.
    """

    __tablename__ = "cases"
    __table_args__ = (
        CheckConstraint(
            "("
            "status::text = 'pending_claim' "
            "AND tenant_id IS NULL "
            "AND assigned_user_id IS NULL"
            ") OR ("
            "status::text = 'active' "
            "AND tenant_id IS NOT NULL "
            "AND assigned_user_id IS NOT NULL"
            ") OR ("
            "status::text = 'closed' "
            "AND tenant_id IS NOT NULL"
            ")",
            name="owner_matches_status",
        ),
        Index(
            "uq_cases_one_open_vin",
            "vin",
            unique=True,
            postgresql_where=text("status <> 'closed'::case_status"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(17), nullable=False, index=True)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(
            CaseStatus,
            name="case_status",
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        index=True,
    )
    scanned_by_tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        index=True,
    )
    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    scanned_by_tenant: Mapped["Tenant"] = relationship(
        back_populates="scanned_cases",
        foreign_keys=[scanned_by_tenant_id],
    )
    owner_tenant: Mapped["Tenant | None"] = relationship(
        back_populates="owned_cases",
        foreign_keys=[tenant_id],
    )
    assigned_user: Mapped["User | None"] = relationship(back_populates="assigned_cases")
    scans: Mapped[list["Scan"]] = relationship(back_populates="case")
