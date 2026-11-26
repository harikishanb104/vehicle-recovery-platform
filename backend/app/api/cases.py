"""Authenticated case list, claim, and location trail."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.http import http_error
from app.database import get_session
from app.errors import DomainError
from app.models import CaseStatus, User
from app.schemas.case import CaseRead, LocationTrail
from app.schemas.scan import ScanRead
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseRead])
def list_cases(
    status: CaseStatus | None = None,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> list[CaseRead]:
    """List this tenant's cases and every pending_claim case.

    Active and closed cases owned by another tenant are not included.
    status is optional, for example ?status=pending_claim.
    """
    cases = CaseService(session).list_cases(user.tenant_id, status)
    return [CaseRead.model_validate(case) for case in cases]


@router.post("/{case_id}/claim", response_model=CaseRead)
def claim_case(
    case_id: int,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> CaseRead:
    """Claim a pending case for the signed-in user's tenant.

    Any staff user may claim, including a user from a different agency
    than the camera that opened the case. A case that is already active
    or closed is refused.
    """
    try:
        case = CaseService(session).claim(case_id, user)
    except DomainError as exc:
        raise http_error(exc) from exc
    return CaseRead.model_validate(case)


@router.get("/{case_id}/scans", response_model=LocationTrail)
def location_trail(
    case_id: int,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> LocationTrail:
    """Return the VIN's sightings, oldest first, when the caller may see the case.

    Another tenant's active or closed case is refused even if the caller
    knows the case id.
    """
    try:
        case, scans = CaseService(session).location_trail(case_id, user.tenant_id)
    except DomainError as exc:
        raise http_error(exc) from exc
    return LocationTrail(
        case_id=case.id,
        vin=case.vin,
        status=case.status,
        scans=[ScanRead.model_validate(scan) for scan in scans],
    )
