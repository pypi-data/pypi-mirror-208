from ..models import (
    GroupAuthorizing,
    GroupCreating,
    GroupDeleting,
    GroupPopulating,
    GroupReading,
    GroupReturning,
    GroupUpdating,
)
from .base import ModelClient


class Group(
    ModelClient[
        GroupCreating,
        GroupReading,
        GroupUpdating,
        GroupDeleting,
        GroupReturning,
        GroupReturning,
    ]
):
    Creating = GroupCreating
    Reading = GroupReading
    Updating = GroupUpdating
    Deleting = GroupDeleting
    Returning = GroupReturning
    Populating = GroupPopulating
    Authorizing = GroupAuthorizing
