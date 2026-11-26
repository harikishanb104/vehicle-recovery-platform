"""Checks for a single value before it is stored or accepted.

These classes do not look up tenants, cameras, or cases. They only
decide whether the characters and the range are usable.
"""

import re


class Vin:
    """A 17-character vehicle identification number.

    I, O, and Q are excluded because they are easy to confuse with
    digits on a plate read. The stored form is uppercase so two scans
    of the same vehicle share one key.
    """

    _PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

    @classmethod
    def parse(cls, value: str) -> str:
        """Return the VIN in canonical form, or raise ValueError."""
        cleaned = value.strip().upper()
        if cls._PATTERN.fullmatch(cleaned) is None:
            raise ValueError("vin must be 17 characters and cannot contain I, O, or Q")
        return cleaned


class Plate:
    """A license plate as read by the camera.

    Plates are stored uppercase. The column allows ten characters,
    which covers the sample plates without pretending to know every
    state format.
    """

    _PATTERN = re.compile(r"^[A-Z0-9]{1,10}$")

    @classmethod
    def parse(cls, value: str) -> str:
        """Return the plate in canonical form, or raise ValueError."""
        cleaned = value.strip().upper()
        if cls._PATTERN.fullmatch(cleaned) is None:
            raise ValueError("plate must be 1 to 10 letters or digits")
        return cleaned


class CameraId:
    """The camera code sent by the webhook, such as cam_1001.

    This is the public identifier, not the tenant id. The scan
    endpoint resolves the tenant from it later.
    """

    _PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

    @classmethod
    def parse(cls, value: str) -> str:
        """Return the camera code, or raise ValueError."""
        cleaned = value.strip()
        if cls._PATTERN.fullmatch(cleaned) is None:
            raise ValueError("camera_id must be 1 to 64 letters, digits, underscores, or hyphens")
        return cleaned


class GeoPoint:
    """A latitude and longitude pair inside the real range.

    The database repeats this check. Validating here lets the API
    name the bad field before Postgres rejects the row.
    """

    def __init__(self, latitude: float, longitude: float) -> None:
        """Store a point that already sits inside the valid range."""
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def parse(cls, latitude: float, longitude: float) -> "GeoPoint":
        """Return the point, or raise ValueError when a coordinate is out of range."""
        if latitude < -90 or latitude > 90:
            raise ValueError("latitude must be between -90 and 90")
        if longitude < -180 or longitude > 180:
            raise ValueError("longitude must be between -180 and 180")
        return cls(latitude, longitude)


class ImageUrl:
    """A link to the scan image. We store the link, not the file."""

    _MAX_LENGTH = 2048

    @classmethod
    def parse(cls, value: str) -> str:
        """Return the URL, or raise ValueError when it is not an http(s) link."""
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("image_url must start with http:// or https://")
        if len(cleaned) > cls._MAX_LENGTH:
            raise ValueError("image_url must be 2048 characters or fewer")
        return cleaned
