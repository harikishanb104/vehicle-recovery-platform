"""Turn one camera webhook into a stored scan and, when required, a case."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import PartnerNetworkDown, UnknownCamera
from app.models import Camera, Case, CaseStatus, Scan
from app.schemas.scan import ScanDraft
from app.services.eligibility_service import EligibilityService


@dataclass(frozen=True)
class ScanOutcome:
    """The branch taken after a scan was stored.

    existing_case means this tenant already had an active case for the VIN.
    pending_case means eligibility opened a claimable case.
    stored means the sighting was kept and no new case was opened.
    """

    result: str
    scan_id: int
    case_id: int | None = None
    status: CaseStatus | None = None
    eligibility: str | None = None


class ScanIngestor:
    """The two flows from the case study, in one transaction.

    Every accepted scan is inserted before the branch. An unknown camera
    is refused first, because there is no tenant to attach the row to.
    """

    def __init__(self, session: Session, eligibility: EligibilityService | None = None) -> None:
        """Use the request session and the shared eligibility stand-in."""
        self.session = session
        self.eligibility = eligibility or EligibilityService()

    def ingest(self, draft: ScanDraft) -> ScanOutcome:
        """Store the scan, then extend an active case or open a pending one.

        A VIN that already has any open case is not given a second case.
        Only an active case owned by this camera's tenant is linked as
        the existing-case flow. Eligibility failure and a lost race both
        leave the scan in place.
        """
        camera = self.session.get(Camera, draft.camera_id)
        if camera is None:
            raise UnknownCamera()

        scan = Scan(
            camera_id=camera.camera_id,
            plate=draft.plate,
            vin=draft.vin,
            latitude=Decimal(str(draft.latitude)),
            longitude=Decimal(str(draft.longitude)),
            scanned_at=draft.scanned_at,
            image_url=draft.image_url,
        )
        self.session.add(scan)
        self.session.flush()

        active = self.session.scalar(
            select(Case).where(
                Case.vin == draft.vin,
                Case.tenant_id == camera.tenant_id,
                Case.status == CaseStatus.ACTIVE,
            )
        )
        if active is not None:
            scan.case_id = active.id
            self.session.flush()
            return ScanOutcome(
                result="existing_case",
                scan_id=scan.id,
                case_id=active.id,
                status=active.status,
            )

        already_open = self.session.scalar(
            select(Case.id).where(
                Case.vin == draft.vin,
                Case.status != CaseStatus.CLOSED,
            )
        )
        if already_open is not None:
            return ScanOutcome(result="stored", scan_id=scan.id)

        try:
            eligible = self.eligibility.still_eligible(draft.vin)
        except PartnerNetworkDown:
            return ScanOutcome(result="stored", scan_id=scan.id, eligibility="unavailable")
        if not eligible:
            return ScanOutcome(result="stored", scan_id=scan.id, eligibility="not_eligible")

        case = Case(
            vin=draft.vin,
            status=CaseStatus.PENDING_CLAIM,
            scanned_by_tenant_id=camera.tenant_id,
        )
        try:
            with self.session.begin_nested():
                self.session.add(case)
                self.session.flush()
                scan.case_id = case.id
        except IntegrityError:
            return ScanOutcome(result="stored", scan_id=scan.id)

        return ScanOutcome(
            result="pending_case",
            scan_id=scan.id,
            case_id=case.id,
            status=CaseStatus.PENDING_CLAIM,
            eligibility="eligible",
        )
