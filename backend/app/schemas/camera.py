"""How a camera is shown to API callers."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CameraRead(BaseModel):
    """A truck camera and the one tenant that owns it.

    camera_id is the code the webhook sends. It is not a secret, but
    it is the key that attributes an unauthenticated scan.
    """

    model_config = ConfigDict(from_attributes=True)

    camera_id: str
    tenant_id: int
    created_at: datetime
