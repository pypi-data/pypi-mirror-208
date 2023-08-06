from typing import Any, Dict, Optional

import pydantic

from classiq.interface.generator.function_params import (
    FunctionParams,
    FunctionParamsDiscriminator,
    parse_function_params,
)
from classiq.interface.generator.grover_diffuser import (
    GroverDiffuser,
    GroverStatePreparation,
)
from classiq.interface.generator.oracles import ArithmeticOracle, OracleABC
from classiq.interface.generator.oracles.oracle_function_param_list import (
    oracle_function_param_library,
)
from classiq.interface.generator.range_types import NonNegativeFloatRange
from classiq.interface.generator.state_preparation import Metrics, StatePreparation

_DEFAULT_ORACLE_DISCRIMINATOR: FunctionParamsDiscriminator = (
    ArithmeticOracle.discriminator()
)


class GroverOperator(FunctionParams):
    oracle: str = pydantic.Field(
        default=_DEFAULT_ORACLE_DISCRIMINATOR, description="Oracle function"
    )
    oracle_params: OracleABC = pydantic.Field(description="Oracle function parameters")
    state_preparation: str = pydantic.Field(
        default="", description="State preparation function"
    )
    state_preparation_params: GroverStatePreparation = pydantic.Field(
        default=None, description="State preparation function parameters"
    )

    def _create_ios(self) -> None:
        self._inputs = {**self.oracle_params.inputs}
        self._outputs = {**self.oracle_params.outputs}

    @pydantic.root_validator(pre=True)
    def _parse_oracle(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        oracle_params = values.get("oracle_params")
        if isinstance(oracle_params, dict):
            values["oracle_params"] = parse_function_params(
                params=oracle_params,
                discriminator=values.get("oracle", _DEFAULT_ORACLE_DISCRIMINATOR),
                param_classes=oracle_function_param_library.param_list,
                no_discriminator_error=ValueError("Invalid oracle name"),
                bad_function_error=ValueError("Invalid oracle params"),
            )
        elif isinstance(oracle_params, FunctionParams):
            values["oracle"] = oracle_params.discriminator()
        else:
            raise ValueError("Invalid oracle params")
        return values

    @pydantic.validator("state_preparation_params", always=True)
    def _validate_state_preparation(
        cls,
        state_preparation_params: Optional[GroverStatePreparation],
        values: Dict[str, Any],
    ) -> GroverStatePreparation:
        oracle = values.get("oracle_params")
        assert oracle is not None, "Must receive an oracle"
        state_preparation_params = (
            state_preparation_params
            or cls._default_state_preparation_params(
                num_qubits=oracle.num_input_qubits(assign_zero_ios=False)
            )
        )
        assert GroverDiffuser(
            state_preparation_params=state_preparation_params,
            state_preparation=values.get("state_preparation", ""),
            variables=oracle.variables(),
        ), "Cannot construct a GroverDiffuser"
        return state_preparation_params

    @staticmethod
    def _default_state_preparation_params(num_qubits: int) -> StatePreparation:
        num_states: int = 2**num_qubits
        return StatePreparation(
            probabilities=[1.0 / float(num_states)] * num_states,
            error_metric={
                Metrics.L2: NonNegativeFloatRange(lower_bound=0.0, upper_bound=0.0)
            },
        )

    def get_diffuser(self) -> GroverDiffuser:
        return GroverDiffuser(
            variables=self.oracle_params.variables(),
            state_preparation=self.state_preparation,
            state_preparation_params=self.state_preparation_params,
        )
