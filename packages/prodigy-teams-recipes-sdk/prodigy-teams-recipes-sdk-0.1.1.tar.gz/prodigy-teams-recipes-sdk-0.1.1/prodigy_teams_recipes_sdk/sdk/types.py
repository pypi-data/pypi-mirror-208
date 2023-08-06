from dataclasses import dataclass
from enum import Enum
from typing import Literal

import spacy

from . import assets, props
from .decorator import teams_type
from .util import get_spacy_langs

Goal = Literal["nooverlap", "overlap"]

Lang = Enum("Lang", {key: key for key in get_spacy_langs()})


@teams_type(
    "use",
    title="Include suggestions from model",
    description="Base questions on the model's predicted annotations.",
    field_props={"update": props.update_model},
)
@dataclass
class UseModel:
    name: assets.Model
    update: bool = False


@teams_type("blank", title="Blank model", field_props={"lang": props.lang})
@dataclass
class BlankModel:
    lang: Lang = Lang.en  # type: ignore

    def load(self) -> spacy.language.Language:
        lang = self.lang if isinstance(self.lang, str) else self.lang.value
        return spacy.blank(lang)


@teams_type(
    "blank-spans",
    title="Blank model",
    field_props={"lang": props.lang, "highlight_chars": props.highlight_chars},
)
@dataclass
class BlankModelSpans:
    lang: Lang = Lang.en  # type: ignore
    highlight_chars: bool = False

    def load(self) -> spacy.language.Language:
        lang = self.lang if isinstance(self.lang, str) else self.lang.value
        return spacy.blank(lang)


@teams_type(
    "classify-image",
    title="Annotate image categories",
    description="Select one or more category labels that apply to the image",
    field_props={"labels_exclusive": props.labels_exclusive},
)
@dataclass
class ImageClassification:
    labels_exclusive: bool = False


__all__ = [
    "Goal",
    "Lang",
    "UseModel",
    "BlankModel",
    "ImageClassification",
]
