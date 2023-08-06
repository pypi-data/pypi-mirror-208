from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, Generic, Iterable, Optional, Tuple, TypeVar, Union

import pydantic
from pydantic.generics import GenericModel
from typing_extensions import Literal

from classiq.interface.generator.arith import argument_utils, number_utils
from classiq.interface.generator.arith.argument_utils import RegisterOrConst
from classiq.interface.generator.arith.arithmetic_operations import (
    ArithmeticOperationParams,
)
from classiq.interface.generator.arith.ast_node_rewrite import (
    NOT_POWER_OF_TWO_ERROR_MSG,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.arith.unary_ops import Negation
from classiq.interface.generator.function_params import get_zero_input_name

_DEFAULT_RIGHT_ARG_NAME = "right_arg"
_DEFAULT_LEFT_ARG_NAME = "left_arg"
LeftDataT = TypeVar("LeftDataT")
RightDataT = TypeVar("RightDataT")
_NumericArgumentInplaceErrorMessage = "Cannot inplace the numeric argument {}"
Numeric = (float, int)

RegisterOrInt = Union[int, RegisterUserInput]


class ArgToInplace(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class BinaryOpParams(
    ArithmeticOperationParams, GenericModel, Generic[LeftDataT, RightDataT]
):
    left_arg: LeftDataT
    right_arg: RightDataT

    @pydantic.validator("left_arg")
    def _set_left_arg_name(cls, left_arg: LeftDataT) -> LeftDataT:
        if isinstance(left_arg, RegisterUserInput) and not left_arg.name:
            return left_arg.revalued(name=_DEFAULT_LEFT_ARG_NAME)  # type: ignore[return-value]
        return left_arg

    @pydantic.validator("right_arg")
    def _set_right_arg_name(cls, right_arg: RightDataT) -> RightDataT:
        if isinstance(right_arg, RegisterUserInput) and not right_arg.name:
            return right_arg.revalued(name=_DEFAULT_RIGHT_ARG_NAME)  # type: ignore[return-value]
        return right_arg

    @pydantic.root_validator(pre=True)
    def _validate_one_is_register(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        left_arg = values.get("left_arg")
        right_arg = values.get("right_arg")
        if isinstance(left_arg, Numeric) and isinstance(right_arg, Numeric):
            raise ValueError("One argument must be a register")
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

    def get_params_inplace_options(self) -> Iterable[BinaryOpParams]:
        return ()


class InplacableBinaryOpParams(
    BinaryOpParams[LeftDataT, RightDataT], Generic[LeftDataT, RightDataT]
):
    inplace_arg: Optional[ArgToInplace] = None

    @pydantic.root_validator(pre=True)
    def _validate_inplace_arg(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        left_arg = values.get("left_arg")
        right_arg = values.get("right_arg")
        inplace_arg: Optional[ArgToInplace] = values.get("inplace_arg")
        if inplace_arg == ArgToInplace.RIGHT and isinstance(right_arg, Numeric):
            raise ValueError(_NumericArgumentInplaceErrorMessage.format(right_arg))
        elif inplace_arg == ArgToInplace.LEFT and isinstance(left_arg, Numeric):
            raise ValueError(_NumericArgumentInplaceErrorMessage.format(left_arg))
        return values

    def _create_ios(self) -> None:
        BinaryOpParams._create_ios(self)
        garbage_size = self.garbage_output_size()
        if garbage_size > 0:
            self._outputs[self.garbage_output_name] = RegisterUserInput(
                name=self.garbage_output_name, size=garbage_size
            )
        if self.inplace_arg is None:
            return
        inplace_arg_name = (
            self.left_arg.name  # type: ignore[attr-defined]
            if self.inplace_arg == ArgToInplace.LEFT
            else self.right_arg.name  # type: ignore[attr-defined]
        )
        self._outputs.pop(inplace_arg_name)

        self._set_inplace_zero_inputs(inplace_arg_name, garbage_size)

    def _set_inplace_zero_inputs(
        self, inplace_arg_name: str, garbage_size: int
    ) -> None:
        self._zero_inputs.pop(get_zero_input_name(self.output_name))

        num_extra_qubits = self.outputs[self.output_name].size - (
            self._inputs[inplace_arg_name].size - garbage_size
        )
        if num_extra_qubits > 0:
            zero_input_name = get_zero_input_name(self.output_name)
            self._zero_inputs[zero_input_name] = RegisterUserInput(
                name=zero_input_name, size=num_extra_qubits
            )

    def is_inplaced(self) -> bool:
        return self.inplace_arg is not None

    def garbage_output_size(self) -> pydantic.NonNegativeInt:
        if self.inplace_arg is None:
            return 0
        arg = self.left_arg if self.inplace_arg == ArgToInplace.LEFT else self.right_arg
        return max(0, arg.integer_part_size - self.result_register.integer_part_size)  # type: ignore[attr-defined]

    def _carried_arguments(self) -> Tuple[Optional[LeftDataT], Optional[RightDataT]]:
        if self.inplace_arg == ArgToInplace.RIGHT and isinstance(
            self.left_arg, RegisterUserInput
        ):
            return self.left_arg, None  # type: ignore[return-value]
        elif self.inplace_arg == ArgToInplace.LEFT and isinstance(
            self.right_arg, RegisterUserInput
        ):
            return None, self.right_arg  # type: ignore[return-value]
        elif self.inplace_arg is not None:
            return None, None
        return self.left_arg, self.right_arg

    def _get_binary_op_inplace_options(self) -> Iterable[ArgToInplace]:
        right_arg = getattr(self, "right_arg", None)
        left_arg = getattr(self, "left_arg", None)
        if isinstance(right_arg, RegisterUserInput) and isinstance(
            left_arg, RegisterUserInput
        ):
            if left_arg.size > right_arg.size:
                yield ArgToInplace.LEFT
                yield ArgToInplace.RIGHT
            else:
                yield ArgToInplace.RIGHT
                yield ArgToInplace.LEFT
        elif isinstance(right_arg, RegisterUserInput):
            yield ArgToInplace.RIGHT
        elif isinstance(left_arg, RegisterUserInput):
            yield ArgToInplace.LEFT

    def get_params_inplace_options(self) -> Iterable[InplacableBinaryOpParams]:
        params_kwargs = self.copy().__dict__
        for inplace_arg in self._get_binary_op_inplace_options():
            params_kwargs["inplace_arg"] = inplace_arg
            yield self.__class__(**params_kwargs)


class BinaryOpWithIntInputs(BinaryOpParams[RegisterOrInt, RegisterOrInt]):
    @pydantic.root_validator()
    def validate_int_registers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        left_arg = values.get("left_arg")
        is_left_arg_float_register = (
            isinstance(left_arg, RegisterUserInput) and left_arg.fraction_places > 0
        )
        right_arg = values.get("right_arg")
        is_right_arg_float_register = (
            isinstance(right_arg, RegisterUserInput) and right_arg.fraction_places > 0
        )
        if is_left_arg_float_register or is_right_arg_float_register:
            raise ValueError("Boolean operation are defined only for integer")
        return values

    @staticmethod
    def _is_signed(arg: Union[int, RegisterUserInput]) -> bool:
        if isinstance(arg, RegisterUserInput):
            return arg.is_signed
        return arg < 0

    def _get_result_register(self) -> RegisterUserInput:
        required_size = self._aligned_inputs_max_length()
        is_signed = self._include_sign and (
            self._is_signed(self.left_arg) or self._is_signed(self.right_arg)
        )
        return RegisterUserInput(
            size=self.output_size or required_size,
            name=self.output_name,
            is_signed=is_signed,
        )

    def _aligned_inputs_max_length(self) -> int:
        left_signed: bool = argument_utils.is_signed(self.left_arg)
        right_signed: bool = argument_utils.is_signed(self.right_arg)
        return max(
            argument_utils.integer_part_size(self.right_arg)
            + int(left_signed and not right_signed),
            argument_utils.integer_part_size(self.left_arg)
            + int(right_signed and not left_signed),
        )


class BinaryOpWithFloatInputs(BinaryOpParams[RegisterOrConst, RegisterOrConst]):
    pass


class BitwiseAnd(BinaryOpWithIntInputs):
    output_name = "bitwise_and"


class BitwiseOr(BinaryOpWithIntInputs):
    output_name = "bitwise_or"


# TODO: fix diamond inheritance
class BitwiseXor(
    BinaryOpWithIntInputs, InplacableBinaryOpParams[RegisterOrInt, RegisterOrInt]
):
    output_name = "bitwise_xor"


class Adder(InplacableBinaryOpParams[RegisterOrConst, RegisterOrConst]):
    output_name = "sum"

    def _get_result_register(self) -> RegisterUserInput:
        lb = argument_utils.lower_bound(self.left_arg) + argument_utils.lower_bound(
            self.right_arg
        )
        ub = argument_utils.upper_bound(self.left_arg) + argument_utils.upper_bound(
            self.right_arg
        )
        integer_part_size = number_utils.bounds_to_integer_part_size(lb, ub)
        fraction_places = max(
            argument_utils.fraction_places(self.left_arg),
            argument_utils.fraction_places(self.right_arg),
        )
        size_needed = integer_part_size + fraction_places
        return RegisterUserInput(
            size=self.output_size or size_needed,
            name=self.output_name,
            fraction_places=fraction_places,
            is_signed=self._include_sign and lb < 0,
            bounds=(lb, ub) if self._include_sign else None,
        )


class Subtractor(InplacableBinaryOpParams[RegisterOrConst, RegisterOrConst]):
    output_name = "difference"

    def _get_result_register(self) -> RegisterUserInput:
        bounds = (
            argument_utils.lower_bound(self.left_arg)
            - argument_utils.upper_bound(self.right_arg),
            argument_utils.upper_bound(self.left_arg)
            - argument_utils.lower_bound(self.right_arg),
        )
        integer_part_size = number_utils.bounds_to_integer_part_size(*bounds)
        fraction_places = max(
            argument_utils.fraction_places(self.left_arg),
            argument_utils.fraction_places(self.right_arg),
        )
        size_needed = integer_part_size + fraction_places
        return RegisterUserInput(
            size=self.output_size or size_needed,
            name=self.output_name,
            fraction_places=fraction_places,
            is_signed=self._include_sign and min(bounds) < 0,
            bounds=self._legal_bounds(bounds),
        )

    def garbage_output_size(self) -> pydantic.NonNegativeInt:
        if not isinstance(self.right_arg, RegisterUserInput):
            adder_params = Adder(
                left_arg=self.left_arg,
                right_arg=-self.right_arg,
                output_size=self.output_size,
                inplace_arg=self.inplace_arg,
            )
            return adder_params.garbage_output_size()

        negation_params = Negation(
            arg=self.right_arg,
            output_size=self.negation_output_size,
            inplace=self.should_inplace_negation,
        )
        negation_result = negation_params.result_register
        if self.output_size is None and max(self.right_arg.bounds) > 0:
            negation_result = negation_result.revalued(
                is_signed=True,
                bounds=(-max(self.right_arg.bounds), -min(self.right_arg.bounds)),
            )
        adder_params = Adder(
            left_arg=self.left_arg,
            right_arg=negation_result,
            output_size=self.output_size,
            inplace_arg=self.arg_to_inplace_adder,
        )
        negation_garbage_size = negation_params.garbage_output_size() * int(
            not self.should_uncompute_negation
        )
        return adder_params.garbage_output_size() + negation_garbage_size

    @property
    def should_uncompute_negation(self) -> bool:
        return self.inplace_arg == ArgToInplace.LEFT

    def _expected_negation_output_size(self) -> int:
        return argument_utils.fraction_places(self.right_arg) + min(
            self.result_register.integer_part_size,
            number_utils.bounds_to_integer_part_size(
                *(-bound for bound in argument_utils.bounds(self.right_arg))
            ),
        )

    @property
    def negation_output_size(self) -> int:
        if self.output_size:
            return min(self.output_size, self._expected_negation_output_size())
        return self._expected_negation_output_size()

    @property
    def should_inplace_negation(self) -> bool:
        return self.inplace_arg is not None

    @property
    def arg_to_inplace_adder(self) -> ArgToInplace:
        return (
            ArgToInplace.LEFT
            if self.inplace_arg == ArgToInplace.LEFT
            else ArgToInplace.RIGHT
        )


class Multiplier(BinaryOpWithFloatInputs):
    output_name = "product"

    def _get_result_register(self) -> RegisterUserInput:
        fraction_places = argument_utils.fraction_places(
            self.left_arg
        ) + argument_utils.fraction_places(self.right_arg)
        extremal_values = [
            left * right
            for left in argument_utils.bounds(self.left_arg)
            for right in argument_utils.bounds(self.right_arg)
        ]
        bounds = (min(extremal_values), max(extremal_values))
        largest_bound = max(bounds, key=abs)
        integer_places = int(largest_bound).bit_length() + int(largest_bound < 0)
        extra_sign_bit = int(
            argument_utils.is_signed(self.left_arg)
            and argument_utils.is_signed(self.right_arg)
            and largest_bound > 0
        )
        return RegisterUserInput(
            size=self.output_size
            or max(1, integer_places + fraction_places + extra_sign_bit),
            name=self.output_name,
            fraction_places=fraction_places,
            is_signed=self._include_sign and min(bounds) < 0,
            bounds=self._legal_bounds(bounds),
        )


class Comparator(BinaryOpWithFloatInputs):
    output_size: Literal[1] = 1

    def _get_result_register(self) -> RegisterUserInput:
        return RegisterUserInput(name=self.output_name, size=1)


class Equal(Comparator):
    output_name = "is_equal"


class NotEqual(Comparator):
    output_name = "is_not_equal"


class GreaterThan(Comparator):
    output_name = "is_greater_than"


class GreaterEqual(Comparator):
    output_name = "is_greater_equal"


class LessThan(Comparator):
    output_name = "is_less_than"


class LessEqual(Comparator):
    output_name = "is_less_equal"


class LShift(InplacableBinaryOpParams[RegisterUserInput, pydantic.NonNegativeInt]):
    output_name = "left_shifted"
    inplace_arg: Optional[ArgToInplace] = ArgToInplace.LEFT

    def _get_result_register(self) -> RegisterUserInput:
        new_fraction_places = max(self.left_arg.fraction_places - self.right_arg, 0)
        new_integer_part_size = self.left_arg.integer_part_size + self.right_arg
        required_size = new_integer_part_size + new_fraction_places
        return RegisterUserInput(
            size=self.output_size or required_size,
            name=self.output_name,
            is_signed=self._include_sign and self.left_arg.is_signed,
            fraction_places=new_fraction_places,
        )


class RShift(InplacableBinaryOpParams[RegisterUserInput, pydantic.NonNegativeInt]):
    output_name = "right_shifted"
    inplace_arg: Optional[ArgToInplace] = ArgToInplace.LEFT

    def garbage_output_size(self) -> pydantic.NonNegativeInt:
        return min(self.left_arg.size, self.right_arg) * int(
            self.inplace_arg is not None
        )

    def _get_result_register(self) -> RegisterUserInput:
        min_size: int = max(self.left_arg.size - self.right_arg, 1)
        new_fraction_places = self.left_arg.fraction_places * int(
            self.left_arg.is_signed or self.right_arg < self.left_arg.size
        )
        required_size = max(min_size, new_fraction_places)
        return RegisterUserInput(
            size=self.output_size or required_size,
            name=self.output_name,
            is_signed=self._include_sign and self.left_arg.is_signed,
            fraction_places=new_fraction_places,
        )


class CyclicShift(InplacableBinaryOpParams[RegisterUserInput, int]):
    output_name = "cyclic_shifted"
    inplace_arg: Optional[ArgToInplace] = ArgToInplace.LEFT

    def _get_result_register(self) -> RegisterUserInput:
        return RegisterUserInput(
            name=self.output_name,
            size=self.left_arg.size,
            is_signed=self._include_sign and self.left_arg.is_signed,
            fraction_places=self.left_arg.fraction_places,
        )


class Modulo(InplacableBinaryOpParams[RegisterUserInput, int]):
    output_name = "modulus"
    inplace_arg: Optional[ArgToInplace] = ArgToInplace.LEFT

    @pydantic.validator("left_arg")
    def _validate_left_arg_is_integer(
        cls, left_arg: RegisterUserInput
    ) -> RegisterUserInput:
        assert left_arg.fraction_places == 0, "left argument is not an integer"
        return left_arg

    @pydantic.validator("right_arg")
    def _validate_right_arg_is_a_power_of_two(
        cls, right_arg: int, values: Dict[str, Any]
    ) -> int:
        repr_qubits_float = math.log2(right_arg)
        repr_qubits = round(repr_qubits_float)
        assert (
            abs(repr_qubits - repr_qubits_float) < 10**-8
        ), NOT_POWER_OF_TWO_ERROR_MSG
        output_size = values.get("output_size")
        if output_size is not None:
            repr_qubits = min(repr_qubits, output_size)
        values["output_size"] = None
        return 2 ** (repr_qubits)

    @property
    def result_size(self) -> int:
        return round(math.log2(self.right_arg))

    def _get_result_register(self) -> RegisterUserInput:
        return RegisterUserInput(
            name=self.output_name,
            size=self.result_size,
            is_signed=False,
            fraction_places=0,
        )
