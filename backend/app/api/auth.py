"""Login for the dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.http import http_error
from app.database import get_session
from app.errors import DomainError
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserRead
from app.services.auth_service import LoginService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)) -> LoginResponse:
    """Check the staff password and return a bearer token.

    The token's subject is the user id. Tenant access is decided later
    by loading that user, not by a tenant id in this body.
    """
    try:
        user, token = LoginService(session).authenticate(body.username, body.password)
    except DomainError as exc:
        raise http_error(exc) from exc
    return LoginResponse(access_token=token, user=UserRead.model_validate(user))
