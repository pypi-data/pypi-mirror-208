from typing import ClassVar, Dict, Mapping, Optional

import pydantic

from classiq.interface.generator.functions import ClassicalType
from classiq.interface.generator.functions.function_declaration import (
    FunctionDeclaration,
)


class ClassicalFunctionDeclaration(FunctionDeclaration):
    """
    Facilitates the creation of a common classical function interface object.
    """

    return_type: Optional[ClassicalType] = pydantic.Field(
        description="The type of the classical value that is returned by the function (for classical functions)",
        default=None,
    )

    BUILTIN_FUNCTION_DECLARATIONS: ClassVar[
        Dict[str, "ClassicalFunctionDeclaration"]
    ] = {}

    def update_logic_flow(
        self, function_dict: Mapping[str, "ClassicalFunctionDeclaration"]
    ) -> None:
        pass


ClassicalFunctionDeclaration.update_forward_refs()
