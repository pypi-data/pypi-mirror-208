from ..models import (
    RecipeCreating,
    RecipeDeleting,
    RecipeDetail,
    RecipeListingLatest,
    RecipeReading,
    RecipeReadingLatest,
    RecipeReturning,
    RecipeUpdating,
)
from .base import VersionedModelClient


class Recipe(
    VersionedModelClient[
        RecipeCreating,
        RecipeReading,
        RecipeUpdating,
        RecipeDeleting,
        RecipeReturning,
        RecipeDetail,
        RecipeReadingLatest,
        RecipeListingLatest,
    ]
):
    Creating = RecipeCreating
    Reading = RecipeReading
    Updating = RecipeUpdating
    Deleting = RecipeDeleting
    Returning = RecipeReturning
    Detail = RecipeDetail
    ReadingLatest = RecipeReadingLatest
    ListingLatest = RecipeListingLatest
