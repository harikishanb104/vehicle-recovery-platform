"""Shared SQLAlchemy base for the plate-scan tables."""

from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Stable constraint names so a migration or a reviewer can point at
# fk_scans_camera_id_cameras instead of an anonymous database name.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Registry of every table in this service.

    A model class registers itself here on import. create_schema()
    reads this registry and creates whatever is missing.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """Stores when the row was written, using the database clock.

    Several tables need the same column. The clock lives in Postgres
    so two application servers cannot disagree about the order.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
