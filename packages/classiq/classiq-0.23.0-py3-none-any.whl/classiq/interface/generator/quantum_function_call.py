from __future__ import annotations

import functools
import itertools
import random
import re
import string
from collections import defaultdict
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Match,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import pydantic
from pydantic import BaseModel

from classiq.interface.generator import function_param_list, function_params as f_params
from classiq.interface.generator.arith.arithmetic import Arithmetic
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.function_call import FunctionCall
from classiq.interface.generator.function_params import (
    NAME_REGEX,
    ArithmeticIODict,
    FunctionParams,
    IOName,
    PortDirection,
)
from classiq.interface.generator.functions import (
    FunctionDeclaration,
    QuantumFunctionDeclaration,
)
from classiq.interface.generator.functions.statement import Statement
from classiq.interface.generator.slice_parsing_utils import (
    IO_REGEX,
    NAME,
    SEPARATOR,
    SLICING,
    parse_io_slicing,
)
from classiq.interface.generator.user_defined_function_params import CustomFunction
from classiq.interface.generator.wiring.sliced_wire import InoutPortBinding, PortBinding
from classiq.interface.helpers.custom_pydantic_types import PydanticNonEmptyString
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)

from classiq import ControlState
from classiq.exceptions import ClassiqControlError, ClassiqValueError

DEFAULT_SUFFIX_LEN: int = 6
BAD_INPUT_ERROR_MSG = "Bad input name given"
BAD_OUTPUT_ERROR_MSG = "Bad output name given"
BAD_INPUT_EXPRESSION_MSG = "Bad input expression given"
BAD_OUTPUT_EXPRESSION_MSG = "Bad output expression given"
BAD_INPUT_SLICING_MSG = "Bad input slicing / indexing given"
BAD_OUTPUT_SLICING_MSG = "Bad output slicing / indexing given"
BAD_CALL_NAME_ERROR_MSG = "Call name must be in snake_case and begin with a letter"
CUSTOM_FUNCTION_SINGLE_IO_ERROR = "Custom function currently supports explicit PortDirection specification only via dictionary"

LEGAL_SLICING = rf"(\-?\d+)?({SEPARATOR}(\-?\d+)?)?({SEPARATOR}(\-?\d+)?)?"

_ALPHANUM_CHARACTERS = string.ascii_letters + string.digits

RegNameAndSlice = Tuple[str, slice]

ZERO_INDICATOR = "0"
INVERSE_SUFFIX = "_qinverse"

SUFFIX_MARKER = "cs4id"

WireName = PydanticNonEmptyString
WireNameOrPortBinding = Union[WireName, PortBinding]
WireDict = Mapping[IOName, WireNameOrPortBinding]
IOType = Union[WireDict, WireName]


class WirePair(HashablePydanticBaseModel):
    in_wire: WireName
    out_wire: WireName


WireNamesOrInoutPortBinding = Union[WirePair, InoutPortBinding]

SUFFIX_RANDOMIZER = random.Random()


def split_wire_names_or_inout_slice(
    wire_names_or_inout_port_binding: WireNamesOrInoutPortBinding,
) -> Tuple[WireNameOrPortBinding, WireNameOrPortBinding]:
    if isinstance(wire_names_or_inout_port_binding, WirePair):
        return (
            wire_names_or_inout_port_binding.in_wire,
            wire_names_or_inout_port_binding.out_wire,
        )
    return (
        wire_names_or_inout_port_binding.source_binding,
        wire_names_or_inout_port_binding.destination_binding,
    )


def randomize_suffix(suffix_len: int = DEFAULT_SUFFIX_LEN) -> str:
    return "".join(
        SUFFIX_RANDOMIZER.choice(_ALPHANUM_CHARACTERS)
        for _ in range(suffix_len)  # nosec B311
    )


def get_non_zero_wires(
    wires: Iterable[WireNameOrPortBinding],
) -> List[WireNameOrPortBinding]:
    return [wire for wire in wires if wire != ZERO_INDICATOR]


class QuantumFunctionCall(FunctionCall, Statement):
    function_params: f_params.FunctionParams = pydantic.Field(
        description="The parameters necessary for defining the function"
    )
    is_inverse: bool = pydantic.Field(
        default=False, description="Call the function inverse."
    )
    assign_zero_ios: bool = pydantic.Field(
        default=False,
        description="Assign zero inputs/outputs to pre-defined registers",
    )
    release_by_inverse: bool = pydantic.Field(
        default=False, description="Release zero inputs in inverse call."
    )
    control_states: List[ControlState] = pydantic.Field(
        default_factory=list,
        description="Call the controlled function with the given controlled states.",
    )
    should_control: bool = pydantic.Field(
        default=True,
        description="False value indicates this call shouldn't be controlled even if the flow is controlled.",
    )
    inputs: IOType = pydantic.Field(
        default_factory=dict,
        description="A mapping from the input name to the wire it connects to",
    )
    inouts: Mapping[IOName, WireNamesOrInoutPortBinding] = pydantic.Field(
        default_factory=dict,
        description="A mapping from in/out name to the wires that connect to it",
    )
    outputs: IOType = pydantic.Field(
        default_factory=dict,
        description="A mapping from the output name to the wire it connects to",
    )
    power: pydantic.NonNegativeInt = pydantic.Field(
        default=1, description="Number of successive calls to the operation"
    )
    name: PydanticNonEmptyString = pydantic.Field(
        default=None,
        description="The name of the function instance. "
        "If not set, determined automatically.",
    )
    operands: Dict[str, LambdaFunctionList] = pydantic.Field(
        description="Function calls passed to the operator",
        default_factory=dict,
    )
    _func_decl: Optional[QuantumFunctionDeclaration] = pydantic.PrivateAttr(
        default=None
    )

    def __init__(
        self, *args, func_decl: Optional[QuantumFunctionDeclaration] = None, **kwargs
    ) -> None:
        super().__init__(*args, func_decl=func_decl, **kwargs)

    @property
    def func_decl(self) -> Optional[QuantumFunctionDeclaration]:
        return self._func_decl

    @property
    def is_operator_call(self) -> bool:
        return (
            len(self.operands) > 0
            or self.function == "join"
            or self.function == "split"
        )

    @property
    def operand_lambda_definitions_dict(self) -> Dict[str, List[QuantumLambdaFunction]]:
        return {
            name: _lambda_definitions(operand)
            for name, operand in self.operands.items()
        }

    def set_func_decl(self, fd: Optional[FunctionDeclaration]) -> None:
        if fd is not None and not isinstance(fd, QuantumFunctionDeclaration):
            raise ClassiqValueError(
                "the declaration of a quantum function call cannot be set to a non-quantum function declaration."
            )
        super().set_func_decl(fd)

    def __eq__(self, other) -> bool:
        return isinstance(other, QuantumFunctionCall) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @property
    def non_zero_input_wires(self) -> List[WireNameOrPortBinding]:
        in_out_input_wires = [
            split_wire_names_or_inout_slice(inout)[0] for inout in self.inouts.values()
        ]
        return get_non_zero_wires(self.inputs_dict.values()) + in_out_input_wires

    @property
    def non_zero_output_wires(self) -> List[WireNameOrPortBinding]:
        in_out_output_wires = [
            split_wire_names_or_inout_slice(inout)[1] for inout in self.inouts.values()
        ]
        return get_non_zero_wires(self.outputs_dict.values()) + in_out_output_wires

    @property
    def inputs_dict(self) -> WireDict:
        assert isinstance(self.inputs, dict)
        return self.inputs

    @property
    def outputs_dict(self) -> WireDict:
        assert isinstance(self.outputs, dict)
        return self.outputs

    @property
    def input_regs_dict(self) -> ArithmeticIODict:
        ctrl_regs_dict = {
            ctrl_state.name: ctrl_state.control_register
            for ctrl_state in self.control_states
        }
        return {
            **self._true_io_dict(io=PortDirection.Input),
            **ctrl_regs_dict,
        }

    @property
    def output_regs_dict(self) -> ArithmeticIODict:
        ctrl_regs_dict = {
            ctrl_state.name: ctrl_state.control_register
            for ctrl_state in self.control_states
        }
        return {
            **self._true_io_dict(io=PortDirection.Output),
            **ctrl_regs_dict,
        }

    def _true_io_dict(self, io: PortDirection) -> ArithmeticIODict:
        if (io == PortDirection.Input) != self.is_inverse:
            return self.function_params.inputs_full(self.assign_zero_ios)
        return self.function_params.outputs

    @pydantic.validator("name", pre=True, always=True)
    def _create_name(cls, name: Optional[str], values: Dict[str, Any]) -> str:
        """
        generates a name to a user defined-functions as follows:
        <function_name>_<SUFFIX_MARKER>_<random_suffix>
        """
        if name is not None:
            match = re.fullmatch(pattern=NAME_REGEX, string=name)
            if match is None:
                raise ValueError(BAD_CALL_NAME_ERROR_MSG)
            return name

        function = values.get("function")
        params = values.get("function_params")
        suffix = f"{SUFFIX_MARKER}_{randomize_suffix()}"
        if not function or params is None:
            return name if name else suffix
        return f"{function}_{suffix}"

    @pydantic.root_validator(pre=True)
    def validate_composite_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values.get("unitary_params"), CustomFunction) and not values.get(
            "unitary"
        ):
            raise ClassiqValueError(
                "`PhaseEstimation` of a user define function (`CustomFunction`) must receive the function name from the `unitary` field"
            )
        return values

    @pydantic.root_validator(pre=True)
    def _parse_function_params(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        f_params.parse_function_params_values(
            values=values,
            params_key="function_params",
            discriminator_key="function",
            param_classes=function_param_list.function_param_library.param_list,
            default_parser_class=CustomFunction,
        )
        return values

    # TODO: note that this checks QuantumFunctionCall input register names
    # are PARTIAL to FunctionParams input register names, not EQUAL.
    # We might want to change that.
    @staticmethod
    def _validate_input_names(
        *,
        params: f_params.FunctionParams,
        inputs: WireDict,
        is_inverse: bool,
        control_states: List[ControlState],
        assign_zero_ios: bool,
    ) -> None:
        (
            invalid_expressions,
            invalid_slicings,
            invalid_names,
        ) = QuantumFunctionCall._get_invalid_ios(
            expressions=inputs.keys(),
            params=params,
            io=PortDirection.Input if not is_inverse else PortDirection.Output,
            control_states=control_states,
            assign_zero_ios=assign_zero_ios,
        )
        error_msg = []
        if invalid_expressions:
            error_msg.append(f"{BAD_INPUT_EXPRESSION_MSG}: {invalid_expressions}")
        if invalid_names:
            error_msg.append(f"{BAD_INPUT_ERROR_MSG}: {invalid_names}")
        if invalid_slicings:
            error_msg.append(f"{BAD_INPUT_SLICING_MSG}: {invalid_slicings}")
        if error_msg:
            raise ValueError("\n".join(error_msg))

    def check_and_update(
        self,
        function_dict: Mapping[str, QuantumFunctionDeclaration],
    ) -> None:
        if not isinstance(self.function_params, CustomFunction):
            return
        self._resolve_function_def(
            function_dict, QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS
        )
        assert self.func_decl is not None
        self.function_params.generate_ios(
            inputs=self.func_decl.inputs,
            outputs=self.func_decl.outputs,
        )
        self._validate_custom_function_io()
        self._check_and_update_operands(function_dict)

    def _check_and_update_operands(
        self,
        function_dict: Mapping[str, QuantumFunctionDeclaration],
    ) -> None:
        for operand_list in self.operand_lambda_definitions_dict.values():
            for single_operand in operand_list:
                for call in single_operand.logic_flow:
                    call.check_and_update(function_dict)

    @pydantic.validator("assign_zero_ios")
    def _validate_arithmetic_cannot_assign_zero_ios(
        cls, assign_zero_ios: bool, values: Dict[str, Any]
    ) -> bool:
        assert not (
            values.get("function") == Arithmetic.discriminator() and assign_zero_ios
        ), "when using the Arithmetic function, assign to the expression result register via the target parameter instead of the assign_zero_ios flag"
        return assign_zero_ios

    @pydantic.validator("control_states")
    def _validate_control_states(
        cls, control_states: List[ControlState], values: Dict[str, Any]
    ) -> List[ControlState]:
        control_names = [ctrl_state.name for ctrl_state in control_states]
        function_params = values.get("function_params")
        assign_zero_ios = values.get("assign_zero_ios")
        if not (
            isinstance(function_params, FunctionParams)
            and isinstance(assign_zero_ios, bool)
        ):
            return control_states
        all_input_names = [
            *function_params.inputs_full(assign_zero_ios=assign_zero_ios),
            *control_names,
        ]
        all_output_names = [*function_params.outputs, *control_names]
        if any(
            cls._has_repetitions(name_list)
            for name_list in (control_names, all_input_names, all_output_names)
        ):
            raise ClassiqControlError()
        return control_states

    @staticmethod
    def _has_repetitions(name_list: Sequence[str]) -> bool:
        return len(set(name_list)) < len(name_list)

    @staticmethod
    def _validate_slices(
        io: PortDirection,
        inputs: IOType,
        fp: FunctionParams,
        assign_zero_ios: bool,
        control_states: List[ControlState],
    ) -> None:
        name_slice_pairs = [parse_io_slicing(input) for input in inputs]
        slices_dict: Dict[str, List[slice]] = defaultdict(list)
        for name, slice in name_slice_pairs:
            slices_dict[name].append(slice)

        fp_inputs = (
            fp.inputs_full(assign_zero_ios)
            if (io == PortDirection.Input)
            else fp.outputs
        )
        widths = {name: reg.size for name, reg in fp_inputs.items()}
        control_names = {state.name for state in control_states}

        for name in slices_dict:
            if name in control_names:
                continue
            assert name in widths, "Name not in widths"
            if not QuantumFunctionCall._register_validate_slices(
                slices_dict[name], widths[name]
            ):
                raise ValueError(BAD_INPUT_SLICING_MSG)

    @staticmethod
    def _register_validate_slices(slices: List[slice], reg_width: int) -> bool:
        widths_separated = [len(range(reg_width)[reg_slice]) for reg_slice in slices]
        # examples: slice(0), slice(5,None) when width <= 5, slice(5,3)
        empty_slices = 0 in widths_separated

        max_stop = max(reg_slice.stop or 0 for reg_slice in slices)
        out_of_range = max_stop > reg_width

        all_widths_separated = sum(widths_separated)
        all_indices = set(
            itertools.chain.from_iterable(
                range(reg_width)[reg_slice] for reg_slice in slices
            )
        )
        all_widths_combined = len(all_indices)
        overlapping_slices = all_widths_combined != all_widths_separated

        return not any((empty_slices, out_of_range, overlapping_slices))

    @pydantic.validator("inputs")
    def _validate_inputs(cls, inputs: IOType, values: Dict[str, Any]) -> WireDict:
        params: Optional[FunctionParams] = values.get("function_params")
        is_inverse: bool = values.get("is_inverse", False)
        assign_zero_ios: bool = values.get("assign_zero_ios", False)
        control_states: List[ControlState] = values.get("control_states", list())
        if params is None:
            return dict()
        if isinstance(params, CustomFunction):
            if not isinstance(inputs, dict):
                raise ValueError(CUSTOM_FUNCTION_SINGLE_IO_ERROR)
            return inputs

        if isinstance(inputs, str):
            inputs = QuantumFunctionCall._single_wire_to_dict(
                io=f_params.PortDirection.Input,
                is_inverse=is_inverse,
                io_wire=inputs,
                params=params,
                assign_zero_ios=assign_zero_ios,
            )

        cls._validate_input_names(
            params=params,
            inputs=inputs,
            is_inverse=is_inverse,
            control_states=control_states,
            assign_zero_ios=assign_zero_ios,
        )

        cls._validate_slices(
            PortDirection.Input if not is_inverse else PortDirection.Output,
            inputs,
            params,
            assign_zero_ios,
            control_states,
        )

        return inputs

    @staticmethod
    def _validate_output_names(
        *,
        params: f_params.FunctionParams,
        outputs: WireDict,
        is_inverse: bool,
        control_states: List[ControlState],
        assign_zero_ios: bool,
    ) -> None:
        (
            invalid_expressions,
            invalid_slicings,
            invalid_names,
        ) = QuantumFunctionCall._get_invalid_ios(
            expressions=outputs.keys(),
            params=params,
            io=PortDirection.Output if not is_inverse else PortDirection.Input,
            control_states=control_states,
            assign_zero_ios=assign_zero_ios,
        )
        error_msg = []
        if invalid_expressions:
            error_msg.append(f"{BAD_OUTPUT_EXPRESSION_MSG}: {invalid_expressions}")
        if invalid_names:
            error_msg.append(f"{BAD_OUTPUT_ERROR_MSG}: {invalid_names}")
        if invalid_slicings:
            error_msg.append(f"{BAD_OUTPUT_SLICING_MSG}: {invalid_slicings}")
        if error_msg:
            raise ValueError("\n".join(error_msg))

    @pydantic.validator("outputs")
    def _validate_outputs(cls, outputs: IOType, values: Dict[str, Any]) -> IOType:
        params = values.get("function_params")
        is_inverse: bool = values.get("is_inverse", False)
        assign_zero_ios: bool = values.get("assign_zero_ios", False)
        control_states = values.get("control_states", list())
        if params is None:
            return outputs
        if isinstance(params, CustomFunction):
            if not isinstance(outputs, dict):
                raise ValueError(CUSTOM_FUNCTION_SINGLE_IO_ERROR)
            return outputs

        if isinstance(outputs, str):
            outputs = QuantumFunctionCall._single_wire_to_dict(
                io=f_params.PortDirection.Output,
                is_inverse=is_inverse,
                io_wire=outputs,
                params=params,
                assign_zero_ios=assign_zero_ios,
            )

        cls._validate_output_names(
            params=params,
            outputs=outputs,
            is_inverse=is_inverse,
            control_states=control_states,
            assign_zero_ios=assign_zero_ios,
        )

        cls._validate_slices(
            PortDirection.Input if is_inverse else PortDirection.Output,
            outputs,
            params,
            assign_zero_ios,
            control_states,
        )

        return outputs

    @pydantic.validator("power", always=True)
    def _validate_power(
        cls, power: pydantic.NonNegativeInt, values: Dict[str, Any]
    ) -> pydantic.NonNegativeInt:
        function_params = values.get("function_params")
        if function_params is None:
            return power
        if power != 1 and not function_params.is_powerable(
            values.get("assign_zero_ios")
        ):
            raise ValueError("Cannot power this operator")
        return power

    @staticmethod
    def _single_wire_to_dict(
        io: f_params.PortDirection,
        is_inverse: bool,
        io_wire: WireName,
        params: f_params.FunctionParams,
        assign_zero_ios: bool = False,
    ) -> WireDict:
        params_io = list(
            params.inputs_full(assign_zero_ios)
            if (io == PortDirection.Input) != is_inverse
            else params.outputs
        )

        if len(params_io) == 1:
            return {list(params_io)[0]: io_wire}
        error_message = _generate_single_io_err(
            io_str=io.name.lower(),
            io_regs=params_io,
            io_wire=io_wire,
            function_name=type(params).__name__,
        )
        raise ValueError(error_message)

    @staticmethod
    def _get_invalid_ios(
        *,
        expressions: Iterable[str],
        params: f_params.FunctionParams,
        io: f_params.PortDirection,
        control_states: List[ControlState],
        assign_zero_ios: bool,
    ) -> Tuple[List[str], List[str], List[str]]:
        expression_matches: Iterable[Optional[Match]] = map(
            functools.partial(re.fullmatch, IO_REGEX), expressions
        )

        valid_matches: List[Match] = []
        invalid_expressions: List[str] = []
        for expression, expression_match in zip(expressions, expression_matches):
            invalid_expressions.append(
                expression
            ) if expression_match is None else valid_matches.append(expression_match)

        invalid_slicings: List[str] = []
        invalid_names: List[str] = []
        valid_names = frozenset(
            params.inputs_full(assign_zero_ios)
            if io == PortDirection.Input
            else params.outputs
        )
        for match in valid_matches:
            name = match.groupdict().get(NAME)
            if name is None:
                raise AssertionError("Input/output name validation error")

            slicing = match.groupdict().get(SLICING)
            if slicing is not None and re.fullmatch(LEGAL_SLICING, slicing) is None:
                invalid_slicings.append(match.string)

            if name in valid_names:
                continue
            elif all(state.name != name for state in control_states):
                invalid_names.append(name)

        return invalid_expressions, invalid_slicings, invalid_names

    def _validate_custom_function_io(self) -> None:
        if not isinstance(self.function_params, CustomFunction):
            raise AssertionError("CustomFunction object expected.")
        QuantumFunctionCall._validate_input_names(
            params=self.function_params,
            inputs=self.inputs_dict,
            is_inverse=self.is_inverse,
            control_states=self.control_states,
            assign_zero_ios=self.assign_zero_ios,
        )
        QuantumFunctionCall._validate_output_names(
            params=self.function_params,
            outputs=self.outputs_dict,
            is_inverse=self.is_inverse,
            control_states=self.control_states,
            assign_zero_ios=self.assign_zero_ios,
        )

    def get_param_exprs(self) -> Dict[str, Expression]:
        if isinstance(self.function_params, CustomFunction):
            return super().get_param_exprs()
        else:
            param_exprs = dict()
            for name, raw_expr in self.function_params:
                if self.function_params.is_field_gen_param(name):
                    expr = Expression(expr=raw_expr)
                    expr.resolve()
                    param_exprs[name] = expr

            return param_exprs

    def inverse(self) -> QuantumFunctionCall:
        call_kwargs = self.__dict__.copy()
        call_kwargs["inputs"] = self.outputs_dict
        call_kwargs["outputs"] = self.inputs_dict
        call_kwargs["name"] = self.inverse_name(self.name)
        call_kwargs["is_inverse"] = not self.is_inverse
        return QuantumFunctionCall(**call_kwargs)

    @staticmethod
    def inverse_name(name: str) -> str:
        if name.endswith(INVERSE_SUFFIX):
            return name[: -len(INVERSE_SUFFIX)]
        return f"{name}{INVERSE_SUFFIX}"

    def control(
        self, control_state: ControlState, input_wire: WireName, output_wire: WireName
    ) -> QuantumFunctionCall:
        if (
            control_state.name in self.inputs_dict
            or control_state.name in self.outputs_dict
        ):
            raise ValueError(f"Control name: {control_state.name} already exists")

        inputs, outputs = dict(self.inputs_dict), dict(self.outputs_dict)
        inputs.update({control_state.name: input_wire})
        outputs.update({control_state.name: output_wire})

        call_kwargs = self.__dict__.copy()
        call_kwargs["inputs"] = inputs
        call_kwargs["outputs"] = outputs
        call_kwargs["name"] = f"{self.name}_{control_state.name}"
        call_kwargs["control_states"] = self.control_states + [control_state]
        return QuantumFunctionCall(**call_kwargs)


class QuantumLambdaFunction(BaseModel):
    """
    The definition of an anonymous function passed as operand to higher-level functions
    """

    rename_params: Dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Mapping of the declared param to the actual variable name used ",
    )

    logic_flow: List[QuantumFunctionCall] = pydantic.Field(
        description="A list of function calls passed to the operator"
    )


class LambdaListComprehension(BaseModel):
    """
    Specification of a list of lambda functions iteratively
    """

    count: Expression = pydantic.Field(
        description="The number of lambda functions in the list"
    )

    index_var: str = pydantic.Field(
        description="The name of the integer variable holding the iteration index"
    )

    func: QuantumLambdaFunction = pydantic.Field(
        description="A lambda function definition replicated for index values 0 to count-1"
    )


LambdaFunctionList = Union[
    QuantumLambdaFunction, List[QuantumLambdaFunction], LambdaListComprehension
]


def _generate_single_io_err(
    *, io_str: str, io_regs: Iterable[str], io_wire: str, function_name: str
) -> str:
    if not io_regs:
        return (
            f"Cannot create {io_str} wire {io_wire!r}. "
            f"Function {function_name} has no {io_str} registers."
        )

    return (
        f"Cannot use a single {io_str} wire. "
        f"Function {function_name} has multiple {io_str} registers: {io_regs}."
    )


def _lambda_definitions(operand: LambdaFunctionList) -> List[QuantumLambdaFunction]:
    if isinstance(operand, list):
        return operand
    elif isinstance(operand, LambdaListComprehension):
        return [operand.func]
    else:
        return [operand]


QuantumFunctionCall.update_forward_refs()
