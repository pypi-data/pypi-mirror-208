from typing import ClassVar

from .. import BoolProps, ChoiceProps, ListProps, Props, TextProps, Validation
from ..sdk.util import get_spacy_langs


class Titles:
    dataset_existing: ClassVar[str] = "Existing dataset"
    update_model: ClassVar[str] = ""
    dataset_new: ClassVar[str] = "New dataset"


class Descriptions:
    update_model: ClassVar[str] = ""
    dataset_existing: ClassVar[str] = "Select an existing dataset"
    dataset_new: ClassVar[str] = "Create a new dataset"


dataset_new = TextProps(
    title=Titles.dataset_new,
    placeholder="Type the name of the new dataset",
    exists=False,
    validations=[
        # TODO: add validation to check it's NOT a UUID
        Validation(
            op="re",
            value="^[\\w-]+$",
            message="It can contain only numbers, letters, dashes '-' and underscores '_'",
            level="error",
        )
    ],
)

dataset_existing = Props(
    title=Titles.dataset_existing,
    description=Descriptions.dataset_existing,
    exists=True,
)

dataset_choice = TextProps(
    title="Dataset",
    description="Select an existing dataset or create a new one",
    validations=[
        Validation(
            op="re",
            value="^[\\w-]+$",
            message="It can contain only numbers, letters, dashes '-' and underscores '_'",
            level="error",
        )
    ],
)

label = ListProps(
    title="Label(s)",
    description="Comma-separated list of labels to annotate",
    placeholder="Type labels here...",
    validations=[
        Validation(
            op="gt",
            value=20,
            message="The model can perform better with less than 20 labels",
            level="warning",
        )
    ],
)

model = Props(title="Model")

segment = BoolProps(
    title="Auto-segment sentences",
    description="Uses the model if available or a simple rule-based strategy otherwise.",
)

labels_exclusive = BoolProps(
    title="Mutually exclusive labels",
    description="Every example has exactly one correct label.",
)

update_model = BoolProps(
    title="Update the model in the loop",
    description="Update the model in the loop with the received annotations.",
)

lang = ChoiceProps(
    title="Language",
    description="Base language to use for tokenization",
    widget="select",
    choice={
        key: Props(name=key, title=value) for key, value in get_spacy_langs().items()
    },
)

goal = ChoiceProps(
    title="Data collection goal",
    choice={
        "nooverlap": Props(title="Annotate all examples once"),
        "overlap": Props(title="Annotate with overlap"),
    },
)

highlight_chars = BoolProps(
    # fmt: off
    title="Allow highlighting individual characters instead of tokens",
    description="Keep in mind that this may produce annotations that are not aligned with the tokenization of the model you might want to train later on."
    # fmt: on
)

view_id = ChoiceProps(title="ID of the interface to use")

asser_or_dataset = ChoiceProps(title="Input data to annotate")
