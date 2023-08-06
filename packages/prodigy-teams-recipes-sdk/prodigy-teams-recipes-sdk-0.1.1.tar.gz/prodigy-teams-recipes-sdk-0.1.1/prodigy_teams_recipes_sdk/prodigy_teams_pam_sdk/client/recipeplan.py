from ..models import (
    ObjectValidation,
    RecipePlanCreating,
    RecipePlanDeleting,
    RecipePlanReading,
    RecipePlanReturning,
    RecipePlanUpdating,
)
from .base import ModelClient


class RecipePlan(
    ModelClient[
        RecipePlanCreating,
        RecipePlanReading,
        RecipePlanUpdating,
        RecipePlanDeleting,
        RecipePlanReturning,
        RecipePlanReturning,
    ]
):
    Creating = RecipePlanCreating
    Reading = RecipePlanReading
    Updating = RecipePlanUpdating
    Deleting = RecipePlanDeleting
    Returning = RecipePlanReturning

    def validate_objects(self, data: RecipePlanCreating) -> ObjectValidation:
        res = self.request(
            "POST",
            endpoint="validate-objects",
            data=data,
            return_model=ObjectValidation,
        )
        assert isinstance(res, ObjectValidation)
        return res

    async def validate_objects_async(
        self, data: RecipePlanCreating
    ) -> ObjectValidation:
        res = await self.request_async(
            "POST",
            endpoint="validate-objects",
            data=data,
            return_model=ObjectValidation,
        )
        assert isinstance(res, ObjectValidation)
        return res
