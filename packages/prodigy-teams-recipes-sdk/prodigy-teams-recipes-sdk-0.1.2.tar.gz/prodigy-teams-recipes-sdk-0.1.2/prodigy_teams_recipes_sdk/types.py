from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Generic, TypeVar
from uuid import UUID

from cloudpathlib import AnyPath

_KindT = TypeVar("_KindT", bound=str)


@dataclass
class Asset(Generic[_KindT]):
    """Custom type for an asset uploaded to the cluster."""

    id: UUID
    broker_id: UUID
    name: str
    version: str
    kind: ClassVar[str] = ""
    path: str
    meta: Dict[str, Any]

    def load(self, *args: Any, **kwargs: Any) -> AnyPath:
        raise NotImplementedError  # shouldn't happen


@dataclass
class Dataset(Generic[_KindT]):
    """Custom type for a Prodigy dataset on the cluster."""

    id: UUID
    name: str
    broker_id: UUID
    kind: ClassVar[str] = ""

    def load(self, *args: Any, **kwargs: Any) -> AnyPath:
        raise NotImplementedError  # shouldn't happen
