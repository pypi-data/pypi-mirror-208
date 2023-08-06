import dataclasses
import inspect
import types
from enum import Enum
from typing import (
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

from ..prodigy_teams_pam_sdk.models import TypeSchema
from ..prodigy_teams_pam_sdk.recipe_utils import (
    SIMPLE_TYPES,
    SIMPLE_TYPES_BY_NAME,
    AnyProps,
    Field,
    Props,
    RecipeSchema,
    slugify_name,
)
from ..types import Asset, Dataset
from .teams_type import (
    get_custom_type_field_props,
    get_custom_type_fields,
    get_custom_type_name,
    get_custom_type_props,
    get_object_type,
    is_custom_type,
)
from .util import merge_props


def make_schema(
    func: Callable,
    *,
    name: Optional[str],  # the recipe name
    title: Optional[str],  # optional display title
    description: Optional[str],  # optional display description
    view_id: Optional[str],  # Prodigy UI for display purposes only
    field_props: Dict[str, AnyProps],  # UI form fields defined in the decorator
    cli_names: Dict[str, str],  # mapping of fields to custom CLI argument names
) -> RecipeSchema:
    """Generate a recipe schema from a recipe function and meta data."""
    ds_title, ds_desc = _parse_docstring(func.__doc__)
    params = inspect.signature(func).parameters
    schema = RecipeSchema(
        name=func.__name__,
        title=ds_title,
        description=ds_desc,
        view_id=view_id,
        fields=[field_schema_from_param(param) for param in params.values()],
        cli_names=cli_names,
    )
    schema.name = name if name is not None else schema.name
    schema.title = title if title is not None else schema.title
    schema.description = description if description is not None else schema.description
    # Add recipe-defined props for form fields to auto-generated fields
    for name, props in field_props.items():
        _update_field_props(schema, name, props)
    return schema


def field_schema_from_param(param: inspect.Parameter) -> Field:
    """Generate a form field schema from a function parameter."""
    positional = param.kind == param.POSITIONAL_OR_KEYWORD
    return field_schema_from_type(
        param.name,
        param.annotation,
        Props(required=True, positional=positional)
        if param.default is param.empty
        else Props(value=param.default, positional=positional),
    )


def field_schema_from_dc_field(
    name: str, field: dataclasses.Field, props: AnyProps
) -> Field:
    """Generate a form field schema from a dataclass field."""
    new_props = (
        Props(required=True)
        if field.default is dataclasses.MISSING
        else Props(value=field.default)
    )
    output = field_schema_from_type(name, field.type, merge_props(props, new_props))
    return output


def field_schema_from_type(name: str, type_: Type, props: Props) -> Field:
    """Generate a form field schema for a given type hint."""
    type_name = _get_type_name(type_)
    props = _update_props_from_registry(type_, props)
    if type_name in SIMPLE_TYPES_BY_NAME:
        assert not isinstance(type_, str)
        return _make_simple_field(name, type_, props)
    elif type_name == "union":
        return _make_union_field(name, type_, props)
    elif type_name == "enum":
        return _make_enum_field(name, type_, props)
    elif type_name == "optional":
        return _make_optional_field(name, type_, props)
    elif type_name == "literal":
        return _make_literal_field(name, type_, props)
    elif type_name == "list":
        return _make_list_field(name, type_, props)
    elif type_name == "asset":
        return _make_asset_field(name, type_, props)
    elif type_name == "dataset":
        return _make_dataset_field(name, type_, props)
    elif is_custom_type(type_):
        return _make_custom_type_field(name, type_, props)
    else:
        raise NotImplementedError


def _update_props_from_registry(type_: Type, props: AnyProps) -> Props:
    if is_custom_type(type_):
        return merge_props(props, get_custom_type_props(type_))
    else:
        return props


def _make_simple_field(name: str, type_: Type, props: AnyProps) -> Field:
    return Field(
        name=name, type=_make_type_schema(type_), props=props, fields=[], choice=[]
    )


def _make_custom_type_field(name: str, type_: Type, props: AnyProps) -> Field:
    custom_props = get_custom_type_props(type_)
    custom_fields = get_custom_type_fields(type_)
    field_props = get_custom_type_field_props(type_)
    return Field(
        name=name,
        type=_make_type_schema(type_),
        props=merge_props(props, custom_props),
        fields=[
            field_schema_from_dc_field(f"{name}.{n}", f, field_props.get(n, None))
            for n, f in custom_fields.items()
        ],
        choice=[],
    )


def _make_union_field(name: str, type_: Type, props: AnyProps) -> Field:
    _, type_args = _parse_type(type_)
    field_props = props.copy()
    field_props.positional = False
    return Field(
        name=name,
        type=_make_type_schema(type_),
        props=field_props,
        fields=[],
        choice=[
            field_schema_from_type(f"{name}-{_get_type_name(t)}", t, Props())
            for t in type_args
        ],
    )


def _make_enum_field(name: str, type_: Type[Enum], props: AnyProps) -> Field:
    field_props = get_custom_type_field_props(type_)
    field_choice_props = props.choice or {}
    choices = []
    for option in type_:
        if issubclass(type_, Enum):
            choice_props = Props(value=option.value)
        else:
            choice_props = Props()
        opt_props = merge_props(choice_props, field_props.get(option.name, Props()))
        opt_props = merge_props(opt_props, field_choice_props.get(option.name, Props()))
        choices.append(
            Field(
                name=option.name,
                type=TypeSchema(name="enum", args=None, object_type=None),
                fields=[],
                choice=[],
                props=opt_props,
            )
        )
    return Field(
        name=name, type=_make_type_schema(type_), props=props, fields=[], choice=choices
    )


def _make_optional_field(name: str, type_: Type, props: AnyProps) -> Field:
    _, type_args = _parse_type(type_)
    assert len(type_args) == 1
    new_props = Props()
    if is_custom_type(type_args[0]):
        # If a custom type is optional and defines an optional title, use that
        item_props = get_custom_type_props(type_args[0])
        new_props.optional_title = item_props.optional_title
    return Field(
        name=name,
        type=_make_type_schema(type_),
        props=props,
        fields=[],
        choice=[field_schema_from_type(name, type_args[0], new_props)],
    )


def _make_literal_field(name: str, type_: Type, props: AnyProps) -> Field:
    return Field(
        name=name, type=_make_type_schema(type_), props=props, fields=[], choice=[]
    )


def _make_list_field(name: str, type_: Type, props: AnyProps) -> Field:
    return Field(
        name=name, type=_make_type_schema(type_), props=props, fields=[], choice=[]
    )


def _make_asset_field(name: str, type_: Type, props: AnyProps) -> Field:
    return Field(
        name=name, type=_make_type_schema(type_), props=props, fields=[], choice=[]
    )


def _make_dataset_field(name: str, type_: Type, props: AnyProps) -> Field:
    return Field(
        name=name, type=_make_type_schema(type_), props=props, fields=[], choice=[]
    )


def _make_type_schema(annot: Type) -> TypeSchema:
    type_, args = _parse_type(annot)
    type_name = _get_type_name(type_)
    object_type = get_object_type(type_)
    arg_schemas = []
    for arg in args:
        if isinstance(arg, str):
            arg_schemas.append(arg)
        else:
            arg_schemas.append(_make_type_schema(arg))
    if type_name in SIMPLE_TYPES_BY_NAME:
        assert not args
        return TypeSchema(name=type_name, args=None, object_type=object_type)
    elif type_name in ("union", "optional", "enum"):
        return TypeSchema(name=type_name, args=None, object_type=object_type)
    elif object_type is not None and type_.kind:
        return TypeSchema(name=type_name, args=[type_.kind], object_type=object_type)
    elif object_type is not None and arg_schemas:
        return TypeSchema(
            name=type_name, args=arg_schemas[0].args, object_type=object_type
        )
    elif object_type is not None:
        return TypeSchema(name=type_name, args=[], object_type=object_type)
    else:
        return TypeSchema(name=type_name, args=arg_schemas, object_type=None)


def _get_type_name(type_: Type) -> str:
    type_, _ = _parse_type(type_)
    origin = get_origin(type_)
    if type_ in SIMPLE_TYPES:
        return SIMPLE_TYPES[type_]
    elif _is_literal(type_, origin):
        return "literal"
    elif _is_list(type_, origin):
        return "list"
    elif _is_optional(type_, origin):
        return "optional"
    elif _is_union(type_, origin):
        return "union"
    elif _is_enum(type_, origin):
        return "enum"
    elif is_custom_type(type_):
        return get_custom_type_name(type_)
    elif _is_asset(type_, origin):
        return "asset"
    elif _is_dataset(type_, origin):
        return "dataset"
    else:
        raise NotImplementedError


def _is_literal(type_: Type, origin: Type) -> bool:
    return type_ == Literal or origin == Literal


def _is_list(type_: Type, origin: Type) -> bool:
    return type_ in (list, List) or origin in (List, list)


def _is_union(type_: Type, origin: Type) -> bool:
    return type_ == Union or origin == Union


def _is_enum(type_: Type, origin: Type) -> bool:
    if isinstance(type_, str):
        return type_.lower() == "enum"
    elif inspect.isclass(type_) and issubclass(type_, Enum):
        return True
    else:
        return False


def _is_optional(type_: Type, origin: Type) -> bool:
    return type_ == Optional or origin == Optional


def _is_asset(type_: Type, origin: Type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, Asset)


def _is_dataset(type_: Type, origin: Type) -> bool:
    return inspect.isclass(type_) and issubclass(type_, Dataset)


def _parse_type(annot: Type) -> Tuple[Type, List[Union[str, Type]]]:
    args = list(get_args(annot))
    origin = get_origin(annot)
    if origin is None:
        return (annot, args)
    elif origin == Union and type(None) in args:
        # An Optional is just a Union with a None in it, but
        # we want to handle them specially. So we need to
        # undo this transformation, going from
        # e.g. Union[str, None] -> Optional[str]
        # or Union[str, int, None] -> Optional[Union[str, int]]
        type_args = [t for t in args if t is not type(None)]  # noqa
        if len(type_args) == 1:
            return (Optional, type_args)
        else:
            return (Optional, [types.GenericAlias(Union, tuple(type_args))])
    else:
        return (origin, list(args))


def _update_field_props(schema: RecipeSchema, name: str, props: AnyProps) -> None:
    for field in schema.fields:
        if field.name == slugify_name(name):
            field.props = merge_props(props, field.props)


def _parse_docstring(doc: Optional[str]) -> Tuple[str, str]:
    if doc is None:
        return "", ""
    doc = doc.strip()
    if "\n" in doc:
        return tuple(doc.split("\n", 1))
    else:
        return doc, ""
