import ast
import itertools
import re
from enum import Enum
from typing import (
    Any,
    Collection,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Type,
    Union,
)

import pydantic
import sympy
from pydantic.fields import ModelField

from classiq.interface.generator.arith.arithmetic_expression_validator import (
    validate_expression,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.parameters import ParameterFloatType
from classiq.interface.helpers.custom_pydantic_types import PydanticNonEmptyString
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)

FunctionParamsDiscriminator = str

IOName = PydanticNonEmptyString
ArithmeticIODict = Dict[IOName, RegisterUserInput]

DEFAULT_ZERO_NAME = "zero"
DEFAULT_OUTPUT_NAME = "OUT"
DEFAULT_INPUT_NAME = "IN"

BAD_FUNCTION_ERROR_MSG = "field must be provided to deduce"
NO_DISCRIMINATOR_ERROR_MSG = "Unknown"

REGISTER_SIZES_MISMATCH_ERROR_MSG = "Register sizes differ between inputs and outputs"

BAD_INPUT_REGISTER_ERROR_MSG = "Bad input register name given"
BAD_OUTPUT_REGISTER_ERROR_MSG = "Bad output register name given"
END_BAD_REGISTER_ERROR_MSG = (
    "Register name must be in snake_case and begin with a letter."
)

ALPHANUM_AND_UNDERSCORE = r"[0-9a-zA-Z_]*"
NAME_REGEX = rf"[a-zA-Z]{ALPHANUM_AND_UNDERSCORE}"

_UNVALIDATED_FUNCTIONS = ["Arithmetic", "CustomFunction"]

ExecutionExpressionSupportedNodeTypes = Union[
    # binary operation
    ast.BinOp,
    ast.BitOr,
    ast.BitAnd,
    ast.BitXor,
    # binary operation - arithmetic
    ast.Add,
    ast.Mod,
    ast.Sub,
    ast.LShift,
    ast.RShift,
    ast.Mult,
    ast.Div,
    # Unary operations
    ast.UnaryOp,
    ast.USub,
    ast.UAdd,
    ast.Invert,
    # Other
    ast.Expression,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Num,
]

GenerationOnlyExpressionSupportedNodeTypes = Union[
    ast.FloorDiv,
    ast.Pow,
    ast.List,
    ast.Subscript,
    ast.Index,
    ast.Tuple,
    ast.Compare,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.Eq,
    ast.Call,
    ast.Dict,
]

GenerationExpressionSupportedNodeTypes = Union[
    ExecutionExpressionSupportedNodeTypes, GenerationOnlyExpressionSupportedNodeTypes
]


def validate_expression_str(
    name: str, expr_str: str, supported_functions: Optional[Collection[str]] = None
) -> None:
    # By default, no functions are allowed.
    supported_functions = supported_functions or set()

    # We validate the given value is legal and does not contain code that will be executed in our BE.
    validate_expression(
        expr_str,
        supported_nodes=GenerationExpressionSupportedNodeTypes,
        expression_type="parameter",
        supported_functions=supported_functions,
    )


class PortDirection(str, Enum):
    Input = "input"
    Output = "output"
    Inout = "inout"

    def __invert__(self) -> "PortDirection":
        if self is PortDirection.Inout:
            return self
        return (
            PortDirection.Input
            if self is PortDirection.Output
            else PortDirection.Output
        )


def get_zero_input_name(output_name: str) -> str:
    return f"{DEFAULT_ZERO_NAME}_{output_name}"


class FunctionParams(HashablePydanticBaseModel):
    _inputs: ArithmeticIODict = pydantic.PrivateAttr(default_factory=dict)
    _outputs: ArithmeticIODict = pydantic.PrivateAttr(default_factory=dict)
    _zero_inputs: ArithmeticIODict = pydantic.PrivateAttr(default_factory=dict)

    @property
    def inputs(self) -> ArithmeticIODict:
        return self._inputs

    def inputs_full(self, assign_zero_ios: bool = False) -> ArithmeticIODict:
        if assign_zero_ios:
            return {**self._inputs, **self._zero_inputs}
        return self._inputs

    @property
    def outputs(self) -> ArithmeticIODict:
        return self._outputs

    def num_input_qubits(self, assign_zero_ios: bool = False) -> int:
        return sum(reg.size for reg in self.inputs_full(assign_zero_ios).values())

    @property
    def num_output_qubits(self) -> int:
        return sum(reg.size for reg in self.outputs.values())

    @property
    def _input_names(self) -> List[IOName]:
        return list(self._inputs.keys())

    @property
    def _output_names(self) -> List[IOName]:
        return list(self._outputs.keys())

    def _create_zero_input_registers(self, names_and_sizes: Mapping[str, int]) -> None:
        for name, size in names_and_sizes.items():
            self._zero_inputs[name] = RegisterUserInput(name=name, size=size)

    def _create_zero_inputs_from_outputs(self) -> None:
        for name, reg in self._outputs.items():
            zero_input_name = get_zero_input_name(name)
            self._zero_inputs[zero_input_name] = reg.revalued(name=zero_input_name)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._create_ios()
        if not self._inputs and not self._zero_inputs:
            self._create_zero_inputs_from_outputs()
        self._validate_io_names()

        if self.discriminator() not in _UNVALIDATED_FUNCTIONS:
            self._validate_total_io_sizes()

    def is_field_param_type(self, name: str, param_type_signature: str) -> bool:
        f = type(self).__fields__[name]
        return isinstance(f, ModelField) and (
            param_type_signature in f.field_info.extra
        )

    def is_field_gen_param(self, name: str) -> bool:
        return self.is_field_param_type(
            name, "is_gen_param"
        ) or self.is_field_exec_param(name)

    def is_field_exec_param(self, name: str) -> bool:
        return self.is_field_param_type(name, "is_exec_param")

    def is_powerable(self, assign_zero_ios: bool = False) -> bool:
        input_names = set(self.inputs_full(assign_zero_ios))
        output_names = set(self._output_names)
        return (
            self.num_input_qubits(assign_zero_ios) == self.num_output_qubits
            and len(input_names) == len(output_names)
            and (len(input_names - output_names) <= 1)
            and (len(output_names - input_names) <= 1)
        )

    def get_power_order(self) -> Optional[int]:
        return None

    def _create_ios(self) -> None:
        pass

    @staticmethod
    def _get_size_of_ios(registers: Collection[Optional[RegisterUserInput]]) -> int:
        return sum(reg.size if reg is not None else 0 for reg in registers)

    def _validate_io_names(self) -> None:
        error_msg: List[str] = []
        error_msg += self._get_error_msg(self._inputs, BAD_INPUT_REGISTER_ERROR_MSG)
        error_msg += self._get_error_msg(self._outputs, BAD_OUTPUT_REGISTER_ERROR_MSG)
        if error_msg:
            error_msg += [END_BAD_REGISTER_ERROR_MSG]
            raise ValueError("\n".join(error_msg))

    @staticmethod
    def _sum_registers_sizes(registers: Iterable[RegisterUserInput]) -> int:
        return sum(reg.size for reg in registers)

    def _validate_total_io_sizes(self) -> None:
        total_inputs_size = self._sum_registers_sizes(
            itertools.chain(self._inputs.values(), self._zero_inputs.values())
        )
        total_outputs_size = self._sum_registers_sizes(self._outputs.values())
        if total_inputs_size != total_outputs_size:
            raise ValueError(REGISTER_SIZES_MISMATCH_ERROR_MSG)

    def _get_error_msg(self, names: Iterable[IOName], msg: str) -> List[str]:
        bad_names = [name for name in names if re.fullmatch(NAME_REGEX, name) is None]
        return [f"{msg}: {bad_names}"] if bad_names else []

    @classmethod
    def discriminator(cls) -> FunctionParamsDiscriminator:
        return cls.__name__

    def _assign_parameters(
        self, parameters_dict: Dict[str, ParameterFloatType]
    ) -> "FunctionParams":
        new_params: Dict[str, ParameterFloatType] = {}
        for param in self._params:
            param_val = getattr(self, param)
            if not isinstance(param_val, str):
                continue

            new_param_expr = sympy.parse_expr(param_val).subs(parameters_dict)
            new_params[param] = (
                float(new_param_expr)
                if new_param_expr.is_number
                else str(new_param_expr)
            )

        return self.copy(update=new_params, deep=True)

    @property
    def _params(self) -> List[str]:
        return [
            name
            for name, field in self.__fields__.items()
            if field.field_info.extra.get("is_exec_param", False)
        ]

    @property
    def _symbols(self) -> Set[str]:
        symbols = set(
            itertools.chain.from_iterable(
                sympy.parse_expr(getattr(self, param)).free_symbols
                for param in self._params
                if isinstance(getattr(self, param), str)
            )
        )
        return {str(symbol) for symbol in symbols}

    @pydantic.validator("*", pre=True)
    def validate_parameters(cls, value, field: pydantic.fields.ModelField):
        if (
            "is_exec_param" in field.field_info.extra
            or "is_gen_param" in field.field_info.extra
        ):
            if isinstance(value, str):
                validate_expression_str(field.name, value)
            elif isinstance(value, sympy.Expr):
                return str(value)
        return value

    class Config:
        frozen = True


def parse_function_params(
    *,
    params: Any,
    discriminator: Any,
    param_classes: Collection[Type[FunctionParams]],
    no_discriminator_error: Exception,
    bad_function_error: Exception,
    default_parser_class: Optional[Type[FunctionParams]] = None,
) -> FunctionParams:  # Any is for use in pydantic validators.
    if params is None and default_parser_class is not None:
        return default_parser_class()

    if not discriminator:
        raise no_discriminator_error

    matching_classes = [
        param_class
        for param_class in param_classes
        if param_class.discriminator() == discriminator
    ]

    if len(matching_classes) != 1:
        if default_parser_class is not None:
            try:
                return default_parser_class.parse_obj(params)
            except Exception:
                raise bad_function_error
        raise bad_function_error

    return matching_classes[0].parse_obj(params)


def parse_function_params_values(
    *,
    values: Dict[str, Any],
    params_key: str,
    discriminator_key: str,
    param_classes: Collection[Type[FunctionParams]],
    default_parser_class: Type[FunctionParams],
) -> None:
    params = values.get(params_key)
    if isinstance(params, FunctionParams):
        values.setdefault(discriminator_key, params.discriminator())
        return
    discriminator = values.get(discriminator_key)
    values[params_key] = parse_function_params(
        params=params,
        discriminator=discriminator,
        param_classes=param_classes,
        no_discriminator_error=ValueError(
            f"The {discriminator_key} {NO_DISCRIMINATOR_ERROR_MSG} {params_key} type."
        ),
        bad_function_error=ValueError(
            f"{BAD_FUNCTION_ERROR_MSG} {discriminator_key}: {discriminator}"
        ),
        default_parser_class=default_parser_class,
    )
