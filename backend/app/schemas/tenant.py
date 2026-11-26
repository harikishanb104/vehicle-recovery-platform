"""How a tenant is shown to API callers."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TenantRead(BaseModel):
    """A recovery agency, without its cameras, users, or cases.

    Those collections are loaded by their own endpoints so a tenant
    response cannot leak another agency's rows by accident.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
