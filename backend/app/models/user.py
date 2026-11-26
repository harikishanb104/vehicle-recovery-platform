"""A staff account that belongs to exactly one tenant."""

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import UserRole


class User(Base, TimestampMixin):
    """A person who logs in and works for one recovery agency.

    The password hash stays in this table and out of every API schema.
    Role is staff or admin. This exercise treats both as allowed to
    claim a pending case and to read their tenant's cases.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda roles: [role.value for role in roles]),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    assigned_cases: Mapped[list["Case"]] = relationship(back_populates="assigned_user")
