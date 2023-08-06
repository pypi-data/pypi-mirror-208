from enum import Enum
from typing import Optional

import pydantic

from classiq.interface.chemistry import operator
from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import (
    DEFAULT_INPUT_NAME,
    DEFAULT_OUTPUT_NAME,
    FunctionParams,
)


class ExponentiationOptimization(str, Enum):
    MINIMIZE_DEPTH = "MINIMIZE_DEPTH"
    MINIMIZE_ERROR = "MINIMIZE_ERROR"


class ExponentiationConstraints(pydantic.BaseModel):
    max_depth: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None, description="Maximum depth of the exponentiation circuit."
    )
    max_error: Optional[pydantic.PositiveFloat] = pydantic.Field(
        default=None,
        description="Maximum approximation error of the exponentiation circuit.",
    )

    class Config:
        frozen = True


class Exponentiation(FunctionParams):
    """
    Exponentiation of a Hermitian Pauli sum operator.
    """

    pauli_operator: PauliOperator = pydantic.Field(
        description="A weighted sum of Pauli strings."
    )
    evolution_coefficient: float = pydantic.Field(
        default=1.0, description="A global coefficient multiplying the operator."
    )
    constraints: ExponentiationConstraints = pydantic.Field(
        default_factory=ExponentiationConstraints,
        description="Constraints for the exponentiation.",
    )
    optimization: ExponentiationOptimization = pydantic.Field(
        default=ExponentiationOptimization.MINIMIZE_DEPTH,
        description="What attribute to optimize.",
    )
    use_naive_evolution: bool = pydantic.Field(
        default=False, description="Whether to evolve the operator naively"
    )

    @pydantic.validator("pauli_operator")
    def _validate_is_hermitian(cls, pauli_operator: PauliOperator) -> PauliOperator:
        return operator.validate_operator_is_hermitian(pauli_operator)

    def _create_ios(self) -> None:
        size = self.pauli_operator.num_qubits
        self._inputs = {
            DEFAULT_INPUT_NAME: RegisterUserInput(name=DEFAULT_INPUT_NAME, size=size)
        }
        self._outputs = {
            DEFAULT_OUTPUT_NAME: RegisterUserInput(name=DEFAULT_OUTPUT_NAME, size=size)
        }
