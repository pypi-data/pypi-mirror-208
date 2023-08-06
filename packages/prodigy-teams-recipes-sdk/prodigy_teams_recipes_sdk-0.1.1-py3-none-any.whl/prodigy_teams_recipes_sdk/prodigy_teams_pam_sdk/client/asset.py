from ..models import (
    AssetCreating,
    AssetDeleting,
    AssetDetail,
    AssetListingLatest,
    AssetReading,
    AssetReadingLatest,
    AssetReturning,
    AssetUpdating,
)
from .base import VersionedModelClient


class Asset(
    VersionedModelClient[
        AssetCreating,
        AssetReading,
        AssetUpdating,
        AssetDeleting,
        AssetReturning,
        AssetDetail,
        AssetReadingLatest,
        AssetListingLatest,
    ]
):
    Creating = AssetCreating
    Reading = AssetReading
    Updating = AssetUpdating
    Deleting = AssetDeleting
    Returning = AssetReturning
    Detail = AssetDetail
    ReadingLatest = AssetReadingLatest
    ListingLatest = AssetListingLatest
