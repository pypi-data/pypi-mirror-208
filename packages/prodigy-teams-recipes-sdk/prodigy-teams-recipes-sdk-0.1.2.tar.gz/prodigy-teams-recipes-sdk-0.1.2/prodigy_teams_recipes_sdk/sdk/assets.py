import tempfile
from pathlib import Path
from typing import Any, ClassVar, List, Literal, Optional

import spacy
import srsly
from cloudpathlib import AnyPath, CloudPath
from spacy.language import Language

from prodigy.components.loaders import get_stream
from prodigy.models.matcher import PatternMatcher
from prodigy.types import StreamType
from prodigy.util import log

from ..prodigy_teams_pam_sdk.recipe_utils import OptionalProps
from ..types import Asset
from .decorator import teams_type

teams_type(
    "asset",
    title="Asset",
    description="Select one asset from the ones available in your cluster.",
    exclude={"id", "broker_id", "name", "version", "kind", "path", "meta"},
)(Asset)


@teams_type(
    "model",
    title="Model",
    description="spaCy model. If you have custom pipelines, you can add them to your cluster",
)
class Model(Asset[Literal["model"]]):
    """Custom type for a spaCy model asset uploaded to the cluster."""

    kind: ClassVar[Literal["model"]] = "model"

    def load(self, download_to: Optional[Path] = None) -> Language:
        assert self.path is not None
        path = AnyPath(self.path)
        if isinstance(path, CloudPath):
            if download_to:
                path.download_to(download_to)
                nlp = spacy.load(download_to)
            else:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    download_to = Path(tmpdirname)
                    path.download_to(download_to)
                    nlp = spacy.load(download_to)
            return nlp
        return spacy.load(path)


@teams_type(
    "input",
    title="Input data asset",
    description="Upload data to your cluster and it will be available here",
)
class Input(Asset[Literal["input"]]):
    """Custom type for a input data asset uploaded to the cluster."""

    kind: ClassVar[Literal["input"]] = "input"

    def load(self, **kwargs: Any) -> StreamType:
        if not kwargs.get("loader") and "loader" in self.meta:
            kwargs["loader"] = self.meta["loader"]
        log(f"LOADER: Loading asset {self.name} with loader '{kwargs['loader']}'")
        return get_stream(self.path, **kwargs)


@teams_type(
    "patterns",
    title="Patterns",
    description="Rules to generate pattern suggestions. Can be uploaded to your cluster.",
    props=OptionalProps(optional_title="Include suggestions from match patterns"),
)
class Patterns(Asset[Literal["patterns"]]):
    """Custom type for a PatternMatcher patterns file uploaded to the cluster."""

    kind: ClassVar[Literal["patterns"]] = "patterns"

    def load(
        self,
        nlp: Language,
        label: Optional[List[str]] = None,
        label_span: bool = True,
        label_task: bool = False,
        combine_matches: bool = True,
        all_examples: bool = True,
        allow_overlap: bool = False,
    ) -> PatternMatcher:
        matcher = PatternMatcher(
            nlp,
            label_span=label_span,
            label_task=label_task,
            filter_labels=label,
            combine_matches=combine_matches,
            all_examples=all_examples,
            allow_overlap=allow_overlap,
        )
        path = AnyPath(self.path)
        patterns = []
        # read each pattern file and add patterns to matcher
        for fl in path.glob("**/*.jsonl"):
            patterns.extend(list(srsly.read_jsonl(fl)))  # type: ignore
        matcher.add_patterns(patterns=patterns)
        return matcher


__all__ = ["Asset", "Input", "Model", "Patterns"]
