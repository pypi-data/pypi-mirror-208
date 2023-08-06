from typing import Any, Dict, Iterable, List, Set, Tuple, Union

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import (
    FunctionParams,
    parse_function_params_values,
)
from classiq.interface.generator.state_preparation import StatePreparation
from classiq.interface.generator.user_defined_function_params import CustomFunction

from classiq.exceptions import ClassiqValueError

GroverStatePreparation = Union[StatePreparation, CustomFunction]


class GroverDiffuser(FunctionParams):
    variables: List[RegisterUserInput]
    state_preparation: str = pydantic.Field(
        default="", description="State preparation function"
    )
    state_preparation_params: GroverStatePreparation = pydantic.Field(
        description="State preparation function parameters"
    )

    def _create_ios(self) -> None:
        self._inputs = {reg.name: reg for reg in self.variables}
        self._outputs = {reg.name: reg for reg in self.variables}

    @pydantic.root_validator(pre=True)
    def _validate_state_preparation_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(
            values.get("state_preparation_params"), CustomFunction
        ) and not values.get("state_preparation"):
            raise ClassiqValueError(
                "Must receive the function name from the `state_preparation` field for user defined functions"
            )
        return values

    @pydantic.root_validator(pre=True)
    def _parse_state_preparation(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        parse_function_params_values(
            values=values,
            params_key="state_preparation_params",
            discriminator_key="state_preparation",
            param_classes={StatePreparation, CustomFunction},
            default_parser_class=CustomFunction,
        )
        return values

    @pydantic.validator("variables")
    def _validate_variables(
        cls, variables: List[RegisterUserInput]
    ) -> List[RegisterUserInput]:
        names = {reg.name for reg in variables}
        assert len(variables) == len(names), "Repeating names not allowed"
        return variables

    @pydantic.validator("state_preparation_params")
    def _validate_state_preparation(
        cls, state_preparation_params: GroverStatePreparation, values: Dict[str, Any]
    ) -> GroverStatePreparation:
        variables = values.get("variables", list())
        sp_inputs = state_preparation_params.inputs_full(assign_zero_ios=True)
        sp_outputs = state_preparation_params.outputs
        if len(sp_inputs) == 1 and len(sp_outputs) == 1:
            var_size = sum(reg.size for reg in variables)
            assert (
                state_preparation_params.num_input_qubits(assign_zero_ios=True)
                == var_size
            )
            assert state_preparation_params.num_output_qubits == var_size
        else:
            variable_names_and_sizes = cls._names_and_sizes(variables)
            assert cls._names_and_sizes(sp_inputs.values()) == variable_names_and_sizes
            assert cls._names_and_sizes(sp_outputs.values()) == variable_names_and_sizes
        return state_preparation_params

    @staticmethod
    def _names_and_sizes(
        transputs: Iterable[RegisterUserInput],
    ) -> Set[Tuple[str, int]]:
        return {(reg.name, reg.size) for reg in transputs}
