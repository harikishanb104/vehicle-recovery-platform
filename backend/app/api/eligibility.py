"""The mock partner network described in the case study appendix."""

from fastapi import APIRouter

from app.api.http import http_error
from app.errors import DomainError
from app.schemas.eligibility import EligibilityRequest, EligibilityResponse
from app.services.eligibility_service import EligibilityService

router = APIRouter(tags=["eligibility"])


@router.post("/mock/partner-network/eligibility", response_model=EligibilityResponse)
def check_eligibility(body: EligibilityRequest) -> EligibilityResponse:
    """Answer whether a VIN is still eligible for repossession.

    This is the external service the new-case flow calls. The scan
    use case calls EligibilityService directly so a network failure
    can still leave the scan stored. This route is here so the same
    rule can be exercised on its own.
    """
    try:
        eligible = EligibilityService().still_eligible(body.vin)
    except DomainError as exc:
        raise http_error(exc) from exc
    return EligibilityResponse(vin=body.vin, still_eligible_for_repo=eligible)
