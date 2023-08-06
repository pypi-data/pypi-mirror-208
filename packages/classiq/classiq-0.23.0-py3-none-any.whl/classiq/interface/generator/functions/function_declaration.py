import abc
from typing import Dict, Mapping, Union

import pydantic
from typing_extensions import Self

from classiq.interface.generator.expressions.expression import resolve_expressions
from classiq.interface.generator.functions.classical_type import ClassicalType
from classiq.interface.generator.functions.port_declaration import PortDeclaration
from classiq.interface.helpers.custom_pydantic_types import PydanticFunctionNameStr
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)

UNRESOLVED_SIZE = 1000


class FunctionDeclaration(HashablePydanticBaseModel, abc.ABC):
    """
    Facilitates the creation of a common function interface object.
    """

    name: PydanticFunctionNameStr = pydantic.Field(
        description="The name of the function"
    )

    param_decls: Dict[str, ClassicalType] = pydantic.Field(
        description="The expected interface of the functions parameters",
        default_factory=dict,
    )

    def resolve_expressions(self) -> Self:
        return resolve_expressions(self, self.param_decls.copy())

    @pydantic.validator("name")
    def _validate_name(cls, name: str) -> str:
        validate_name_end_not_newline(name=name)
        return name

    @staticmethod
    def _validate_declaration_names(
        declarations: Mapping[str, Union["FunctionDeclaration", PortDeclaration]],
        declaration_name: str,
    ) -> None:
        if not all(
            [name == declaration.name for (name, declaration) in declarations.items()]
        ):
            raise ValueError(
                f"{declaration_name} declaration names should match the keys of their names."
            )

    class Config:
        frozen = True
        extra = pydantic.Extra.forbid


class OperandDeclaration(FunctionDeclaration):
    is_list: bool = pydantic.Field(
        description="Indicate whether the operand expects an unnamed list of lambdas",
        default=False,
    )


def validate_name_end_not_newline(name: str) -> None:
    _new_line = "\n"
    if name.endswith(_new_line):
        raise ValueError("Function name cannot end in a newline character")


FunctionDeclaration.update_forward_refs()
