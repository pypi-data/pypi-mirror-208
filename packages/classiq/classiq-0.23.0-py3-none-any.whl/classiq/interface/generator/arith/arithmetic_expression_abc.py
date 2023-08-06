import abc
import ast
import enum
import re
from typing import Any, Dict, Optional, Set

import pydantic

from classiq.interface.generator.arith import arithmetic_expression_parser, number_utils
from classiq.interface.generator.arith.arithmetic_result_builder import (
    ArithmeticDefinitions,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.expressions.expression_constants import (
    FORBIDDEN_LITERALS,
    SUPPORTED_FUNC_NAMES,
    SUPPORTED_VAR_NAMES_REG,
)
from classiq.interface.generator.function_params import FunctionParams
from classiq.interface.helpers.custom_pydantic_types import PydanticExpressionStr


class UncomputationMethods(str, enum.Enum):
    naive = "naive"
    optimized = "optimized"


class MappingMethods(str, enum.Enum):
    naive = UncomputationMethods.naive.value
    optimized = UncomputationMethods.optimized.value
    dirty_optimized = "dirty_optimized"
    no_uncomputation = "no_uncomputation"


class ArithmeticExpressionABC(abc.ABC, FunctionParams):
    max_fraction_places: pydantic.NonNegativeInt = number_utils.MAX_FRACTION_PLACES
    expression: PydanticExpressionStr
    definitions: ArithmeticDefinitions
    qubit_count: Optional[pydantic.NonNegativeInt] = None
    simplify: bool = False

    @pydantic.validator("expression")
    def _check_expression_is_legal(cls, expression: str) -> str:
        try:
            ast.parse(expression, "", "eval")
        except SyntaxError:
            raise ValueError(f"Failed to parse expression {expression!r}") from None
        return expression

    @pydantic.validator("simplify")
    def _validate_expression_graph_for_simplify(
        cls, simplify: bool, values: Dict[str, Any]
    ) -> bool:
        if simplify:
            arithmetic_expression_parser.validate_expression_graph(
                expression=values.get("expression", ""),
            )
        return simplify

    @pydantic.root_validator()
    def _check_all_variable_are_defined(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        expression: str = values.get("expression", "")
        definitions: ArithmeticDefinitions = values.get("definitions", dict())
        literals = set(re.findall(SUPPORTED_VAR_NAMES_REG, expression))

        not_allowed = literals.intersection(FORBIDDEN_LITERALS)
        if not_allowed:
            raise ValueError(f"The following names: {not_allowed} are not allowed")

        undefined_literals = literals.difference(definitions, SUPPORTED_FUNC_NAMES)
        if undefined_literals:
            raise ValueError(f"{undefined_literals} need to be defined in definitions")
        return values

    @pydantic.root_validator()
    def _substitute_expression(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        expression = values.get("expression")
        definitions = values.get("definitions")
        if expression is None or definitions is None:
            raise ValueError("Valid expression and definition are required")
        max_fraction_places: int = values.get(
            "max_fraction_places", number_utils.MAX_FRACTION_PLACES
        )

        new_definitions = dict()
        for var_name, value in definitions.items():
            if isinstance(value, RegisterUserInput):
                new_definitions[var_name] = value
                continue
            if isinstance(value, int):
                pass
            elif isinstance(value, float):
                value = number_utils.limit_fraction_places(
                    value, max_fraction_places=max_fraction_places
                )
            else:
                raise ValueError(f"{type(value)} type is illegal")
            expression = re.sub(r"\b" + var_name + r"\b", str(value), expression)
        values["expression"] = expression
        values["definitions"] = new_definitions
        return values

    @pydantic.validator("definitions")
    def _set_register_names(
        cls, definitions: ArithmeticDefinitions
    ) -> ArithmeticDefinitions:
        for name, reg in definitions.items():
            if isinstance(reg, RegisterUserInput):
                definitions[name] = reg.revalued(name=name)
        return definitions

    def _get_literal_set(self) -> Set[str]:
        return (
            set(re.findall("[A-Za-z][A-Za-z0-9]*", self.expression))
            - SUPPORTED_FUNC_NAMES
        )
