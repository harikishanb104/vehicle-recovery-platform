"""List, claim, and read the location trail under the tenant rules."""

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.errors import CaseHidden, CaseMissing, CaseNotPending
from app.models import Case, CaseStatus, Scan, User


class CaseService:
    """Case reads and the one cross-tenant write: claiming.

    Visibility is the same for the list and the trail. A pending_claim
    case is visible to every authenticated user. An active or closed
    case is visible only to the tenant that owns it.
    """

    def __init__(self, session: Session) -> None:
        """Bind the use case to the request session."""
        self.session = session

    def list_cases(self, tenant_id: int, status: CaseStatus | None) -> list[Case]:
        """Return this tenant's cases plus every unclaimed case.

        status narrows that set. Asking for active therefore cannot
        include another agency's active rows, because those rows fail
        both the owner check and the pending_claim check.
        """
        visible = or_(Case.tenant_id == tenant_id, Case.status == CaseStatus.PENDING_CLAIM)
        statement = select(Case).where(visible)
        if status is not None:
            statement = statement.where(Case.status == status)
        statement = statement.order_by(Case.created_at.desc(), Case.id.desc())
        return list(self.session.scalars(statement).all())

    def claim(self, case_id: int, user: User) -> Case:
        """Assign a pending case to this user and their tenant.

        The row is locked so two staff members cannot both win. The
        loser finds the case is no longer pending_claim.
        """
        case = self.session.scalar(select(Case).where(Case.id == case_id).with_for_update())
        if case is None:
            raise CaseMissing()
        if case.status != CaseStatus.PENDING_CLAIM:
            raise CaseNotPending()
        case.status = CaseStatus.ACTIVE
        case.tenant_id = user.tenant_id
        case.assigned_user_id = user.id
        case.claimed_at = datetime.now(timezone.utc)
        self.session.flush()
        return case

    def location_trail(self, case_id: int, tenant_id: int) -> tuple[Case, list[Scan]]:
        """Return every stored scan for the case VIN, oldest first.

        The caller must already be allowed to see the case. Scans are
        matched by VIN, including sightings taken before the case existed
        and sightings from another agency's camera.
        """
        case = self._visible_case(case_id, tenant_id)
        scans = list(
            self.session.scalars(
                select(Scan).where(Scan.vin == case.vin).order_by(Scan.scanned_at.asc(), Scan.id.asc())
            ).all()
        )
        return case, scans

    def _visible_case(self, case_id: int, tenant_id: int) -> Case:
        """Load a case the caller may see, or raise CaseMissing or CaseHidden."""
        case = self.session.get(Case, case_id)
        if case is None:
            raise CaseMissing()
        if case.status != CaseStatus.PENDING_CLAIM and case.tenant_id != tenant_id:
            raise CaseHidden()
        return case
