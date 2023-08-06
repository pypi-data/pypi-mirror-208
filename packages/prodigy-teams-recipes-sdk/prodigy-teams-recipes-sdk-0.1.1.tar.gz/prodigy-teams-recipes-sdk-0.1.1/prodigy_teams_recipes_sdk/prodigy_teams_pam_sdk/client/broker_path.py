from ..models import (
    BrokerPathCreating,
    BrokerPathDeleting,
    BrokerPathReading,
    BrokerPathReturning,
    BrokerPathUpdating,
)
from .base import ModelClient


class BrokerPath(
    ModelClient[
        BrokerPathCreating,
        BrokerPathReading,
        BrokerPathUpdating,
        BrokerPathDeleting,
        BrokerPathReturning,
        BrokerPathReturning,
    ]
):
    Creating = BrokerPathCreating
    Reading = BrokerPathReading
    Updating = BrokerPathUpdating
    Deleting = BrokerPathDeleting
    Returning = BrokerPathReturning
