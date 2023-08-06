import pydantic

from classiq.interface.generator.functions import QuantumFunctionDeclaration
from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)


class QuantumInvokerDeclaration(ClassicalFunctionDeclaration):
    target_function: QuantumFunctionDeclaration = pydantic.Field(
        description="The invoked quantum function's declaration."
    )
