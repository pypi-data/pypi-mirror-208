import importlib.util
import inspect
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict, cast

import srsly
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, Response

from ..about import __version__
from . import registry
from .recipe import Recipe


class PreviewData(TypedDict):
    name: str
    path: Optional[str]


BUNDLE_FILE = "preview.js"
INDEX_PATH = Path(__file__).parent / "preview.html"
BUNDLE_PATH = Path(__file__).parent / BUNDLE_FILE
RECIPE_PATH = Path(__file__).parent / "recipe.json"

with INDEX_PATH.open("r", encoding="utf8") as file_:
    INDEX_HTML = file_.read()
with BUNDLE_PATH.open("r", encoding="utf8") as file_:
    JAVASCRIPT = file_.read()


app = FastAPI(title="Prodigy Teams Recipe Preview", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serve_preview(
    recipe_name: str, path: Optional[Path], host: str = "localhost", port: int = 9090
) -> None:
    """Serve a built-in or local recipe file on a given host and port."""
    path = path.absolute() if path else None
    set_recipe(recipe_name, path)
    recipe = get_recipe()
    url = f"http://{host}:{port}"
    print("Starting the preview server...")
    print("SCHEMA  ", f"{url}/schema")
    print("PREVIEW ", url)
    uvicorn.run(
        f"{__name__}:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[
            # Parent directory of current recipe function
            str(Path(inspect.getfile(recipe.func)).parent),
            # This package for local development
            str(Path(__file__).parent.parent),
        ],
        log_level="warning",
    )


def import_recipe(path: Path) -> None:
    spec = importlib.util.spec_from_file_location("recipe", str(path))
    module = importlib.util.module_from_spec(spec)  # pyright: ignore
    spec.loader.exec_module(module)  # pyright: ignore


# Important note: This is a bit ugly and unideal but we're writing the currently
# set recipe and path to a JSON file. This is necessary because in order to
# use uvicorn's auto-reloading, we need to run the app from a string (module)
# and can't just call it on the app function. This means that uvicorn imports
# the module in another process and given the nature of ASGI servers, we can't
# pass arbitrary settings like the recipe name and path to it.
def set_recipe(recipe_name: str, path: Optional[Path]) -> None:
    data = {"name": recipe_name, "path": str(path) if path else None}
    srsly.write_json(RECIPE_PATH, data)


def get_recipe() -> Recipe:
    assert RECIPE_PATH.exists(), "no recipe set"
    data = cast(PreviewData, srsly.read_json(RECIPE_PATH))
    if data["path"] is not None:
        import_recipe(Path(data["path"]))
    return registry.need(data["name"])


@app.get("/")
def static_root() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@app.get(f"/{BUNDLE_FILE}")
def static_bundle() -> Response:
    return Response(JAVASCRIPT, media_type="application/javascript")


@app.get("/schema")
def schema() -> Dict[str, Any]:
    """Request the JSON form schema for the currently served recipe."""
    data = get_recipe().to_json()
    return data["form_schema"]
