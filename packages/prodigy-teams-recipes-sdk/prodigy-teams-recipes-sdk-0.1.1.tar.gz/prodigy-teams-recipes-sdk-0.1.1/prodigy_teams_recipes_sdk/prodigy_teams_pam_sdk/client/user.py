from ..models import (
    UserCreating,
    UserDeleting,
    UserReading,
    UserReturning,
    UserUpdating,
)
from .base import ModelClient


class User(
    ModelClient[
        UserCreating,
        UserReading,
        UserUpdating,
        UserDeleting,
        UserReturning,
        UserReturning,
    ]
):
    Creating = UserCreating
    Reading = UserReading
    Updating = UserUpdating
    Deleting = UserDeleting
    Returning = UserReturning
