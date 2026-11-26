"""Scan payload in, and a stored sighting out."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.enums import CaseStatus

from app.validation import CameraId, GeoPoint, ImageUrl, Plate, Vin


class ScanDraft(BaseModel):
    """The camera webhook body, checked before a row is inserted.

    This does not decide which case the scan belongs to. That decision
    needs the database. The model only rejects a payload we could not
    store safely.
    """

    camera_id: str
    plate: str
    vin: str
    latitude: float
    longitude: float
    scanned_at: datetime
    image_url: str

    @field_validator("camera_id")
    @classmethod
    def check_camera_id(cls, value: str) -> str:
        """Keep the camera code inside the column limit."""
        return CameraId.parse(value)

    @field_validator("plate")
    @classmethod
    def check_plate(cls, value: str) -> str:
        """Store the plate in uppercase so later matches do not depend on case."""
        return Plate.parse(value)

    @field_validator("vin")
    @classmethod
    def check_vin(cls, value: str) -> str:
        """Store the VIN in the same form the case table uses."""
        return Vin.parse(value)

    @field_validator("scanned_at")
    @classmethod
    def check_scanned_at(cls, value: datetime) -> datetime:
        """Require a timezone so the location trail sorts the same on every server."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scanned_at must include a timezone")
        return value

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, value: str) -> str:
        """Accept a link to the image. The file itself is out of scope."""
        return ImageUrl.parse(value)

    @model_validator(mode="after")
    def check_point(self) -> "ScanDraft":
        """Reject a coordinate pair the database would also reject.

        Each field is validated on its own first. Latitude and longitude
        are a pair, so the range check runs only after both are present.
        """
        GeoPoint.parse(self.latitude, self.longitude)
        return self


class ScanIngestResult(BaseModel):
    """What the camera webhook receives after the sighting is stored.

    existing_case means this tenant already tracked the VIN.
    pending_case means a claimable case was opened.
    stored means the sighting was kept and no new case was opened.
    """

    result: Literal["existing_case", "pending_case", "stored"]
    scan_id: int
    case_id: int | None = None
    status: CaseStatus | None = None
    eligibility: Literal["eligible", "not_eligible", "unavailable"] | None = None


class ScanRead(BaseModel):
    """One stored sighting on a case's location trail.

    The trail is ordered by scanned_at, which is when the camera saw
    the vehicle, not when this API saved the row.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    camera_id: str
    plate: str
    vin: str
    latitude: float
    longitude: float
    scanned_at: datetime
    image_url: str
    case_id: int | None
    created_at: datetime
