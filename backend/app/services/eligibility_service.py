"""Mock of the partner network that confirms repossession eligibility."""

from app.errors import PartnerNetworkDown


class EligibilityService:
    """Stand-in for POST /mock/partner-network/eligibility.

    A VIN that ends in 0 is not eligible, so that branch can be shown.
    The VIN 00000000000000000 stands for a network failure. Every other
    VIN is still eligible. Both sample VINs in the case study are eligible.
    """

    FAILURE_VIN = "00000000000000000"

    def still_eligible(self, vin: str) -> bool:
        """Return whether the lender still wants this vehicle recovered.

        Raises PartnerNetworkDown when the stand-in is asked to fail.
        The caller must keep the scan and skip case creation.
        """
        if vin == self.FAILURE_VIN:
            raise PartnerNetworkDown("partner network did not answer")
        return not vin.endswith("0")
