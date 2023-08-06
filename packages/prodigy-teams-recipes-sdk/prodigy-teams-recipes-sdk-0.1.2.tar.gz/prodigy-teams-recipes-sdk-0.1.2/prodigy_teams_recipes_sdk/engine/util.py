from typing import Optional

from ..prodigy_teams_pam_sdk.recipe_utils import AnyProps, Props


def merge_props(x: Optional[AnyProps], y: Optional[AnyProps]) -> AnyProps:
    """Merge two sets of field props."""
    if x is None and y is None:
        return Props()
    elif x is None:
        assert y is not None
        return y.copy()
    elif y is None:
        assert x is not None
        return x.copy()
    else:
        x_ = x.dict(exclude_defaults=True)
        y_ = y.dict(exclude_defaults=True)
        for key in y_.keys():
            if key not in x_:
                x_[key] = getattr(y, key)
        output = x.__class__(**x_)
        return output
