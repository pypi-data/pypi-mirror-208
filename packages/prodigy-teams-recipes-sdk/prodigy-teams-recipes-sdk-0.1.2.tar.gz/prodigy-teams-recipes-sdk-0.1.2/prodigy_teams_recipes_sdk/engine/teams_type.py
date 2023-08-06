import dataclasses
import inspect
from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Optional, Set, Type, Union

import catalogue

from ..prodigy_teams_pam_sdk.errors import RecipeProcessingError
from ..prodigy_teams_pam_sdk.recipe_utils import AnyProps, Props
from ..types import Asset, Dataset
from .util import merge_props


class type_registry:
    registry = catalogue.create("type_registry")
    types: Dict[Type, str] = {}

    @classmethod
    def has(cls, item: Union[str, Type]) -> bool:
        """Whether a type or type name is in the registry."""
        if isinstance(item, str):
            return item in cls.registry
        return item in cls.types

    @classmethod
    def get_by_type(cls, type_: Type) -> "_TeamsTypeData":
        """Get the data for a given type."""
        return cls.get(cls.types[type_])

    @classmethod
    def get(cls, name: str) -> "_TeamsTypeData":
        """Get the data for a given type name."""
        return cls.registry.get(name)

    @classmethod
    def set(cls, name: str, data: "_TeamsTypeData") -> None:
        """Register a custom type."""
        cls.registry.register(name, func=data)
        cls.types[data.type] = name


@dataclass
class _TeamsTypeData:
    """Data stored for custom types registered with the @teams_type decorator."""

    type: Type
    type_name: str
    props: AnyProps
    exclude: Set[str] = dataclasses.field(default_factory=set)
    field_props: Dict[str, AnyProps] = dataclasses.field(default_factory=dict)
    fields: Dict[str, dataclasses.Field] = dataclasses.field(default_factory=dict)

    def merge(self, other: "_TeamsTypeData") -> "_TeamsTypeData":
        props = merge_props(self.props, other.props)
        field_props = dict(self.field_props)
        for key, value in other.field_props.items():
            field_props[key] = merge_props(field_props.get(key), value)
        fields = dict(self.fields)
        for key, value in other.fields.items():
            if key not in fields:
                fields[key] = value
        exclude = set(self.exclude)
        exclude.update(other.exclude)
        return _TeamsTypeData(
            type=self.type,
            type_name=self.type_name if self.type_name is not None else other.type_name,
            props=props,
            field_props=field_props,
            fields=fields,
            exclude=exclude,
        )


def is_custom_type(type_: Union[str, Type]) -> bool:
    if isinstance(type_, (Asset, Dataset)):
        return True
    return type_registry.has(type_)


def get_custom_type_name(type_: Type) -> str:
    if not type_registry.has(type_):
        return type_.__name__
    return type_registry.get_by_type(type_).type_name


def get_custom_type(name: str) -> Optional[Type]:
    if type_registry.has(name):
        return type_registry.get(name).type
    return None


def get_custom_type_props(type_: Type) -> AnyProps:
    if type_registry.has(type_):
        return type_registry.get_by_type(type_).props
    else:
        return Props()


def get_custom_type_field_props(type_: Type) -> Dict:
    if type_registry.has(type_):
        return type_registry.get_by_type(type_).field_props
    else:
        return {}


def get_custom_type_fields(type_: Type) -> Dict:
    if type_registry.has(type_):
        data = type_registry.get_by_type(type_)
        return {n: f for n, f in data.fields.items() if n not in data.exclude}
    else:
        return {}


def get_object_type(type_: Union[str, Type]) -> Optional[Literal["asset", "dataset"]]:
    if isinstance(type_, str):
        type_ = get_custom_type(type_)
    if type_ is None:
        return None
    elif not inspect.isclass(type_):
        return None
    elif issubclass(type_, Dataset):
        return "dataset"
    elif issubclass(type_, Asset):
        return "asset"
    else:
        return None


def store_custom_type(
    cls: Type,
    *,
    type_name: Optional[str],
    props: Optional[AnyProps],
    field_props: Dict,
    exclude: Iterable[str],
) -> None:
    """Store a custom type in the type registry."""
    if type_name is None:
        type_name = cls.__name__
    assert type_name is not None
    data = _TeamsTypeData(
        type=cls,
        type_name=type_name,
        props=props if props is not None else Props(),
        field_props=field_props,
        fields={f.name: f for f in dataclasses.fields(cls)},
        exclude=set(exclude),
    )
    if len(data.type.__mro__) >= 2:
        parent = data.type.__mro__[1]
        if type_registry.has(parent):
            data = data.merge(type_registry.get_by_type(parent))
    if type_registry.has(data.type_name):
        raise RecipeProcessingError(
            f"There is an existing type with name '{data.type_name}'. Please choose another type name for the class '{cls.__name__}'."
        )
    type_registry.set(data.type_name, data)
