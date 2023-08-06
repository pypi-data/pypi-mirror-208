from typing import Any, Dict, Optional, Tuple

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.exponentiation import Exponentiation
from classiq.interface.generator.function_param_list_without_self_reference import (
    function_param_library_without_self_reference,
)
from classiq.interface.generator.function_params import (
    DEFAULT_ZERO_NAME,
    FunctionParams,
    IOName,
    parse_function_params_values,
)
from classiq.interface.generator.parameters import ParameterFloatType
from classiq.interface.generator.user_defined_function_params import CustomFunction

from classiq.exceptions import (
    ClassiqMismatchIOsError,
    ClassiqNotImplementedError,
    ClassiqValueError,
)

PHASE_ESTIMATION_DEFAULT_OUTPUT_NAME = "PHASE_ESTIMATION"
CUSTOM_FUNCTIONS_IO_MISMATCH_ERROR = (
    "Custom function provided to the QPE has different input and output names."
)


class ExponentiationScaling(pydantic.BaseModel):
    """
    Details of exponentiation scaling for phase estimation.
    """

    max_depth: pydantic.PositiveInt = pydantic.Field(
        description="The max_depth of the smallest exponentiation",
    )
    max_depth_scaling_factor: pydantic.NonNegativeFloat = pydantic.Field(
        default=2.0,
        description="The scaling factor of the exponentiation max_depth; defaults to 2.",
    )

    class Config:
        frozen = True


class ExponentiationSpecification(pydantic.BaseModel):
    """
    Specifications of individual Exponentiation details for each qubit; only valid if Exponentiation is given as unitary_params for PhaseEstimation.
    This sets the optimization to ExponentiationOptimization.MINIMIZE_ERROR and overrides the max_depth constraints.
    """

    scaling: Optional[ExponentiationScaling] = pydantic.Field(
        default=None,
        description="The scaling of the exponentiation functions.",
    )
    max_depths: Optional[Tuple[pydantic.NonNegativeInt, ...]] = pydantic.Field(
        default=None,
        description="The max_depth of each exponentiation function; overrides scaling.",
    )

    class Config:
        frozen = True

    @pydantic.root_validator
    def _validate_exponentiation_specification(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        if values.get("scaling") is None and values.get("max_depths") is None:
            raise ValueError("At least one specification must be provided.")
        return values


class PhaseEstimation(FunctionParams):
    """
    Quantum phase estimation of a given unitary function.
    """

    size: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits storing the estimated phase."
    )
    unitary: str = pydantic.Field(
        description="The unitary function for phase estimation.",
    )
    unitary_params: FunctionParams = pydantic.Field(
        description="The unitary function parameters."
    )
    exponentiation_specification: Optional[
        ExponentiationSpecification
    ] = pydantic.Field(
        default=None,
        description="The specifications for phase estimation of exponentiation functions.",
    )

    _output_name: IOName = pydantic.PrivateAttr(
        default=PHASE_ESTIMATION_DEFAULT_OUTPUT_NAME
    )

    @property
    def output_name(self) -> str:
        return self._output_name

    def _create_ios(self) -> None:
        self._inputs = {**self.unitary_params.inputs}
        self._outputs = {**self.unitary_params.outputs}
        self._outputs[self._output_name] = RegisterUserInput(
            name=self._output_name, size=self.size
        )
        self._create_zero_input_registers({DEFAULT_ZERO_NAME: self.size})

    def _assign_parameters(
        self, parameters_dict: Dict[str, ParameterFloatType]
    ) -> FunctionParams:
        if self.unitary_params._symbols:
            raise ClassiqNotImplementedError(
                "assigning parameters to a parameter of a QPE function is not implemented"
            )
        return self

    @pydantic.root_validator(pre=True)
    def _validate_composite_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values.get("unitary_params"), CustomFunction) and not values.get(
            "unitary"
        ):
            raise ClassiqValueError(
                "`PhaseEstimation` of a user define function (`CustomFunction`) must receive the function name from the `unitary` field"
            )
        return values

    @pydantic.root_validator(pre=True)
    def _parse_function_params(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        parse_function_params_values(
            values=values,
            params_key="unitary_params",
            discriminator_key="unitary",
            param_classes=function_param_library_without_self_reference.param_list,
            default_parser_class=CustomFunction,
        )
        return values

    @pydantic.validator("unitary_params")
    def _validate_unitary_params(cls, unitary_params: FunctionParams) -> FunctionParams:
        if not unitary_params.is_powerable():
            if isinstance(unitary_params, CustomFunction):
                raise ClassiqMismatchIOsError(CUSTOM_FUNCTIONS_IO_MISMATCH_ERROR)
            raise ValueError(
                f"Phase estimation of {unitary_params.discriminator()} is currently not supported."
            )
        return unitary_params

    @pydantic.validator("exponentiation_specification")
    def _validate_exponentiation_specification(
        cls,
        exponentiation_specification: Optional[ExponentiationSpecification],
        values: Dict[str, Any],
    ) -> Optional[ExponentiationSpecification]:
        if exponentiation_specification is None:
            return exponentiation_specification
        unitary_params = values.get("unitary_params")
        if not isinstance(unitary_params, Exponentiation):
            raise ValueError(
                "exponentiation_specification is only valid for Exponentiation unitary_params."
            )
        if exponentiation_specification.max_depths is not None and len(
            exponentiation_specification.max_depths
        ) != values.get("size"):
            raise ValueError("Length of max_depths must match the provided size.")
        return exponentiation_specification
