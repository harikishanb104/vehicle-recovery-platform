"""A truck-mounted camera that belongs to one tenant."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Camera(Base, TimestampMixin):
    """The device that sends a scan.

    A scan arrives with no logged-in user. camera_id is the only way
    to decide which agency the sighting belongs to, so the code is
    unique and required.
    """

    __tablename__ = "cameras"

    camera_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="cameras")
    scans: Mapped[list["Scan"]] = relationship(back_populates="camera")
