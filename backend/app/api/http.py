"""Map a domain error to the HTTP response the dashboard should show."""

from fastapi import HTTPException

from app.errors import (
    AuthNotConfigured,
    CaseHidden,
    CaseMissing,
    CaseNotPending,
    DomainError,
    InvalidCredentials,
    PartnerNetworkDown,
    UnknownCamera,
)


def http_error(error: DomainError) -> HTTPException:
    """Translate one business failure into a status code and a short detail.

    Unknown errors are not swallowed here. They keep their type so a
    programming mistake is not reported as a user error.
    """
    if isinstance(error, UnknownCamera):
        return HTTPException(status_code=404, detail="Camera is not registered")
    if isinstance(error, InvalidCredentials):
        return HTTPException(status_code=401, detail="Username or password is incorrect")
    if isinstance(error, AuthNotConfigured):
        return HTTPException(status_code=503, detail="Login is not configured")
    if isinstance(error, CaseMissing):
        return HTTPException(status_code=404, detail="Case not found")
    if isinstance(error, CaseHidden):
        return HTTPException(status_code=403, detail="This case belongs to another agency")
    if isinstance(error, CaseNotPending):
        return HTTPException(status_code=409, detail="Case is already claimed or closed")
    if isinstance(error, PartnerNetworkDown):
        return HTTPException(status_code=503, detail="Partner network did not answer")
    raise error
