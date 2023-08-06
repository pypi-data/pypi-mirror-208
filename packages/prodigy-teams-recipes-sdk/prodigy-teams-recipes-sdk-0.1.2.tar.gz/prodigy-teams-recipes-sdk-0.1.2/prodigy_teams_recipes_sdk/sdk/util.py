from pathlib import Path
from typing import Dict, cast

import spacy
import spacy.lang
import srsly
from spacy.about import __version__ as spacy_version
from spacy.util import get_lang_class

# Super basic caching – should work in theory, although it doesn't currently
# capture custom languages registered via entry points
LANGS_CACHE = Path(__file__).parent / f"spacy_langs_{spacy_version}.json"


def get_spacy_langs() -> Dict[str, str]:
    # This is hacky and slow, and maybe we can find a better solution? The
    # problem here is the language data is lazy-loaded, so we can't go via the
    # module. And we need to import the language class to get its human-readable
    # name.
    if LANGS_CACHE.exists():
        return cast(Dict[str, str], srsly.read_json(LANGS_CACHE))
    overrides = {"xx": "Multi-language"}
    lang_dir = Path(spacy.lang.__file__).parent
    langs = {}
    for path in sorted(lang_dir.iterdir()):
        if path.is_dir() and len(path.name) <= 3:
            lang = path.name
            if lang in overrides:
                name = overrides[lang]
            else:
                name = get_lang_class(lang).__name__
            langs[lang] = name
    srsly.write_json(LANGS_CACHE, langs)
    return langs
