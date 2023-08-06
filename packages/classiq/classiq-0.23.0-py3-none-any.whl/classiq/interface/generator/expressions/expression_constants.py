import keyword
from typing import Set

from classiq.interface.generator.arith.arithmetic_expression_parser import (
    DEFAULT_SUPPORTED_FUNC_NAMES,
)
from classiq.interface.generator.expressions.sympy_supported_expressions import (
    SYMPY_SUPPORTED_EXPRESSIONS,
)

SUPPORTED_VAR_NAMES_REG = "[A-Za-z][A-Za-z0-9]*"

SUPPORTED_FUNC_NAMES: Set[str] = (
    {"or", "and"}.union(DEFAULT_SUPPORTED_FUNC_NAMES).union(SYMPY_SUPPORTED_EXPRESSIONS)
)
FORBIDDEN_LITERALS: Set[str] = set(keyword.kwlist) - SUPPORTED_FUNC_NAMES
