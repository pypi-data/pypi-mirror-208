from ..models import OrgCreating, OrgDeleting, OrgReading, OrgReturning, OrgUpdating
from .base import ModelClient


class Org(
    ModelClient[
        OrgCreating, OrgReading, OrgUpdating, OrgDeleting, OrgReturning, OrgReturning
    ]
):
    Creating = OrgCreating
    Reading = OrgReading
    Updating = OrgUpdating
    Deleting = OrgDeleting
    Returning = OrgReturning
