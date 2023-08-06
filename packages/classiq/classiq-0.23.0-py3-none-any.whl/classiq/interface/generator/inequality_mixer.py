import pydantic

from classiq.interface.generator import function_params
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.parameters import ParameterFloatType
from classiq.interface.generator.validations.validator_functions import (
    RegisterOrConst,
    RegisterOrConstOrDict,
    validate_reg,
)

DATA_REG_INPUT_NAME = "data_reg_input"
BOUND_REG_INPUT_NAME = "bound_reg_input"

DATA_REG_OUTPUT_NAME = "data_reg_output"
BOUND_REG_OUTPUT_NAME = "bound_reg_output"


class InequalityMixer(function_params.FunctionParams):
    """
    Mixing a fixed point number variable below a given upper bound or above a given
    lower bound. i.e. after applying this function the variable will hold a
    superposition position of all the valid values.
    """

    data_reg_input: RegisterUserInput = pydantic.Field(
        description="The input variable to mix."
    )

    bound_reg_input: RegisterOrConst = pydantic.Field(
        description="Fixed number or variable that define the upper or lower bound for"
        " the mixing operation. In case of a fixed number bound, the value"
        " must be positive."
    )

    mixer_parameter: ParameterFloatType = pydantic.Field(
        description="The parameter used for rotation gates in the mixer.",
        is_exec_param=True,
    )

    is_less_inequality: bool = pydantic.Field(
        default=True,
        description="Whether to mix below or above a certain bound."
        "Less inequality mixes between 0 and the given bound."
        "Greater inequality mixes between the bound and the maximal number allowed by"
        " the number of qubits (i.e 2^n - 1).",
    )

    @pydantic.validator("data_reg_input")
    def _validate_data_reg_input(cls, value: RegisterUserInput) -> RegisterUserInput:
        return value.revalued(name=DATA_REG_INPUT_NAME)

    @pydantic.validator("bound_reg_input", pre=True)
    def _validate_bound_reg_input(cls, value: RegisterOrConstOrDict) -> RegisterOrConst:
        return validate_reg(value, BOUND_REG_INPUT_NAME)

    def _create_ios(self) -> None:
        self._inputs = {DATA_REG_INPUT_NAME: self.data_reg_input}
        self._outputs = {DATA_REG_OUTPUT_NAME: self.data_reg_input}

        if isinstance(self.bound_reg_input, RegisterUserInput):
            self._inputs[BOUND_REG_INPUT_NAME] = self.bound_reg_input
            self._outputs[BOUND_REG_OUTPUT_NAME] = self.bound_reg_input
