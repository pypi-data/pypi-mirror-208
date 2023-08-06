from typing import Any, Dict, List, Optional

import pydantic
from pydantic import BaseModel
from sympy import Array, Basic, Function, sympify
from sympy.logic.boolalg import BooleanFalse, BooleanTrue
from sympy.tensor.array import ArrayKind

from classiq.interface.generator.expressions import sympy_list_as_array  # noqa: F401
from classiq.interface.generator.expressions.atomic_expression_functions import (
    SUPPORTED_ATOMIC_EXPRESSION_FUNCTIONS,
)
from classiq.interface.generator.expressions.optimizers import Optimizer
from classiq.interface.generator.expressions.pauli import Pauli
from classiq.interface.generator.expressions.sympy_struct_instance import (
    SympyStructInstance,
)
from classiq.interface.generator.expressions.sympy_supported_expressions import (
    SYMPY_SUPPORTED_EXPRESSIONS,
)
from classiq.interface.generator.function_params import validate_expression_str
from classiq.interface.generator.functions.classical_type import (
    ClassicalType,
    sympy_symbols,
)
from classiq.interface.generator.node_reducer import ModelNode, reduce_node
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class Expression(HashablePydanticBaseModel):
    expr: str

    _sympy_expr_attr: Optional[Basic] = pydantic.PrivateAttr(default=None)

    def __init__(self, *, sympy_expr: Optional[Basic] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if sympy_expr is not None:
            self._sympy_expr_attr = sympy_expr

        self._try_resolve_as_immediate()

    @property
    def _sympy_expr(self) -> Basic:
        assert self._sympy_expr_attr is not None
        return self._sympy_expr_attr

    @property
    def evaluated_expr(self) -> str:
        return str(self._sympy_expr)

    def resolve(self, params: Optional[Dict[str, ClassicalType]] = None) -> None:
        if self._sympy_expr_attr is not None:
            return
        self._sympy_expr_attr = self._sympify_wrapper(params)

    def is_resolved(self) -> bool:
        return self._sympy_expr_attr is not None

    def is_int_constant(self) -> bool:
        return self.is_resolved() and self._sympy_expr.is_Integer

    def to_int_value(self) -> int:
        if not self.is_int_constant():
            raise ValueError("Expression is not an integer constant")
        return int(self._sympy_expr)

    def is_bool_constant(self) -> bool:
        return self.is_resolved() and self._sympy_expr.is_Boolean

    def to_bool_value(self) -> bool:
        if not self.is_bool_constant():
            raise ValueError("Expression is not a boolean constant")
        return bool(self._sympy_expr)

    def is_numeric_constant(self) -> bool:
        return self.is_resolved() and self._sympy_expr.is_Number

    def to_float_value(self) -> float:
        if not self.is_numeric_constant():
            raise ValueError("Expression is not a number constant")
        return float(self._sympy_expr)

    def is_list(self) -> bool:
        return self.is_resolved() and isinstance(self._sympy_expr.kind, ArrayKind)

    def to_list(self) -> List[Any]:
        if not self.is_list():
            raise ValueError("Expression is not a list")
        return list(self._sympy_expr)

    def is_sympy_struct(self) -> bool:
        return self.is_resolved() and isinstance(self._sympy_expr, SympyStructInstance)

    def to_sympy_struct_dict(self) -> Dict[str, Any]:
        if not self.is_sympy_struct():
            raise ValueError("value is not a sympy struct")
        return {key.name: value for (key, value) in self._sympy_expr.fields.items()}

    @pydantic.validator("expr")
    def validate_expression(cls, expr: str) -> str:
        supported_functions = (
            SUPPORTED_ATOMIC_EXPRESSION_FUNCTIONS | SYMPY_SUPPORTED_EXPRESSIONS
        )
        validate_expression_str(
            "expression", expr, supported_functions=supported_functions
        )
        return expr

    def _try_resolve_as_immediate(self) -> None:
        try:
            resolved_expr = self._sympy_expr_attr
            if resolved_expr is None:
                resolved_expr = self._sympify_wrapper()

            if resolved_expr.is_Number or resolved_expr.is_Boolean:
                self._sympy_expr_attr = resolved_expr
        except TypeError:
            # Ignore issues related to subscription and what not,
            # this is not an immediate and needs extra context to be resolved
            pass

    def _sympify_wrapper(
        self, params: Optional[Dict[str, ClassicalType]] = None
    ) -> Basic:
        params = params or dict()
        params = params or dict()
        sympy_locals = sympy_symbols(params)
        sympy_locals.update(Pauli.sympy_locals())
        sympy_locals.update(Optimizer.sympy_locals())
        sympy_locals.update(
            {name: Function(name) for name in SUPPORTED_ATOMIC_EXPRESSION_FUNCTIONS}
        )
        sympify_result = sympify(self.expr, locals=sympy_locals)

        if isinstance(sympify_result, list):
            sympify_result = Array(sympify_result)
        elif isinstance(sympify_result, (Pauli, Optimizer)):
            sympify_result = sympify_result.to_sympy()
        elif isinstance(sympify_result, bool):
            sympify_result = BooleanTrue() if sympify_result else BooleanFalse()

        return sympify_result

    class Config:
        frozen = True


def resolve_expressions(
    model: ModelNode, params: Dict[str, ClassicalType]
) -> ModelNode:
    def visit(expr: BaseModel) -> BaseModel:
        if not isinstance(expr, Expression):
            return expr.copy()

        new_expr = expr.copy()
        new_expr.resolve(params)
        return new_expr

    return reduce_node(model, [visit])
