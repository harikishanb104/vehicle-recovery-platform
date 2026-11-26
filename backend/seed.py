"""Load the two-tenant demo from the case study appendix.

Running this again does nothing once Agency A is present, so the
active case and its older scans are not duplicated.
"""

import sys
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import create_schema, get_engine
from app.models import Camera, Case, CaseStatus, Scan, Tenant, User, UserRole
from app.services.auth_service import hash_password

DEMO_PASSWORD = "demo-pass"


def main() -> int:
    """Insert Agency A, Agency B, their cameras, users, and Tenant A's trail."""
    engine = get_engine()
    create_schema(engine)
    with Session(engine) as session:
        existing = session.scalar(select(Tenant).where(Tenant.name == "Agency A"))
        if existing is not None:
            print("seed already applied")
            return 0
        _insert(session)
        session.commit()
    print("seeded Agency A and Agency B")
    return 0


def _insert(session: Session) -> None:
    """Write the demo rows in foreign-key order.

    Tenant A's case is already active and assigned, so a later scan from
    cam_1001 follows the existing-case flow. Tenant B has no case for
    5NPE34AF9KH123456, so a scan from cam_2050 follows the new-case flow.
    """
    agency_a = Tenant(name="Agency A")
    agency_b = Tenant(name="Agency B")
    session.add_all([agency_a, agency_b])
    session.flush()

    password_hash = hash_password(DEMO_PASSWORD)
    agent_a = User(
        tenant_id=agency_a.id,
        username="agent.a",
        password_hash=password_hash,
        role=UserRole.STAFF,
    )
    agent_b = User(
        tenant_id=agency_b.id,
        username="agent.b",
        password_hash=password_hash,
        role=UserRole.STAFF,
    )
    session.add_all([agent_a, agent_b])
    session.add_all(
        [
            Camera(camera_id="cam_1001", tenant_id=agency_a.id),
            Camera(camera_id="cam_2050", tenant_id=agency_b.id),
        ]
    )
    session.flush()

    case = Case(
        vin="1FTFW1E51NFA12345",
        status=CaseStatus.ACTIVE,
        scanned_by_tenant_id=agency_a.id,
        tenant_id=agency_a.id,
        assigned_user_id=agent_a.id,
        claimed_at=_at("2026-09-01T14:32:00+00:00"),
    )
    session.add(case)
    session.flush()

    sightings = [
        ("2026-09-01T14:32:00+00:00", "33.7490", "-84.3880"),
        ("2026-09-02T18:05:00+00:00", "33.7700", "-84.3650"),
        ("2026-09-03T09:15:00+00:00", "33.6890", "-84.4450"),
    ]
    for when, latitude, longitude in sightings:
        session.add(
            Scan(
                camera_id="cam_1001",
                plate="7XYZ123",
                vin=case.vin,
                latitude=latitude,
                longitude=longitude,
                scanned_at=_at(when),
                image_url="https://example.com/scans/history.jpg",
                case_id=case.id,
            )
        )


def _at(value: str) -> datetime:
    """Parse a timezone-aware timestamp from the seed list."""
    return datetime.fromisoformat(value)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"seed failed: {exc.__class__.__name__}", file=sys.stderr)
        raise
