from typing import Dict, List, Mapping, Set

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import ArithmeticIODict, FunctionParams
from classiq.interface.generator.parameters import ParameterFloatType, ParameterMap


class CustomFunction(FunctionParams):
    """
    A user-defined custom function parameters object.
    """

    _name: str = pydantic.PrivateAttr(default="")

    parameters: List[ParameterMap] = pydantic.Field(
        default_factory=list,
        description="The parameters used inside the custom function and their mapping.",
    )

    input_decls: ArithmeticIODict = pydantic.Field(
        default_factory=dict,
        description="A mapping from the inputs names to the registers information. should be identical to the register defined in the function creation.",
    )

    output_decls: ArithmeticIODict = pydantic.Field(
        default_factory=dict,
        description="A mapping from the outputs names to the registers information. should be identical to the register defined in the function creation.",
    )

    def _create_ios(self) -> None:
        self._inputs = self.input_decls
        self._outputs = self.output_decls

    def generate_ios(
        self,
        inputs: Mapping[str, RegisterUserInput],
        outputs: Mapping[str, RegisterUserInput],
    ) -> None:
        self._inputs = dict(inputs)
        self._outputs = dict(outputs)

    @property
    def _symbols(self) -> Set[str]:
        return {new for new in self.parameters_mapping.values() if isinstance(new, str)}

    @property
    def parameters_mapping(self) -> Dict[str, ParameterFloatType]:
        return {
            parameter.original: parameter.new_parameter for parameter in self.parameters
        }

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.name))
