import ast
from typing import Any, Collection, Optional, Set, Tuple, Union

from typing_extensions import get_args

from classiq.interface.generator.arith.ast_node_rewrite import AstNodeRewrite
from classiq.interface.generator.expressions.sympy_supported_expressions import (
    SYMPY_SUPPORTED_EXPRESSIONS,
)

from classiq.exceptions import ClassiqValueError

DEFAULT_SUPPORTED_FUNC_NAMES: Set[str] = {"CLShift", "CRShift", "min", "max"}

DEFAULT_EXPRESSION_TYPE = "arithmetic"

_REPEATED_VARIABLES_ERROR_MESSAGE: str = (
    "Repeated variables in the beginning of an arithmetic expression are not allowed."
)


SupportedNodesTypes = Union[
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.BitOr,
    ast.BitAnd,
    ast.BitXor,
    ast.Invert,
    ast.Compare,
    ast.Eq,
    ast.Mod,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.USub,
    ast.UAdd,
    ast.Sub,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.NotEq,
    ast.LShift,
    ast.RShift,
    ast.Call,
    ast.Mult,
]


class ExpressionValidator(ast.NodeVisitor):
    def __init__(
        self,
        supported_nodes,
        expression_type: str = DEFAULT_EXPRESSION_TYPE,
        supported_functions: Optional[Collection[str]] = None,
    ) -> None:
        super().__init__()
        self.supported_nodes = get_args(supported_nodes)
        self._expression_type = expression_type
        self._supported_functions = supported_functions or DEFAULT_SUPPORTED_FUNC_NAMES

    def visit_str(self, expression: str) -> None:
        ast_expr = ast.parse(expression, "", "eval")
        ast_obj = AstNodeRewrite().visit(ast_expr)
        self.visit(ast_obj)

    @staticmethod
    def _check_repeated_variables(variables: Tuple[Any, Any]) -> None:
        if (
            all(isinstance(var, ast.Name) for var in variables)
            and variables[0].id == variables[1].id
        ):
            raise ClassiqValueError(_REPEATED_VARIABLES_ERROR_MESSAGE)

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, self.supported_nodes):
            return super().generic_visit(node)
        raise ClassiqValueError(
            f"{type(node).__name__} is not suitable for {self._expression_type} expression"
        )

    def validate_Compare(self, node: ast.Compare):  # noqa: N802
        self._check_repeated_variables((node.left, node.comparators[0]))

    def visit_Compare(self, node: ast.Compare) -> None:
        self.validate_Compare(node)
        self.generic_visit(node)

    def validate_BinOp(self, node: ast.BinOp) -> None:  # noqa: N802
        self._check_repeated_variables((node.left, node.right))

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.validate_BinOp(node)
        self.generic_visit(node)

    def validate_Call(self, node: ast.Call) -> None:  # noqa: N802
        if len(node.args) >= 2:
            self._check_repeated_variables((node.args[0], node.args[1]))
        node_id = AstNodeRewrite().extract_node_id(node)
        if node_id not in self._supported_functions:
            raise ClassiqValueError(f"{node_id} not in supported functions")

        if node_id in ("CLShift", "CRShift") and (
            len(node.args) != 2 or not isinstance(node.args[1], ast.Constant)
        ):
            raise ClassiqValueError("Cyclic Shift expects 2 arguments (exp, int)")

    def visit_Call(self, node: ast.Call) -> None:
        self.validate_Call(node)
        self.generic_visit(node)

    def validate_Constant(self, node: ast.Constant) -> None:  # noqa: N802
        if not isinstance(node.value, (int, float, complex)):
            raise ClassiqValueError(
                f"{type(node.value).__name__} literals are not valid in arithmetic expressions"
            )

    def visit_Constant(self, node: ast.Constant) -> None:
        self.validate_Constant(node)
        self.generic_visit(node)


def validate_expression(
    expression: str,
    *,
    supported_nodes=SupportedNodesTypes,
    expression_type: str = DEFAULT_EXPRESSION_TYPE,
    supported_functions: Optional[Collection[str]] = None,
) -> None:
    supported_functions = supported_functions or SYMPY_SUPPORTED_EXPRESSIONS.union(
        DEFAULT_SUPPORTED_FUNC_NAMES
    )
    ExpressionValidator(
        supported_nodes, expression_type, supported_functions
    ).visit_str(expression)
