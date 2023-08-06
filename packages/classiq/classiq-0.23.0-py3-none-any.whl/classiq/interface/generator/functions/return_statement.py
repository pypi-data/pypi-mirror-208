import pydantic

from classiq.interface.generator.functions.statement import Statement


class ReturnStatement(Statement):
    returned_variable: str = pydantic.Field(
        description="The name of the variable to be returned by the enclosing function."
    )
