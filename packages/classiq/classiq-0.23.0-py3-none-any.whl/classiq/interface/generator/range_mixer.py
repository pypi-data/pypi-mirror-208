import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams
from classiq.interface.generator.parameters import ParameterFloatType
from classiq.interface.generator.validations.validator_functions import (
    RegisterOrConst,
    validate_reg,
)

DATA_REG_INPUT_NAME = "data_reg_input"
LOWER_BOUND_REG_INPUT_NAME = "lower_bound_reg_input"
UPPER_BOUND_REG_INPUT_NAME = "upper_bound_reg_input"


DATA_REG_OUTPUT_NAME = "data_reg_output"
LOWER_BOUND_REG_OUTPUT_NAME = "lower_bound_reg_output"
UPPER_BOUND_REG_OUTPUT_NAME = "upper_bound_reg_output"


class RangeMixer(FunctionParams):
    """
    Mixing a fixed point number variable between a given lower and upper bounds.
    I.e. after applying this function the variable will hold a
    superposition of all the valid values.
    """

    data_reg_input: RegisterUserInput = pydantic.Field(
        description="The input variable to mix."
    )

    lower_bound_reg_input: RegisterOrConst = pydantic.Field(
        description="Fixed number or variable that define the lower bound for"
        " the mixing operation. In case of a fixed number bound, the value"
        " must be positive."
    )

    upper_bound_reg_input: RegisterOrConst = pydantic.Field(
        description="Fixed number or variable that define the upper bound for"
        " the mixing operation. In case of a fixed number bound, the value"
        " must be positive."
    )

    mixer_parameter: ParameterFloatType = pydantic.Field(
        description="The parameter used for rotation gates in the mixer.",
        is_exec_param=True,
    )

    @pydantic.validator("data_reg_input")
    def _validate_data_reg_input(cls, value: RegisterUserInput) -> RegisterUserInput:
        return value.copy(update={"name": DATA_REG_INPUT_NAME}, deep=True)

    @pydantic.validator("lower_bound_reg_input", pre=True)
    def _validate_lower_bound_reg_input(cls, value: RegisterOrConst) -> RegisterOrConst:
        return validate_reg(value, LOWER_BOUND_REG_INPUT_NAME)

    @pydantic.validator("upper_bound_reg_input", pre=True)
    def _validate_upper_bound_reg_input(cls, value: RegisterOrConst) -> RegisterOrConst:
        return validate_reg(value, UPPER_BOUND_REG_INPUT_NAME)

    def _create_ios(self) -> None:
        self._inputs = {DATA_REG_INPUT_NAME: self.data_reg_input}
        self._outputs = {DATA_REG_OUTPUT_NAME: self.data_reg_input}

        if isinstance(self.lower_bound_reg_input, RegisterUserInput):
            self._add_ios_if_reg_user_input(self.lower_bound_reg_input)

        if isinstance(self.upper_bound_reg_input, RegisterUserInput):
            self._add_ios_if_reg_user_input(self.upper_bound_reg_input)

    def _add_ios_if_reg_user_input(self, reg: RegisterUserInput) -> None:
        self._inputs[reg.name] = reg
        output_name = self._replace_input_with_output(reg.name)
        self._outputs[output_name] = reg

    @staticmethod
    def _replace_input_with_output(name: str) -> str:
        return name[: -len("input")] + "output"
