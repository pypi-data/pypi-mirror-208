from typing import Any, Dict, List, Mapping, Optional

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import IOName, PortDirection
from classiq.interface.generator.functions.port_declaration import PortDeclaration
from classiq.interface.generator.functions.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)
from classiq.interface.generator.parameters import ParameterFloatType, ParameterMap
from classiq.interface.generator.quantum_function_call import (
    QuantumFunctionCall,
    WireDict,
    WireName,
)
from classiq.interface.generator.validations import flow_graph
from classiq.interface.helpers.validation_helpers import is_list_unique

LOGIC_FLOW_DUPLICATE_NAME_ERROR_MSG = (
    "Cannot have multiple function calls with the same name"
)


def update_logic_flow(
    logic_flow: List[QuantumFunctionCall],
    function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    if not is_list_unique([call.name for call in logic_flow]):
        raise ValueError(LOGIC_FLOW_DUPLICATE_NAME_ERROR_MSG)

    for fc in logic_flow:
        fc.check_and_update(function_dict)


class IOData(pydantic.BaseModel):
    wire: WireName = pydantic.Field(
        description="The name of the wire of the PortDirection data."
    )
    reg: RegisterUserInput = pydantic.Field(
        description="The register information about the PortDirection data."
    )

    class Config:
        frozen = True


class NativeFunctionDefinition(QuantumFunctionDeclaration):
    """
    Facilitates the creation of a user-defined composite function

    This class sets extra to forbid so that it can be used in a Union and not "steal"
    objects from other classes.
    """

    parameters: List[ParameterMap] = pydantic.Field(
        default_factory=list,
        description="The parameters (name and mapped parameter or value) of the function",
    )

    input_ports_wiring: Dict[IOName, WireName] = pydantic.Field(
        description="The mapping between the functions input ports, to inner wires",
        default_factory=dict,
    )

    output_ports_wiring: Dict[IOName, WireName] = pydantic.Field(
        description="The mapping between the functions output ports, to inner wires",
        default_factory=dict,
    )

    logic_flow: List[QuantumFunctionCall] = pydantic.Field(
        default_factory=list, description="List of function calls to perform."
    )

    @pydantic.validator("logic_flow")
    def _validate_logic_flow(
        cls, logic_flow: List[QuantumFunctionCall], values: Dict[str, Any]
    ) -> List[QuantumFunctionCall]:
        function_call_names = {call.name for call in logic_flow}
        if len(function_call_names) != len(logic_flow):
            raise ValueError(LOGIC_FLOW_DUPLICATE_NAME_ERROR_MSG)

        inputs = values.get("input_ports_wiring", dict())
        outputs = values.get("output_ports_wiring", dict())

        flow_graph.validate_legal_wiring(
            logic_flow,
            flow_input_names=list(inputs.values()),
            flow_output_names=list(outputs.values()),
        )
        flow_graph.validate_acyclic_logic_flow(
            logic_flow,
            flow_input_names=list(inputs.values()),
            flow_output_names=list(outputs.values()),
        )

        return logic_flow

    def update_logic_flow(
        self, function_dict: Mapping[str, QuantumFunctionDeclaration]
    ) -> None:
        update_logic_flow(
            self.logic_flow, {**function_dict, **self.operand_declarations}
        )

    @property
    def inputs_to_wires(self) -> WireDict:
        return self.input_ports_wiring

    @property
    def outputs_to_wires(self) -> WireDict:
        return self.output_ports_wiring

    @property
    def parameters_mapping(self) -> Dict[str, ParameterFloatType]:
        return {
            parameter.original: parameter.new_parameter for parameter in self.parameters
        }

    @classmethod
    def _validate_direction_ports(
        cls,
        port_declarations: Dict[IOName, PortDeclaration],
        directions_external_port_wiring: WireDict,
        direction: PortDirection,
    ) -> None:
        for io_name in directions_external_port_wiring:
            if (
                io_name not in port_declarations
                or not port_declarations[io_name].direction == direction
            ):
                raise ValueError(
                    f"The wired {direction} port {io_name!r} is not declared."
                )

    @pydantic.root_validator
    def validate_ports(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        port_declarations: Optional[Dict[IOName, PortDeclaration]] = values.get(
            "port_declarations"
        )
        if port_declarations is None:
            return values
        cls._validate_direction_ports(
            port_declarations,
            values.get("input_ports_wiring", dict()),
            PortDirection.Input,
        )
        cls._validate_direction_ports(
            port_declarations,
            values.get("output_ports_wiring", dict()),
            PortDirection.Output,
        )
        return values
