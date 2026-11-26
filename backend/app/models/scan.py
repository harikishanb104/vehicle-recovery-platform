"""One plate sighting from a truck camera."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Scan(Base, TimestampMixin):
    """A single sighting. Every scan is stored, match or not.

    camera_id attributes the row to a tenant, because the webhook is
    not authenticated. case_id is set when this sighting is already
    known to belong to a case. The location trail does not depend on
    that link: it lists every stored scan for the case VIN, ordered
    by scanned_at, including sightings taken before the case existed.

    created_at is when our API stored the row. scanned_at is when the
    camera saw the vehicle, and that is the time the trail sorts on.
    """

    __tablename__ = "scans"
    __table_args__ = (
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="latitude_range",
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="longitude_range",
        ),
        Index("ix_scans_vin_scanned_at", "vin", "scanned_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[str] = mapped_column(
        ForeignKey("cameras.camera_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    plate: Mapped[str] = mapped_column(String(10), nullable=False)
    vin: Mapped[str] = mapped_column(String(17), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("cases.id", ondelete="RESTRICT"),
        index=True,
    )

    camera: Mapped["Camera"] = relationship(back_populates="scans")
    case: Mapped["Case | None"] = relationship(back_populates="scans")
