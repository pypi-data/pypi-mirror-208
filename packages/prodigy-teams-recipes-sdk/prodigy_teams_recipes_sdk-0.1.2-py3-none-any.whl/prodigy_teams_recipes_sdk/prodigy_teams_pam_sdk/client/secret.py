from ..models import (
    SecretCreating,
    SecretDeleting,
    SecretDetail,
    SecretReading,
    SecretReturning,
    SecretUpdating,
)
from .base import ModelClient


class Secret(
    ModelClient[
        SecretCreating,
        SecretReading,
        SecretUpdating,
        SecretDeleting,
        SecretReturning,
        SecretDetail,
    ]
):
    Creating = SecretCreating
    Reading = SecretReading
    Updating = SecretUpdating
    Deleting = SecretDeleting
    Returning = SecretReturning
    Detail = SecretDetail
