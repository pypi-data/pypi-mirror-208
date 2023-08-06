from ..models import (
    PackageCreating,
    PackageDeleting,
    PackageListingLatest,
    PackageReading,
    PackageReadingLatest,
    PackageReturning,
    PackageUpdating,
)
from .base import VersionedModelClient


class Package(
    VersionedModelClient[
        PackageCreating,
        PackageReading,
        PackageUpdating,
        PackageDeleting,
        PackageReturning,
        PackageReturning,
        PackageReadingLatest,
        PackageListingLatest,
    ]
):
    Creating = PackageCreating
    Reading = PackageReading
    Updating = PackageUpdating
    Deleting = PackageDeleting
    Returning = PackageReturning
    Detail = PackageReturning
    ReadingLatest = PackageReadingLatest
    ListingLatest = PackageListingLatest
