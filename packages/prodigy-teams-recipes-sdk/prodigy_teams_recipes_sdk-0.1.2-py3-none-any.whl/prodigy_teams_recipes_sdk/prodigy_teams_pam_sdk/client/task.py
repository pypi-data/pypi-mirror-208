from ..models import (
    TaskCreating,
    TaskDeleting,
    TaskReading,
    TaskReturning,
    TaskUpdating,
)
from .base import ModelClient


class Task(
    ModelClient[
        TaskCreating,
        TaskReading,
        TaskUpdating,
        TaskDeleting,
        TaskReturning,
        TaskReturning,
    ]
):
    Creating = TaskCreating
    Reading = TaskReading
    Updating = TaskUpdating
    Deleting = TaskDeleting
    Returning = TaskReturning
