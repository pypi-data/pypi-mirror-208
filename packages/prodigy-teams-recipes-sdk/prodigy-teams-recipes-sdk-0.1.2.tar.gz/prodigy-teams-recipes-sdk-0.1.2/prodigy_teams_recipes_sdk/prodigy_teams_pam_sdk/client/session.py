from ..models import (
    SessionCreating,
    SessionDeleting,
    SessionReading,
    SessionReturning,
    SessionUpdating,
)
from .base import ModelClient


class Session(
    ModelClient[
        SessionCreating,
        SessionReading,
        SessionUpdating,
        SessionDeleting,
        SessionReturning,
        SessionReturning,
    ]
):
    Creating = SessionCreating
    Reading = SessionReading
    Updating = SessionUpdating
    Deleting = SessionDeleting
    Returning = SessionReturning
