from enum import Enum
from typing import Any

import pydantic

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.function_params import PortDirection
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class PortDeclarationDirection(str, Enum):
    Input = "input"
    Inout = "inout"
    Output = "output"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PortDeclarationDirection):
            return super().__eq__(other)
        if isinstance(other, PortDirection):
            return self == self.Inout or self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    def includes_port_direction(self, direction: PortDirection) -> bool:
        return self in (direction, self.Inout)

    @property
    def is_input(self) -> bool:
        return self.includes_port_direction(PortDirection.Input)

    @property
    def is_output(self) -> bool:
        return self.includes_port_direction(PortDirection.Output)

    @classmethod
    def from_port_direction(
        cls, port_direction: PortDirection
    ) -> "PortDeclarationDirection":
        return cls(port_direction.value)


class PortDeclaration(HashablePydanticBaseModel):
    name: str
    size: Expression
    direction: PortDeclarationDirection
    is_signed: Expression = pydantic.Field(default=Expression(expr="false"))
    fraction_places: Expression = pydantic.Field(default=Expression(expr="0"))

    class Config:
        frozen = True
