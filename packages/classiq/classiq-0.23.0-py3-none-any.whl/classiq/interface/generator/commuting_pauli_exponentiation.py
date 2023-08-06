import pydantic

from classiq.interface.chemistry import operator
from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator.function_params import (
    DEFAULT_INPUT_NAME,
    DEFAULT_OUTPUT_NAME,
    FunctionParams,
)
from classiq.interface.generator.parameters import ParameterFloatType

from classiq import RegisterUserInput


class CommutingPauliExponentiation(FunctionParams):
    """
    Exponentiation of a Hermitian Pauli sum operator with commuting pauli strings.
    """

    pauli_operator: PauliOperator = pydantic.Field(
        description="A weighted sum of Pauli strings."
    )
    evolution_coefficient: ParameterFloatType = pydantic.Field(
        default=1.0,
        description="A global coefficient multiplying the operator.",
        is_exec_param=True,
    )

    @pydantic.validator("pauli_operator")
    def _validate_is_hermitian(cls, pauli_operator: PauliOperator) -> PauliOperator:
        return operator.validate_operator_is_hermitian(pauli_operator)

    @pydantic.validator("pauli_operator")
    def _validate_paulis_commute(cls, pauli_operator: PauliOperator) -> PauliOperator:
        if not pauli_operator.is_commutative:
            raise ValueError("Pauli strings are not commutative")
        return pauli_operator

    def _create_ios(self) -> None:
        size = self.pauli_operator.num_qubits
        self._inputs = {
            DEFAULT_INPUT_NAME: RegisterUserInput(name=DEFAULT_INPUT_NAME, size=size)
        }
        self._outputs = {
            DEFAULT_OUTPUT_NAME: RegisterUserInput(name=DEFAULT_OUTPUT_NAME, size=size)
        }
