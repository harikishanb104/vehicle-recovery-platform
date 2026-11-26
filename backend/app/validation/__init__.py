"""Value rules that do not touch the database."""

from app.validation.fields import CameraId, GeoPoint, ImageUrl, Plate, Vin

__all__ = [
    "CameraId",
    "GeoPoint",
    "ImageUrl",
    "Plate",
    "Vin",
]
