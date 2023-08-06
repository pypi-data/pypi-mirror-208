from typing import Optional, Union

import pydantic

from classiq.interface.generator.classical_function_call import ClassicalFunctionCall
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.statement import Statement

ConcreteExpression = Union[Expression, ClassicalFunctionCall]


class ExpressionStatement(Statement):
    invoked_expression: ConcreteExpression = pydantic.Field(
        description="The expression this statement invokes."
    )

    _evaluation_result: Optional[Expression] = pydantic.PrivateAttr(default=None)
