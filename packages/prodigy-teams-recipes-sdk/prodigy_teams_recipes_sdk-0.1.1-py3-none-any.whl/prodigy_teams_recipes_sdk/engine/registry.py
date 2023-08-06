import builtins
import enum
from collections import defaultdict
from functools import cached_property
from typing import Dict, List, Optional, Union

from .recipe import Recipe
from .recipe_loader import RecipeLoader

REGISTRY: Optional["RecipeRegistry"] = None

# TODO: this type is annoying but it needs to allow passing in List[str]
LoadPath = Union[List[str], List[Union[str, "PackageSource"]]]


class PackageSource(enum.Enum):
    """
    Special load path values that allow you to specify the load order for
    dynamically discovered packages.
    """

    # Recipes from the built-in recipe package
    BUILTIN = object()
    # Recipes from packages discovered via entrypoints
    ENTRYPOINTS = object()
    # Recipes from packages that exist in the registry even if added manually
    IMPLICIT = object()


class RecipeRegistry:
    """
    The recipe registry handles registration and name lookups for recipes with
    support for lazy loading and deterministic resolution for name conflicts.

    Recipes are entered into the registry only when their containing module
    is imported. To prevent changes in import order from affecting name resolution
    the registry supports querying for recipes according to a load path specified
    by the caller. During recipe lookup, the recipe loader ensures that all
    recipes on the load path are imported before returning a result.

    By default, the load path prioritises recipes from custom recipe packages in
    order to allow overrides.
    """

    def __init__(self) -> None:
        self._loader = RecipeLoader()
        self._registry: Dict[str, Dict[str, Recipe]] = defaultdict(dict)
        self._default_load_path: LoadPath = [
            PackageSource.ENTRYPOINTS,
            PackageSource.BUILTIN,
            PackageSource.IMPLICIT,
        ]

    @cached_property
    def entrypoint_packages(self) -> List[str]:
        return self._loader.discover_packages_from_entrypoints()

    def set_load_path(self, load_path: LoadPath) -> None:
        self._default_load_path = load_path

    def _walk_load_path(self, load_path: Optional[LoadPath] = None):
        visited = builtins.set()
        if load_path is None:
            load_path = self._default_load_path
        for source in load_path:
            if source is PackageSource.BUILTIN:
                packages = [self._loader.builtin_recipes_package]
            elif source is PackageSource.ENTRYPOINTS:
                packages = self.entrypoint_packages
            elif source is PackageSource.IMPLICIT:
                packages = self._registry.keys()
            elif isinstance(source, str):
                packages = [source]
            else:
                raise ValueError(f"Invalid load path value: {source}")
            for package_name in packages:
                if package_name not in visited:
                    yield package_name
                    visited.add(package_name)

    def set(self, module_name: str, name: str, func: Recipe) -> None:
        # Only store the top level package until we have a reason to do otherwise
        package_name = module_name.split(".")[0]
        self._registry[package_name][name] = func

    def ensure_fully_loaded(self, package_name: str):
        # Normally we treat a missing package on the load path as an error
        # but we allow packages to be missing if there are already recipes
        # registered in its namespace. This is primarily intended for testing.
        has_registered_recipes = package_name.split(".")[0] in self._registry
        self._loader.load_package(package_name, must_exist=not has_registered_recipes)

    def get_all(self, load_path: Optional[LoadPath] = None) -> Dict[str, Recipe]:
        """
        Get all recipes in the registry.

        If multiple packages on the load path define the same recipe name, the first
        one on the load path is preferred.
        """
        # This preresolves name conflicts such that the first package on the load path is
        # preferred
        for p in self._walk_load_path(load_path):
            self.ensure_fully_loaded(p)
        result = {}
        for p in self._walk_load_path(load_path):
            recipes_in_p = self._registry.get(p, {})
            for name, recipe in recipes_in_p.items():
                if name not in result:
                    result[name] = recipe
        return result

    def want(self, name: str, load_path: Optional[LoadPath] = None) -> Optional[Recipe]:
        """
        Get a recipe definition from the registry, or return None if it isn't there.

        If multiple packages on the load path define the same recipe name, the first
        one on the load path is returned.
        """
        for p in self._walk_load_path(load_path):
            self.ensure_fully_loaded(p)
            recipes_in_p = self._registry.get(p, {})
            if name in recipes_in_p:
                return recipes_in_p[name]
        return None

    def need(self, name: str, load_path: Optional[LoadPath] = None) -> Recipe:
        """Get a recipe definition from the registry, or raise KeyError if it isn't there."""
        maybe_recipe = self.want(name, load_path=load_path)
        if maybe_recipe is None:
            opts = ", ".join(self.get_all(load_path=load_path).keys())
            raise KeyError(f"Can't find recipe '{name}'. Available: {opts}")
        return maybe_recipe

    def has(
        self,
        name: str,
        load_path: Optional[LoadPath] = None,
    ) -> bool:
        """Check whether the registry contains some recipe."""
        maybe_recipe = self.want(name, load_path=load_path)
        return maybe_recipe is not None

    def __contains__(self, name: str) -> bool:
        return self.has(name)


def get_recipes_registry() -> RecipeRegistry:
    global REGISTRY
    if REGISTRY is None:
        REGISTRY = RecipeRegistry()
    return REGISTRY


def has(name: str) -> bool:
    registry = get_recipes_registry()
    return registry.has(name)


def reset() -> None:
    global REGISTRY
    REGISTRY = RecipeRegistry()


def get_all() -> Dict[str, Recipe]:
    """
    Get all recipes in the registry.

    If multiple packages on the load path define the same recipe name, the first
    one on the load path is preferred.
    """
    registry = get_recipes_registry()
    return registry.get_all()


def set(module_name: str, name: str, recipe: Recipe) -> None:
    """Add a recipe definition to the registry."""
    registry = get_recipes_registry()
    registry.set(module_name, name, func=recipe)


def need(name: str) -> Recipe:
    """
    Get a recipe definition from the registry, or raise KeyError if it isn't there.

    If multiple packages on the load path define the same recipe name, the first
    one on the load path is returned.
    """
    registry = get_recipes_registry()
    return registry.need(name)


def want(name: str) -> Optional[Recipe]:
    """
    Get a recipe definition from the registry, or return None if it isn't there.

    If multiple packages on the load path define the same recipe name, the first
    one on the load path is returned.
    """
    registry = get_recipes_registry()
    return registry.want(name)


def keys() -> List[str]:
    """Get all keys from the registry, i.e. recipe names."""
    registry = get_recipes_registry()
    return list(registry.get_all().keys())
