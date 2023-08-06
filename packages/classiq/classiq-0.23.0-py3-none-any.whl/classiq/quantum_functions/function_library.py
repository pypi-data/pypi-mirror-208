"""Function library module, implementing facilities for adding user defined functions to the Classiq platform."""
from typing import Any, Dict, Tuple, Type, Union

from classiq.interface.generator.functions import (
    DEFAULT_FUNCTION_LIBRARY_NAME,
    ForeignFunctionDefinition,
    FunctionLibraryData,
    NativeFunctionDefinition,
    QuantumFunctionDeclaration,
)
from classiq.interface.generator.model.model import MAIN_FUNCTION_NAME
from classiq.interface.generator.user_defined_function_params import CustomFunction

from classiq.exceptions import ClassiqValueError
from classiq.quantum_functions.quantum_function import (
    QuantumFunction,
    QuantumFunctionFactory,
)

QASM_INTRO = 'OPENQASM 2.0;\ninclude "qelib1.inc";\n'
QASM3_INTRO = 'OPENQASM 3.0;\ninclude "stdgates.inc";\n'

_INVALID_FUNCTION_LIBRARY_ARGUMENT_ERROR_MSG: str = (
    "Argument is not a valid FunctionLibrary object"
)


class FunctionLibrary:
    """Facility to manage functions."""

    def __init__(self, *functions, name: str = DEFAULT_FUNCTION_LIBRARY_NAME) -> None:
        """
        Args:
            name (:obj:`str`, optional): The name of the function library.
            *functions (:obj:`QuantumFunctionDeclaration`, optional): A list of functions to initialize the object.
        """
        self._data = FunctionLibraryData(name=name)
        self._params: Dict[str, CustomFunction] = dict()
        self._func_factories: Dict[str, Type[QuantumFunctionFactory]] = dict()

        for f in functions:
            self.add_function(f)

        if MAIN_FUNCTION_NAME not in self._data.function_dict:
            self.add_function(NativeFunctionDefinition(name=MAIN_FUNCTION_NAME))

    def get_function(self, function_name: str) -> CustomFunction:
        return self._params[function_name]

    def get_function_factory(
        self, function_factory_name: str
    ) -> Type[QuantumFunctionFactory]:
        return self._func_factories[function_factory_name]

    def __getitem__(self, key: Any) -> CustomFunction:
        if isinstance(key, str):
            return self.get_function(key)
        else:
            raise ClassiqValueError("Invalid key")

    def add_function(
        self,
        function_data: Union[
            QuantumFunctionDeclaration, QuantumFunction, Type[QuantumFunctionFactory]
        ],
        override_existing_functions: bool = False,
    ) -> None:
        """Adds a function to the function library.

        Args:
            function_data (QuantumFunctionDeclaration): The function data object.
            override_existing_functions (:obj:`bool`, optional): Defaults to False.

        Returns:
            None
        """
        if isinstance(function_data, type) and issubclass(
            function_data, QuantumFunctionFactory
        ):
            self._func_factories[function_data.__name__] = function_data
            return
        if isinstance(function_data, QuantumFunction):
            function_data = function_data.function_data

        if not isinstance(
            function_data, (ForeignFunctionDefinition, NativeFunctionDefinition)
        ):
            raise ClassiqValueError(
                f"Concrete function definition object expected, got {function_data.__class__.__name__}"
            )

        function_name = function_data.name
        if (
            not override_existing_functions
            and function_name in self._data.function_dict
        ):
            raise ClassiqValueError("Cannot override existing functions.")

        if isinstance(function_data, NativeFunctionDefinition):
            for call in filter(
                lambda i: isinstance(i.function_params, CustomFunction),
                function_data.logic_flow,
            ):
                if self._data and call.function not in self.data:
                    raise ClassiqValueError(
                        "FunctionLibrary: The function is not found in included library."
                    )

        self._data.add_function_definition(function_data)
        self._params[function_name] = self._to_params(function_data)

    @property
    def name(self) -> str:
        """The library name."""
        return self._data.name

    @property
    def function_names(self) -> Tuple[str, ...]:
        """Get a tuple of the names of the functions in the library.

        Returns:
            The names of the functions in the library.
        """
        return tuple(self._data.function_dict.keys())

    @property
    def function_factory_names(self) -> Tuple[str, ...]:
        return tuple(self._func_factories.keys())

    @property
    def data(self) -> FunctionLibraryData:
        return self._data

    @staticmethod
    def _to_params(data: QuantumFunctionDeclaration) -> CustomFunction:
        parameters = (
            data.parameters if isinstance(data, NativeFunctionDefinition) else list()
        )
        params = CustomFunction(
            parameters=parameters,
            input_decls=data.inputs,
            output_decls=data.outputs,
        )
        return params

    def __add__(self, other: "FunctionLibrary") -> "FunctionLibrary":
        if not isinstance(other, FunctionLibrary):
            raise ClassiqValueError(_INVALID_FUNCTION_LIBRARY_ARGUMENT_ERROR_MSG)
        joint_library = FunctionLibrary(name=f"{self.name}_and_{other.name}")
        for library in (self, other):
            for func in library.data.functions:
                if (
                    func.name == MAIN_FUNCTION_NAME
                    or func.name in joint_library.function_names
                ):
                    continue
                joint_library.add_function(func)
        return joint_library

    def __iadd__(self, other: "FunctionLibrary") -> "FunctionLibrary":
        if not isinstance(other, FunctionLibrary):
            raise ClassiqValueError(_INVALID_FUNCTION_LIBRARY_ARGUMENT_ERROR_MSG)
        for func in other.data.functions:
            if func.name == MAIN_FUNCTION_NAME or func.name in self.function_names:
                continue
            self.add_function(func)
        return self
