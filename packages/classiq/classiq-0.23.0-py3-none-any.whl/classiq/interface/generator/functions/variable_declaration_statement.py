from classiq.interface.generator.functions import ClassicalType
from classiq.interface.generator.functions.statement import Statement


class VariableDeclaration(Statement):
    name: str
    var_type: ClassicalType
