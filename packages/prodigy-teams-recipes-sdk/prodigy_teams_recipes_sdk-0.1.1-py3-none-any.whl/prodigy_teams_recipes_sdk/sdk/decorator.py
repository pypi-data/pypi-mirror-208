from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set, Type, TypeVar

from ..engine import registry
from ..engine.recipe import Recipe
from ..engine.teams_type import store_custom_type
from ..prodigy_teams_pam_sdk.recipe_utils import Props

_CallableT = TypeVar("_CallableT", bound=Callable)
_T = TypeVar("_T", bound=Type)


def teams_recipe(
    *,
    name: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    # The view_id is currently only used in the UI to show visual previews, since
    # we don't otherwise have access to that before we start the recipe.
    view_id: Optional[str] = None,
    field_props: Dict[str, Props] = {},
    is_action: bool = False,
    cli_names: Optional[Dict[str, str]] = None,
    module_name: Optional[str] = None,
) -> Callable[[_CallableT], _CallableT]:
    """
    Register a Prodigy Teams recipe. Usually used as a decorator. The decorator
    constructs a Recipe object and stores it in a global variable within the
    registry module, and then returns the original function object unchanged.

    name (str): The recipe name.
    title (str): Display title of the recipe.
    description (str): Display description of the recipe.
    view_id (str): Prodigy UI ID to show in recipe preview in Prodigy Teams.
    field_props (Dict[str, Props]): Form field props for the UI, keyed by argument.
    is_action (bool): Whether the recipe is an action. If False, it starts the
        Prodigy server for annotation.
    cli_names (Dict[str, str]): Mapping of nested field names to nicer
        human-readable CLI argument names.
    module_name (Optional[str]): If specified, overrides the module path used
        to register the recipe. Defaults to the `__package__` of the function.
    """

    def teams_recipe_decorator(recipe_func: _CallableT) -> _CallableT:
        recipe = Recipe.from_decorator(
            recipe_func,
            name=name,
            title=title,
            description=description,
            view_id=view_id,
            field_props=field_props,
            is_action=is_action,
            cli_names=cli_names or {},
        )
        mod_name = module_name or recipe_func.__globals__["__package__"]
        registry.set(mod_name, recipe.name, recipe)
        return recipe_func

    return teams_recipe_decorator


def task_recipe(
    *,
    name: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    view_id: Optional[str] = None,
    field_props: Dict[str, Props] = {},
    cli_names: Dict[str, str] = {},
    module_name: Optional[str] = None,
) -> Callable[[_CallableT], _CallableT]:
    """
    Register a Prodigy Teams recipe that returns a dictionary of components
    for the annotation server. Usually used as a decorator.

    name (str): The recipe name.
    title (str): Display title of the recipe.
    description (str): Display description of the recipe.
    view_id (str): Prodigy UI ID to show in recipe preview in Prodigy Teams.
    field_props (Dict[str, Props]): Form field props for the UI, keyed by argument.
    cli_names (Dict[str, str]): Mapping of nested field names to nicer
        human-readable CLI argument names.
    module_name (Optional[str]): If specified, overrides the module path used
        to register the recipe. Defaults to the `__package__` of the function.
    """
    return teams_recipe(
        name=name,
        title=title,
        description=description,
        view_id=view_id,
        field_props=field_props,
        is_action=False,
        cli_names=cli_names,
        module_name=module_name,
    )


def action_recipe(
    *,
    name: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    view_id: Optional[str] = None,
    field_props: Dict[str, Props] = {},
    cli_names: Dict[str, str] = {},
    module_name: Optional[str] = None,
) -> Callable[[_CallableT], _CallableT]:
    """
    Register a Prodigy Teams recipe that doesn't start the annotation server and
    performs some computation, e.g. training. Usually used as a decorator.

    name (str): The recipe name.
    title (str): Display title of the recipe.
    description (str): Display description of the recipe.
    view_id (str): Prodigy UI ID to show in recipe preview in Prodigy Teams.
    field_props (Dict[str, Props]): Form field props for the UI, keyed by argument.
    cli_names (Dict[str, str]): Mapping of nested field names to nicer
        human-readable CLI argument names.
    module_name (Optional[str]): If specified, overrides the module path used
        to register the recipe. Defaults to the `__package__` of the function.
    """
    return teams_recipe(
        name=name,
        title=title,
        description=description,
        view_id=view_id,
        field_props=field_props,
        is_action=True,
        cli_names=cli_names,
        module_name=module_name,
    )


def teams_type(
    type: Optional[str] = None,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    props: Optional[Props] = None,
    field_props: Optional[Dict[str, Props]] = None,
    exclude: Optional[Set[str]] = None,
) -> Callable[[_T], _T]:
    """
    Decorator to register dataclasses as custom types. Dataclasses can define
    one or more custom subfields and an instance of the dataclass will be passed
    to the recipe function if it's used as a type annotation. Custom types can
    also be used as part of a union. This metadata defined in the decorator is
    propagated and merged to child classes that are also annotated with @teams_type.

    type (str): If provided this will be the type in the schema, instead of the
        class name. Useful for having shorter names and also for having a whole
        hierarchy with the same type, e.g. Dataset and Asset classes.
    title (str): Title shortcut. Will be merged to props afterwards.
    description (str): Description shortcut. Will be merged to props afterwards.
    props (Props): Additional type props that will be used whenever this type is
        used so you don't have to repeat it everywhere, but you can override it.
    field_props (Dict[str, Props]): Add metadata to this type's fields.
    exclude (Set[str]): Field names to not include in the schema.
    """
    exclude = set(exclude) if exclude is not None else set()
    field_props = dict(field_props) if field_props is not None else {}
    if props is None and title is None and description is None:
        props = None
    elif props is not None:
        props = props.copy()
        props.title = title if title is not None else props.title
        props.description = (
            description if description is not None else props.description
        )
    else:
        props = Props(title=title, description=description)

    def _teams_type(cls: _T) -> _T:
        # Wrap the class as a dataclass to ensure fields added to a subclass
        # are added correctly, even if the subclass is not decorated with
        # @dataclass (which is an easy mistake to make) or if type is defined
        # as a regular Python class.
        cls = dataclass(cls)  # type: ignore
        store_custom_type(
            cls, props=props, field_props=field_props, exclude=exclude, type_name=type
        )
        return cls

    return _teams_type


__all__ = ["teams_recipe", "task_recipe", "action_recipe", "teams_type"]
