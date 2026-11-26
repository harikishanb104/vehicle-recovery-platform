"""Import every model so Base.metadata knows the full schema.

The order matters only to avoid a circular import. Relationships are
resolved by class name after all of these modules have been imported.
"""

from app.models.base import Base
from app.models.camera import Camera
from app.models.case import Case
from app.models.enums import CaseStatus, UserRole
from app.models.scan import Scan
from app.models.tenant import Tenant
from app.models.user import User

__all__ = [
    "Base",
    "Camera",
    "Case",
    "CaseStatus",
    "Scan",
    "Tenant",
    "User",
    "UserRole",
]
