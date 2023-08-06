from typing import List, Union

import pydantic

from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.expression_statement import (
    ExpressionStatement,
)
from classiq.interface.generator.functions.return_statement import ReturnStatement
from classiq.interface.generator.functions.variable_declaration_statement import (
    VariableDeclaration,
)

ClassicalStatement = Union[ExpressionStatement, VariableDeclaration, ReturnStatement]


class ClassicalFunctionDefinition(ClassicalFunctionDeclaration):
    """
    Facilitates the creation of a classical function

    """

    body: List[ClassicalStatement] = pydantic.Field(
        default_factory=list, description="List of statements to perform."
    )
