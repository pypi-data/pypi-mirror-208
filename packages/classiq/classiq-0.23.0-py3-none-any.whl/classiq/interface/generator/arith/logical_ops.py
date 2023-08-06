from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import pydantic

from classiq.interface.generator.arith.argument_utils import RegisterOrConst
from classiq.interface.generator.arith.arithmetic_operations import (
    ArithmeticOperationParams,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import get_zero_input_name

_DEFAULT_ARG_NAME: str = "in_arg"


class LogicalOps(ArithmeticOperationParams):
    args: List[RegisterOrConst]
    target: Optional[RegisterUserInput]
    _should_invert_node_list: List[str] = pydantic.PrivateAttr(default_factory=list)

    def update_should_invert_node_list(self, invert_args: List[str]) -> None:
        self._should_invert_node_list.extend(invert_args)

    @pydantic.validator("output_size")
    def _validate_output_size(cls, output_size: Optional[int]) -> int:
        if output_size is not None and output_size != 1:
            raise ValueError("logical operation output size must be 1")
        return 1

    @pydantic.validator("args")
    def _validate_inputs_sizes(
        cls, arguments: List[RegisterOrConst]
    ) -> List[RegisterOrConst]:
        for arg in arguments:
            if isinstance(arg, RegisterUserInput) and (
                arg.size != 1 or arg.fraction_places != 0
            ):
                raise ValueError(
                    f"All inputs to logical and must be of size 1 | {arg.name}"
                )
        return arguments

    @pydantic.validator("args")
    def _set_inputs_names(
        cls, arguments: List[RegisterOrConst]
    ) -> List[RegisterOrConst]:
        renamed_arguments: List[RegisterOrConst] = list()
        for idx, arg in enumerate(arguments):
            if isinstance(arg, RegisterUserInput) and not arg.name:
                renamed_arguments.append(arg.revalued(name=f"{_DEFAULT_ARG_NAME}{idx}"))
            else:
                renamed_arguments.append(arg)
        return renamed_arguments

    @pydantic.validator("target", always=True)
    def _validate_target(
        cls, target: Optional[RegisterUserInput], values: Dict[str, Any]
    ) -> Optional[RegisterUserInput]:
        if target is None:
            return None
        if not target.is_boolean_register:
            raise ValueError("Register doesn't match a boolean variable")
        output_name = values.get("output_name", "")
        return target if target.name else target.revalued(name=output_name)

    def _get_result_register(self) -> RegisterUserInput:
        return RegisterUserInput(size=1, name=self.output_name)

    def _create_ios(self) -> None:
        args = {
            arg.name: arg for arg in self.args if isinstance(arg, RegisterUserInput)
        }
        self._inputs = {**args}
        self._outputs = {**args, self.output_name: self.result_register}
        if self.target:
            self._inputs[self.target.name] = self.target
        else:
            zero_input_name = get_zero_input_name(self.output_name)
            self._create_zero_input_registers(
                {zero_input_name: self.result_register.size}
            )

    def is_inplaced(self) -> bool:
        return False

    def get_params_inplace_options(self) -> Iterable[LogicalOps]:
        return ()

    class Config:
        arbitrary_types_allowed = True


class LogicalAnd(LogicalOps):
    output_name = "and"
    pass


class LogicalOr(LogicalOps):
    output_name = "or"
    pass
