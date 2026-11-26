"""How a logged-in user is shown to API callers."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole


class UserRead(BaseModel):
    """The signed-in account, safe to return from a login response.

    password_hash is deliberately absent. The column stays on the
    User model and never crosses this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    username: str
    role: UserRole
    created_at: datetime
