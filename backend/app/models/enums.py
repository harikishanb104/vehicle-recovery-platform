"""Status and role values stored in Postgres and returned by the API."""

from enum import StrEnum


class UserRole(StrEnum):
    """What a user may do inside the one tenant they belong to.

    staff and admin both claim cases and read location trails in this
    exercise. The split is stored now so a later permission check has
    a real column to read instead of a string buried in a route.
    """

    STAFF = "staff"
    ADMIN = "admin"


class CaseStatus(StrEnum):
    """Life of a recovery case.

    pending_claim is visible to every tenant and owned by none.
    active is owned by exactly one tenant and one agent.
    closed stays with that tenant and can no longer be claimed.
    """

    PENDING_CLAIM = "pending_claim"
    ACTIVE = "active"
    CLOSED = "closed"
