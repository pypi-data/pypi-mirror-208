from ..models import (
    InvitationCreating,
    InvitationDeleting,
    InvitationReading,
    InvitationReturning,
    InvitationUpdating,
)
from .base import ModelClient


class Invitation(
    ModelClient[
        InvitationCreating,
        InvitationReading,
        InvitationUpdating,
        InvitationDeleting,
        InvitationReturning,
        InvitationReturning,
    ]
):
    Creating = InvitationCreating
    Reading = InvitationReading
    Updating = InvitationUpdating
    Deleting = InvitationDeleting
    Returning = InvitationReturning
