from typing import Any, Collection, Dict

import pydantic

from classiq.interface.generator.arith import number_utils
from classiq.interface.generator.generated_circuit_data import GeneratedRegister

from classiq.exceptions import ClassiqStateInitializationError


class RegisterInitialization(pydantic.BaseModel):
    register_data: GeneratedRegister = pydantic.Field(
        description="Register information"
    )
    initial_condition: pydantic.NonNegativeInt = pydantic.Field(
        description="Initial register state"
    )

    @pydantic.validator("initial_condition", pre=True)
    def _validate_initial_condition(cls, value: int) -> int:
        if not isinstance(value, int) or value < 0:
            raise ClassiqStateInitializationError(
                "Only Natural number are support as an initial condition for the "
                "registers. "
            )
        return value

    @pydantic.root_validator()
    def _validate_register_initialization(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        register_data = values.get("register_data")
        assert isinstance(register_data, GeneratedRegister)
        initial_condition: int = values.get("initial_condition", 0)

        initial_condition_length = number_utils.size(initial_condition)
        register_length = len(register_data.qubit_indexes_absolute)
        if initial_condition_length > register_length:
            raise ClassiqStateInitializationError(
                f"Register {register_data.name} has {register_length} qubits, which is not enough to represent the number {initial_condition}."
            )
        return values

    @classmethod
    def initialize_registers(
        cls,
        registers: Collection[GeneratedRegister],
        initial_conditions: Dict[str, int],
    ) -> Dict[str, "RegisterInitialization"]:
        return {
            reg.name: cls(
                register_data=reg, initial_condition=initial_conditions[reg.name]
            )
            for reg in registers
        }
