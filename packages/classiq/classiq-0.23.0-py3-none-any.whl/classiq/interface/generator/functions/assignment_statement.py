import pydantic

from classiq.interface.generator.functions.expression_statement import (
    ExpressionStatement,
)
from classiq.interface.helpers.custom_pydantic_types import PydanticNonEmptyString


class AssignmentStatement(ExpressionStatement):
    assigned_variable: PydanticNonEmptyString = pydantic.Field(
        description="The variable to assign the result of the invoked expression (left hand side)"
    )
