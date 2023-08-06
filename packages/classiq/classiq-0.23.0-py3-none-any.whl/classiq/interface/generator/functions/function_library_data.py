from typing import Any, Dict, List, Union

import pydantic
from more_itertools import locate

from classiq.interface.generator.functions.foreign_function_definition import (
    ForeignFunctionDefinition,
)
from classiq.interface.generator.functions.function_declaration import (
    validate_name_end_not_newline,
)
from classiq.interface.generator.functions.native_function_definition import (
    NativeFunctionDefinition,
)
from classiq.interface.generator.functions.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)
from classiq.interface.generator.user_defined_function_params import CustomFunction
from classiq.interface.helpers.custom_pydantic_types import PydanticFunctionNameStr
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)

DEFAULT_FUNCTION_LIBRARY_NAME = "default_function_library_name"


# We need to define ConcreteFunctionData so pydantic will know
# what class to use when deserializing from object (pydantic attempts to
# parse as each of the classes in the Union, in order).
ConcreteFunctionDefinition = Union[ForeignFunctionDefinition, NativeFunctionDefinition]


class FunctionLibraryData(HashablePydanticBaseModel):
    """Facility to store user-defined custom functions."""

    name: PydanticFunctionNameStr = pydantic.Field(
        default=DEFAULT_FUNCTION_LIBRARY_NAME,
        description="The name of the custom function library",
    )

    functions: List[ConcreteFunctionDefinition] = pydantic.Field(
        default_factory=list,
        description="A list of the function definitions in the library",
    )

    def add_function_definition(self, func_def: QuantumFunctionDeclaration):
        self.functions.append(func_def)  # type:ignore[arg-type]

    def remove_function_definition(self, name: str):
        idx = list(locate(self.functions, lambda func: func.name == name))
        assert len(idx) == 1
        self.functions.pop(idx[0])

    @pydantic.validator("name")
    def validate_name(cls, name: str) -> str:
        validate_name_end_not_newline(name=name)
        return name

    @pydantic.validator("functions")
    def validate_functions(cls, functions: List[ConcreteFunctionDefinition]):
        functions_dict = _user_functions_to_declaration_dict(functions)

        for name, fd in functions_dict.items():
            if isinstance(fd, NativeFunctionDefinition):
                functions_dict[name] = fd.resolve_expressions()

        for fd in functions_dict.values():
            fd.update_logic_flow(functions_dict)

        return list(functions_dict.values())

    @property
    def function_dict(self) -> Dict[str, QuantumFunctionDeclaration]:
        return _user_functions_to_declaration_dict(self.functions)

    def __contains__(self, obj: Any) -> bool:
        if isinstance(obj, str):
            return obj in self.function_dict
        elif isinstance(obj, CustomFunction):
            return obj.name in self.function_dict
        elif isinstance(obj, QuantumFunctionDeclaration):
            return obj in self.function_dict.values()
        else:
            return False

    class Config:
        frozen = True


def _user_functions_to_declaration_dict(
    functions: List[ConcreteFunctionDefinition],
) -> Dict[PydanticFunctionNameStr, QuantumFunctionDeclaration]:
    return {function.name: function for function in functions}
