"""Username and password login that issues a short-lived JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, TOKEN_HOURS
from app.errors import AuthNotConfigured, InvalidCredentials
from app.models import User


def hash_password(plain: str) -> str:
    """Hash a password for the users table.

    The plain text is never stored. Seed data and a future password
    change both go through this function so the algorithm stays in one place.
    """
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    """Return whether the plain password matches the stored hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))


class LoginService:
    """Check a staff login and sign a token that carries only the user id.

    The tenant id is not trusted from the token body. Callers load the
    user row and read tenant_id from the database.
    """

    def __init__(self, session: Session) -> None:
        """Bind the login check to the request session."""
        self.session = session

    def authenticate(self, username: str, password: str) -> tuple[User, str]:
        """Return the user and a bearer token, or raise InvalidCredentials."""
        if not JWT_SECRET:
            raise AuthNotConfigured()
        user = self.session.scalar(select(User).where(User.username == username.strip()))
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentials()
        return user, self._token(user.id)

    def _token(self, user_id: int) -> str:
        """Sign a token whose subject is the user id."""
        expires = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)
        return jwt.encode({"sub": str(user_id), "exp": expires}, JWT_SECRET, algorithm="HS256")
