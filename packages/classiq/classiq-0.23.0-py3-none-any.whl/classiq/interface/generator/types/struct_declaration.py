from typing import Dict

import pydantic

from classiq.interface.generator.functions.classical_type import ClassicalType
from classiq.interface.helpers.custom_pydantic_types import PydanticFunctionNameStr
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class StructDeclaration(HashablePydanticBaseModel):
    name: PydanticFunctionNameStr
    variables: Dict[str, ClassicalType] = pydantic.Field(
        default_factory=dict,
        description="Dictionary of variable names and their classical type",
    )
