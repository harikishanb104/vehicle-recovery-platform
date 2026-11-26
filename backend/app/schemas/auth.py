"""Login request and the token returned to the dashboard."""

from pydantic import BaseModel

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    """Username and password for a seeded staff account.

    The body has no tenant id. The tenant is read from the user row
    after the password matches.
    """

    username: str
    password: str


class LoginResponse(BaseModel):
    """A bearer token plus the signed-in user, without the password hash."""

    access_token: str
    token_type: str = "bearer"
    user: UserRead
