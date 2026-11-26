"""How a recovery case is shown to API callers."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import CaseStatus
from app.schemas.scan import ScanRead


class CaseRead(BaseModel):
    """A case the caller is allowed to see.

    tenant_id is null only while status is pending_claim. The list
    endpoint may include those unowned cases for every tenant, and
    must leave out active or closed cases owned by someone else.
    scanned_by_tenant_id is the agency whose camera opened the case.
    It does not decide who is allowed to claim it.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    vin: str
    status: CaseStatus
    scanned_by_tenant_id: int
    tenant_id: int | None
    assigned_user_id: int | None
    claimed_at: datetime | None
    closed_at: datetime | None
    created_at: datetime


class LocationTrail(BaseModel):
    """The sightings an agent uses to narrow down where a vehicle has been.

    scans are every stored row for this VIN, oldest first. The route
    only builds this after the caller is allowed to see the case.
    """

    case_id: int
    vin: str
    status: CaseStatus
    scans: list[ScanRead]
