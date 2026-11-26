"""The logged-in user for dashboard routes.

The scan webhook does not use this. It has no token; the camera id
is resolved inside the scan use case.
"""

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import JWT_SECRET
from app.database import get_session
from app.models import User

_bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    """Load the staff user named by the bearer token.

    A missing, expired, or unknown token is a 401. The tenant id used
    by later queries comes from this row, not from the request body.
    """
    if credentials is None or not JWT_SECRET:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Login required") from exc
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Login required")
    return user
