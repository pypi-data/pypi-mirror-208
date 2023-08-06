import abc
from typing import Any, Dict, Iterable

import pydantic

from classiq.interface.generator.arith import argument_utils
from classiq.interface.generator.arith.arithmetic_operations import (
    ArithmeticOperationParams,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import get_zero_input_name

Numeric = (float, int)


class Extremum(ArithmeticOperationParams):
    left_arg: argument_utils.RegisterOrConst
    right_arg: argument_utils.RegisterOrConst

    @pydantic.root_validator(pre=True)
    def _validate_one_is_register(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        left_arg = values.get("left_arg")
        right_arg = values.get("right_arg")
        if isinstance(left_arg, Numeric) and isinstance(right_arg, Numeric):
            raise ValueError("One argument must be a register")
        if isinstance(left_arg, RegisterUserInput) and isinstance(
            right_arg, RegisterUserInput
        ):
            assert left_arg.name != right_arg.name
        if left_arg is right_arg and isinstance(left_arg, pydantic.BaseModel):
            # In case both arguments refer to the same object, copy it.
            # This prevents changes performed on one argument to affect the other.
            values["right_arg"] = left_arg.copy(deep=True)
        return values

    def _create_ios(self) -> None:
        self._inputs = dict()
        if isinstance(self.left_arg, RegisterUserInput):
            self._inputs[self.left_arg.name] = self.left_arg
        if isinstance(self.right_arg, RegisterUserInput):
            self._inputs[self.right_arg.name] = self.right_arg
        zero_input_name = get_zero_input_name(self.output_name)
        self._zero_inputs = {zero_input_name: self.result_register}
        self._outputs = {**self._inputs, **{self.output_name: self.result_register}}

    def is_inplaced(self) -> bool:
        return False

    def get_params_inplace_options(self) -> Iterable["Extremum"]:
        return ()

    @classmethod
    @abc.abstractmethod
    def _bound_calculator(cls, arg1: float, arg2: float) -> float:
        pass

    def _get_result_register(self) -> RegisterUserInput:
        integer_part_size = max(
            argument_utils.integer_part_size(self.left_arg),
            argument_utils.integer_part_size(self.right_arg),
        )
        fraction_places = max(
            argument_utils.fraction_places(self.left_arg),
            argument_utils.fraction_places(self.right_arg),
        )
        required_size = integer_part_size + fraction_places
        bounds = (
            self._bound_calculator(
                argument_utils.lower_bound(self.left_arg),
                argument_utils.lower_bound(self.right_arg),
            ),
            self._bound_calculator(
                argument_utils.upper_bound(self.left_arg),
                argument_utils.upper_bound(self.right_arg),
            ),
        )
        return RegisterUserInput(
            size=self.output_size or required_size,
            fraction_places=fraction_places,
            is_signed=self._include_sign and min(bounds) < 0,
            name=self.output_name,
            bounds=self._legal_bounds(bounds),
        )


class Min(Extremum):
    output_name = "min_value"

    @classmethod
    def _bound_calculator(cls, arg1: float, arg2: float) -> float:
        return min(arg1, arg2)


class Max(Extremum):
    output_name = "max_value"

    @classmethod
    def _bound_calculator(cls, arg1: float, arg2: float) -> float:
        return max(arg1, arg2)
