from typing import Any, ClassVar, Dict, Mapping, Set

import pydantic

from classiq.interface.generator.function_params import (
    ArithmeticIODict,
    IOName,
    PortDirection,
)
from classiq.interface.generator.functions.function_declaration import (
    UNRESOLVED_SIZE,
    FunctionDeclaration,
    OperandDeclaration,
)
from classiq.interface.generator.functions.port_declaration import PortDeclaration

from classiq import RegisterUserInput


class QuantumFunctionDeclaration(FunctionDeclaration):
    """
    Facilitates the creation of a common quantum function interface object.
    """

    port_declarations: Dict[IOName, PortDeclaration] = pydantic.Field(
        description="The input and output ports of the function.",
        default_factory=dict,
    )

    operand_declarations: Mapping[str, "QuantumOperandDeclaration"] = pydantic.Field(
        description="The expected interface of the quantum function operands",
        default_factory=dict,
    )

    BUILTIN_FUNCTION_DECLARATIONS: ClassVar[
        Dict[str, "QuantumFunctionDeclaration"]
    ] = {}

    @property
    def input_set(self) -> Set[IOName]:
        return set(self.inputs.keys())

    @property
    def output_set(self) -> Set[IOName]:
        return set(self.outputs.keys())

    @property
    def inputs(self) -> ArithmeticIODict:
        return _ports_to_registers(self.port_declarations, PortDirection.Input)

    @property
    def outputs(self) -> ArithmeticIODict:
        return _ports_to_registers(self.port_declarations, PortDirection.Output)

    def update_logic_flow(
        self, function_dict: Mapping[str, "QuantumFunctionDeclaration"]
    ) -> None:
        pass

    @pydantic.validator("operand_declarations")
    def _validate_operand_declarations_names(
        cls, operand_declarations: Dict[str, "OperandDeclaration"]
    ) -> Dict[str, "OperandDeclaration"]:
        cls._validate_declaration_names(operand_declarations, "Operand")
        return operand_declarations

    @pydantic.validator("port_declarations")
    def _validate_port_declarations_names(
        cls, port_declarations: Dict[IOName, PortDeclaration]
    ) -> Dict[IOName, PortDeclaration]:
        cls._validate_declaration_names(port_declarations, "Port")
        return port_declarations

    @pydantic.root_validator()
    def _validate_params_and_operands_uniqueness(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        operand_declarations = values.get("operand_declarations")
        parameter_declarations = values.get("param_decl")
        if operand_declarations is None or parameter_declarations is None:
            return values
        if len(operand_declarations.keys() & parameter_declarations.keys()):
            raise ValueError(
                "A function's operand and parameter cannot have the same name."
            )
        return values


def _ports_to_registers(
    port_declarations: Dict[IOName, PortDeclaration], direction: PortDirection
) -> ArithmeticIODict:
    return {
        name: RegisterUserInput(
            name=name,
            size=(
                port_decl.size.to_int_value()
                if port_decl.size.is_int_constant()
                else UNRESOLVED_SIZE
            ),
            is_signed=(
                port_decl.is_signed.to_bool_value()
                if port_decl.is_signed.is_bool_constant()
                else False
            ),
            fraction_places=(
                port_decl.fraction_places.to_int_value()
                if port_decl.fraction_places.is_int_constant()
                else 0
            ),
        )
        for name, port_decl in port_declarations.items()
        if port_decl.direction.includes_port_direction(direction)
    }


class QuantumOperandDeclaration(OperandDeclaration, QuantumFunctionDeclaration):
    pass


QuantumFunctionDeclaration.update_forward_refs()
