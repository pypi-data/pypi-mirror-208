from typing import Any, Dict

import pydantic

from classiq.interface.generator.function_params import parse_function_params_values
from classiq.interface.generator.oracles.oracle_abc import (
    ArithmeticIODict,
    OracleABC,
    VariableBinResultMap,
    VariableTypedResultMap,
)
from classiq.interface.generator.user_defined_function_params import CustomFunction

QubitState = str


class CustomOracle(OracleABC[QubitState]):
    custom_oracle: str = pydantic.Field(description="Oracle function")
    custom_oracle_params: CustomFunction = pydantic.Field(
        description="Oracle function parameters"
    )

    @pydantic.root_validator(pre=True)
    def _parse_oracle(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        parse_function_params_values(
            values=values,
            params_key="custom_oracle_params",
            discriminator_key="custom_oracle",
            param_classes={CustomFunction},
            default_parser_class=CustomFunction,
        )
        return values

    @pydantic.validator("custom_oracle_params")
    def _validate_names_match_oracle(
        cls, custom_oracle_params: CustomFunction
    ) -> CustomFunction:
        if set(custom_oracle_params.input_decls.keys()) != set(
            custom_oracle_params.output_decls.keys()
        ):
            raise ValueError("Oracle IO names must be identical")
        if any(
            custom_oracle_params.output_decls[name].size != input_decl.size
            for name, input_decl in custom_oracle_params.input_decls.items()
        ):
            raise ValueError("Oracle IO sizes must be identical")
        return custom_oracle_params

    def _get_register_transputs(self) -> ArithmeticIODict:
        return {
            name: reg.revalued(name=name)
            for name, reg in self.custom_oracle_params.input_decls.items()
        }

    def binary_result_to_typed_result(
        self, bin_result: VariableBinResultMap
    ) -> VariableTypedResultMap[QubitState]:
        return bin_result

    def is_good_result(
        self, problem_result: VariableTypedResultMap[QubitState]
    ) -> bool:
        return True
