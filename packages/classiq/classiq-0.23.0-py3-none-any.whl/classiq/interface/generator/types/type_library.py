from typing import List, Union

import pydantic

from classiq.interface.generator.expressions.expression import resolve_expressions
from classiq.interface.generator.types.combinatorial_problem import (
    CombinatorialOptimizationStructDeclaration,
)
from classiq.interface.generator.types.struct_declaration import StructDeclaration
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)
from classiq.interface.helpers.validation_helpers import is_list_unique

ConcreteStructDeclaration = Union[
    CombinatorialOptimizationStructDeclaration, StructDeclaration
]


TYPE_LIBRARY_DUPLICATED_TYPE_NAMES = (
    "Cannot have multiple struct types with the same name"
)


class TypeLibrary(HashablePydanticBaseModel):
    types: List[ConcreteStructDeclaration] = pydantic.Field(default_factory=list)

    @pydantic.validator("types")
    def types_validator(cls, types: List[ConcreteStructDeclaration]):
        if not is_list_unique([struct_type.name for struct_type in types]):
            raise ValueError(TYPE_LIBRARY_DUPLICATED_TYPE_NAMES)

        return [resolve_expressions(struct_type, dict()) for struct_type in types]
