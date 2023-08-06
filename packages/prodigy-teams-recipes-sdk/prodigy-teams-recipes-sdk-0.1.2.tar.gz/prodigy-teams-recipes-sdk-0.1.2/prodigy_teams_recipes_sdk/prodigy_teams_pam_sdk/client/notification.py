from ..models import (
    NotificationCreating,
    NotificationDeleting,
    NotificationReading,
    NotificationReturning,
    NotificationUpdating,
)
from .base import ModelClient


class Notification(
    ModelClient[
        NotificationCreating,
        NotificationReading,
        NotificationUpdating,
        NotificationDeleting,
        NotificationReturning,
        NotificationReturning,
    ]
):
    Creating = NotificationCreating
    Reading = NotificationReading
    Updating = NotificationUpdating
    Deleting = NotificationDeleting
    Returning = NotificationReturning
