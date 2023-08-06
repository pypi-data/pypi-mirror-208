from pathlib import Path
from typing import Any

import srsly

from prodigy.components.loaders import get_stream
from prodigy.types import StreamType

from .. import Props
from ..types import Dataset
from .decorator import teams_type

teams_type(
    "dataset",
    title="Dataset",
    description="Select an existing dataset or create a new one",
    exclude={"id", "name", "kind", "broker_id"},
)(Dataset)


@teams_type(
    "input-dataset",
    # fmt: off
    props=Props(title="Existing dataset", description="Select an existing dataset", exists=True),
    # fmt: on
)
class InputDataset(Dataset):
    """Custom type for a Prodigy data set used as an input source."""

    def load(self, **kwargs: Any) -> StreamType:
        return get_stream(f"dataset:{self.name}", loader="dataset", **kwargs)

    def export(self, path: Path) -> None:
        examples = self.load()
        srsly.write_jsonl(path, examples)


__all__ = ["InputDataset", "Dataset"]
