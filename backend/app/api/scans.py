"""Camera webhook. This router does not require a logged-in user."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.http import http_error
from app.database import get_session
from app.errors import DomainError
from app.schemas.scan import ScanDraft, ScanIngestResult
from app.services.scan_service import ScanIngestor

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("", response_model=ScanIngestResult, status_code=201)
def ingest_scan(draft: ScanDraft, session: Session = Depends(get_session)) -> ScanIngestResult:
    """Store a sighting and run the existing-case or new-case branch.

    The tenant is taken from camera_id. A scan that passes validation
    is stored even when eligibility says no, or when the partner
    network does not answer.
    """
    try:
        outcome = ScanIngestor(session).ingest(draft)
    except DomainError as exc:
        raise http_error(exc) from exc
    return ScanIngestResult(
        result=outcome.result,
        scan_id=outcome.scan_id,
        case_id=outcome.case_id,
        status=outcome.status,
        eligibility=outcome.eligibility,
    )
