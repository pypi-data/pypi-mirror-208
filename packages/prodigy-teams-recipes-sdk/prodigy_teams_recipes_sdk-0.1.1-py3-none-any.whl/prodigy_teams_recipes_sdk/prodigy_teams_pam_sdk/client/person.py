from .. import ty
from ..models import (
    PersonCreating,
    PersonDeleting,
    PersonReading,
    PersonReturning,
    PersonUpdating,
)
from .base import ModelClient


class Person(
    ModelClient[
        PersonCreating,
        PersonReading,
        PersonUpdating,
        PersonDeleting,
        PersonReturning,
        PersonReturning,
    ]
):
    Creating = PersonCreating
    Reading = PersonReading
    Updating = PersonUpdating
    Deleting = PersonDeleting
    Returning = PersonReturning

    class Authenticating(ty.BaseModel):
        """
        Data describing a Person derived from an identity token provided
        by an authentication provider such as Auth0. Used during signup and login.
        """

        email: str
        name: str
        token: str
