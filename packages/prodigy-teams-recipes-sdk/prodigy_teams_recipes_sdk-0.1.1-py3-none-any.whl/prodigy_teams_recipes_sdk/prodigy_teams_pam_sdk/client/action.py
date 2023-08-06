from ..models import (
    ActionCreating,
    ActionDeleting,
    ActionReading,
    ActionReturning,
    ActionUpdating,
)
from .base import ModelClient


class Action(
    ModelClient[
        ActionCreating,
        ActionReading,
        ActionUpdating,
        ActionDeleting,
        ActionReturning,
        ActionReturning,
    ]
):
    Creating = ActionCreating
    Reading = ActionReading
    Updating = ActionUpdating
    Deleting = ActionDeleting
    Returning = ActionReturning
