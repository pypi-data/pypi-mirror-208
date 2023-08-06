import builtins
import importlib
import importlib.metadata as importlib_metadata
import importlib.util as importlib_util
import pkgutil
from collections import defaultdict
from types import ModuleType
from typing import Dict, List, Union

AVAILABLE_ENTRY_POINTS = None


def import_submodules(package, recursive=True):
    """Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


class RecipeLoader:
    """
    Handles discovery and recursive imports of recipe packages on demand.
    """

    def __init__(
        self,
    ):
        # The entrypoint namespace we search for to discover installed
        # recipe packages in the local environment.
        self._entry_point_namespace = "prodigy_teams_recipes"
        # When _loaded[package] is True, all recipes under that namespace
        # are imported. Contains both top-level packages and modules.
        self._loaded = {}
        # _known_import_paths[package] specifies an optional subset of modules
        # containing recipes. Custom recipe packages can specify these through
        # a list of entrypoints under self._entry_point_namespace
        self._known_import_paths: Dict[str, List[str]] = {}

    def discover_packages_from_entrypoints(self) -> List[str]:
        """
        Find all installed packages that specify a recipe entrypoint.

        Returns the top level recipe package and caches the specified
        submodule paths containing recipes.
        """
        discovered = self._get_entrypoints()

        def sorted_unique_modules(entrypoints):
            # For now, only consider the module names of the entrypoints.
            # Since we may be able to enumerate recipes individually in
            # the future, this this ensures compatibility with newer
            # recipe packages.
            return list(sorted(builtins.set([e.module for e in entrypoints])))

        self._known_import_paths.update(
            {
                package: sorted_unique_modules(entrypoints)
                for package, entrypoints in discovered.items()
            }
        )
        return list(discovered.keys())

    def _get_entrypoints(self) -> Dict[str, List[importlib_metadata.EntryPoint]]:
        """
        Gets all raw entrypoints in the `prodigy_teams_recipes` namespace from the current venv
        """
        # Entrypoint scans are expensive, so we only do the environment scan once.
        global AVAILABLE_ENTRY_POINTS

        by_package = defaultdict(list)
        if AVAILABLE_ENTRY_POINTS is None:
            AVAILABLE_ENTRY_POINTS = importlib_metadata.entry_points()

        for entrypoint in AVAILABLE_ENTRY_POINTS.get(self._entry_point_namespace, []):
            package_name = entrypoint.module.split(".")[0]
            by_package[package_name].append(entrypoint)
        return dict(by_package)

    def load_recursive(
        self, recipes_root: Union[str, ModuleType], must_exist: bool = True
    ):
        """
        Import all recipes from a root recipes module (e.g. `prodigy_teams_recipes.recipes`)
        """
        name = recipes_root if isinstance(recipes_root, str) else recipes_root.__name__  # type: ignore
        if name in self._loaded:
            return self._loaded[name]
        loaded = False
        try:
            imported_modules: Dict[str, ModuleType] = import_submodules(recipes_root)
            for module in imported_modules.keys():
                self._loaded[module] = True
            loaded = True
        except ImportError:
            if must_exist:
                raise
        finally:
            self._loaded[name] = loaded
        return self._loaded[name]

    def load_package(
        self, package_root: Union[str, ModuleType], must_exist: bool = True
    ):
        """
        Import all recipes from a package (e.g. `prodigy_teams_recipes`)
        """
        package_name = package_root if isinstance(package_root, str) else package_root.__name__  # type: ignore
        package_name = package_name.split(".")[0]
        if package_name in self._loaded:
            return self._loaded[package_name]
        loaded = False
        import_paths = self._known_import_paths.get(package_name, [])
        if import_paths:
            # If explicit recipe modules are specified, import those
            for module in import_paths:
                if self.load_recursive(module, must_exist=must_exist):
                    loaded = True
        else:
            # Otherwise, default to a heuristic of trying ".recipes" and "."
            for subpath in [".recipes", "."]:
                module = importlib_util.resolve_name(subpath, package_name)
                if self.load_recursive(module, must_exist=False):
                    loaded = True
        self._loaded[package_name] = loaded
        if not loaded and must_exist:
            raise ImportError(
                f"No recipes found in package '{package_name}'. "
                f"Make sure the package is installed and contains a "
                f"top-level module named .recipes, or specify the "
                f"recipe module(s) explicitly via the "
                f"{self._entry_point_namespace} entrypoint."
            )
        return loaded

    @property
    def builtin_recipes_package(self) -> str:
        """Returns the root package name for the built-in recipes"""
        return "prodigy_teams_recipes"
