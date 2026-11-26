"""The mock partner-network request and response from the case study."""

from pydantic import BaseModel, field_validator

from app.validation import Vin


class EligibilityRequest(BaseModel):
    """A VIN sent to the stand-in lender network."""

    vin: str

    @field_validator("vin")
    @classmethod
    def check_vin(cls, value: str) -> str:
        """Use the same VIN shape the scan table stores."""
        return Vin.parse(value)


class EligibilityResponse(BaseModel):
    """Whether the vehicle is still eligible for repossession."""

    vin: str
    still_eligible_for_repo: bool
