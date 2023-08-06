from ..models import (
    DatasetCreating,
    DatasetDeleting,
    DatasetDetail,
    DatasetReading,
    DatasetReturning,
    DatasetUpdating,
)
from .base import ModelClient


class Dataset(
    ModelClient[
        DatasetCreating,
        DatasetReading,
        DatasetUpdating,
        DatasetDeleting,
        DatasetReturning,
        DatasetDetail,
    ]
):
    Creating = DatasetCreating
    Reading = DatasetReading
    Updating = DatasetUpdating
    Deleting = DatasetDeleting
    Returning = DatasetReturning
    Detail = DatasetDetail
