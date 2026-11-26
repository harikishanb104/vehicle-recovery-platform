"""Business failures. Routes turn these into HTTP responses.

Services raise these and do not import FastAPI, so the same rule can
be reused by a script or a test without dragging the web framework in.
"""


class DomainError(Exception):
    """A use case stopped because a business rule was not met."""


class UnknownCamera(DomainError):
    """The webhook named a camera this platform does not know.

    Without a camera row there is no tenant, so the scan is rejected
    before anything is stored.
    """


class InvalidCredentials(DomainError):
    """The username and password do not match a staff account.

    The message stays the same for an unknown user and a wrong password
    so the login route does not reveal which accounts exist.
    """


class AuthNotConfigured(DomainError):
    """JWT_SECRET is empty, so a login token cannot be signed."""


class CaseMissing(DomainError):
    """No case has the requested id."""


class CaseHidden(DomainError):
    """The case exists, but this tenant is not allowed to see it.

    Active and closed cases stay with their owner. pending_claim is the
    only status another agency may open.
    """


class CaseNotPending(DomainError):
    """A claim arrived for a case that is already active or closed.

    The second caller, including one that lost a row lock, gets this
    rather than a second owner.
    """


class PartnerNetworkDown(DomainError):
    """The mock lender network did not answer.

    The scan is still stored. No case is created without a yes.
    """
