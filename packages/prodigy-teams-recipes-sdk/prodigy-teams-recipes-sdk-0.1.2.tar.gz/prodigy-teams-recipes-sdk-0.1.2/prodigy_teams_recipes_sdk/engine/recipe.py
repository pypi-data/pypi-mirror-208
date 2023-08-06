from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    cast,
)

import srsly
from radicli import Command
from radicli.util import StaticCommand

from ..prodigy_teams_pam_sdk.recipe_utils import (
    AnyProps,
    PlanType,
    RecipeSchema,
    get_field_cli_args,
    parse_plan,
)
from .recipe_schema import make_schema
from .teams_type import get_custom_type

_RecipeT = TypeVar("_RecipeT", bound="Recipe")


class RecipeJSON(TypedDict):
    """JSON representation of a recipe that can be sent over REST."""

    name: str  # recipe name
    title: str  # recipe display title
    description: str  # recipe diplay description
    is_action: bool  # whether it's an action (if False, it starts annotation server)
    form_schema: Dict[str, Any]  # serialized schema for the form
    cli_schema: StaticCommand  # serialized CLI command for the recipe
    entry_point: str  # name of Python entry point
    meta: Dict[str, Any]  # additional meta information


@dataclass
class Recipe:
    func: Callable
    schema: RecipeSchema
    cli: Command
    is_action: bool
    entry_point: str

    @classmethod
    def from_decorator(
        cls: Type[_RecipeT],
        func: Callable,
        name: Optional[str],
        title: Optional[str],
        description: Optional[str],
        view_id: Optional[str],
        field_props: Dict[str, AnyProps],
        is_action: bool,
        cli_names: Dict[str, str],
    ) -> _RecipeT:
        """Create a Recipe object from the recipe decorator."""
        schema = make_schema(
            func,
            name=name,
            title=title,
            description=description,
            view_id=view_id,
            field_props=field_props,
            cli_names=cli_names,
        )
        cli = make_cli(func, schema)
        return cls(
            func=func,
            schema=schema,
            cli=cli,
            is_action=is_action,
            entry_point=f"{func.__module__}:{func.__name__}",
        )

    @property
    def name(self) -> str:
        return self.schema.name

    def parse_plan(
        self, plan: PlanType, objects_map: Dict[str, Dict[str, Dict[str, Any]]]
    ) -> Tuple[List[str], Dict]:
        """
        Generate positional and keyword arguments for a recipe function from a
        recipe plan, i.e. a dictionary of parsed values from the CLI.
        """
        return parse_plan(self.schema, plan, objects_map, get_custom_type)

    def to_json(self) -> RecipeJSON:
        """Serialize a recipe to JSON."""
        # We need to dump/load here to ensure values are serialized correctly
        data = srsly.json_loads(self.schema.json(exclude_none=True, exclude_unset=True))
        form_schema = cast(Dict[str, Any], data)
        return RecipeJSON(
            name=self.name,
            title=self.schema.title or "",
            description=self.schema.description or "",
            is_action=self.is_action,
            form_schema=form_schema,
            cli_schema=self.cli.to_static_json(),
            meta={},
            entry_point=self.entry_point,
        )


def make_cli(func: Callable, schema: Optional[RecipeSchema] = None) -> Command:
    """
    Construct a JSON-serializable radicli Command from a function and optionally a
    RecipeSchema. If the RecipeSchema isn't provided, it's built using make_schema.
    """
    if schema is None:
        schema = make_schema(
            func,
            name=None,
            title=None,
            description=None,
            view_id=None,
            field_props={},
            cli_names={},
        )
    ap_args = []
    for field in schema.fields:
        ap_args.extend(get_field_cli_args(field, schema.cli_names))
    desc = (
        f"{schema.title}: {schema.description}"
        if schema.title
        else schema.description or None
    )
    return Command(schema.name, description=desc, args=ap_args, func=func)
