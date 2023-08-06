"""Model module, implementing facilities for designing models and generating circuits using Classiq platform."""
from __future__ import annotations

import logging
import tempfile
from contextlib import nullcontext
from typing import IO, AnyStr, ContextManager, Dict, List, Mapping, Optional, Union

from classiq.interface.generator import result
from classiq.interface.generator.function_params import IOName
from classiq.interface.generator.functions import NativeFunctionDefinition
from classiq.interface.generator.model import (
    Constraints,
    Model as APIModel,
    Preferences,
)
from classiq.interface.generator.model.model import MAIN_FUNCTION_NAME
from classiq.interface.generator.quantum_function_call import QuantumFunctionCall

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import AsyncifyABC
from classiq.model import function_handler
from classiq.quantum_functions.function_library import FunctionLibrary
from classiq.quantum_register import QReg, QRegGenericAlias

_logger = logging.getLogger(__name__)

_SupportedIO = Union[IO, str]

# TODO: Add docstrings for auto generated methods.


def _file_handler(fp: Optional[_SupportedIO], mode: str = "r") -> ContextManager[IO]:
    if fp is None:
        temp_file = tempfile.NamedTemporaryFile(mode, suffix=".qmod", delete=False)
        print(f"Using temporary file: {temp_file.name!r}")
        return temp_file

    if isinstance(fp, str):
        return open(fp, mode)

    return nullcontext(fp)


class Model(function_handler.FunctionHandler, metaclass=AsyncifyABC):
    """Facility to generate circuits, based on the model."""

    def __init__(self, **kwargs) -> None:
        """Init self."""
        super().__init__()
        self._model = APIModel(**kwargs)

    @classmethod
    def from_model(cls, model: APIModel) -> Model:
        return cls(**dict(model))

    @property
    def _logic_flow(
        self,
    ) -> List[QuantumFunctionCall]:
        return self._model.logic_flow

    @property
    def constraints(self) -> Constraints:
        """Get the constraints aggregated in self.

        Returns:
            The constraints data.
        """
        return self._model.constraints

    @property
    def preferences(self) -> Preferences:
        """Get the preferences aggregated in self.

        Returns:
            The preferences data.
        """
        return self._model.preferences

    def create_inputs(
        self, inputs: Mapping[IOName, QRegGenericAlias]
    ) -> Dict[IOName, QReg]:
        qregs = super().create_inputs(inputs=inputs)
        self._model.set_inputs(self.input_wires)
        return qregs

    def set_outputs(self, outputs: Mapping[IOName, QReg]) -> None:
        super().set_outputs(outputs=outputs)
        self._model.set_outputs(self.output_wires)

    async def synthesize_async(
        self,
        constraints: Optional[Constraints] = None,
        preferences: Optional[Preferences] = None,
    ) -> result.GeneratedCircuit:
        """Async version of `generate`
        Generates a circuit, based on the aggregation of requirements in self.

        Returns:
            The results of the generation procedure.
        """
        self._model.preferences = preferences or self._model.preferences
        self._model.constraints = constraints or self._model.constraints
        return await ApiWrapper.call_generation_task(self._model)

    def include_library(self, library: FunctionLibrary) -> None:
        """Includes a user-defined custom function library.

        Args:
            library (FunctionLibrary): The custom function library.
        """
        super().include_library(library=library)
        self._model.function_library = library.data
        self._model.function_library.remove_function_definition(MAIN_FUNCTION_NAME)
        self._model.function_library.add_function_definition(
            NativeFunctionDefinition(name=MAIN_FUNCTION_NAME)
        )

    def dumps(self, ignore_warning: bool = False) -> str:
        """Serialize model to a JSON formatted `str`

        Args:
            ignore_warning (bool): Whether to ignore the warning print
        """
        if not ignore_warning:
            _logger.warning(
                "Saving to json is currently unstable since versions may change"
            )

        return self._model.json(exclude_defaults=True, indent=4)

    def dump(
        self, fp: Optional[_SupportedIO] = None, ignore_warning: bool = False
    ) -> None:
        """Serialize model to a JSON formatted stream to `fp` (a `.write()`)-supporting file-like object

        Args:
            fp (IO | str | None): a file-like object
                if None -> a temporaty file will be created
                if str -> this will be treated as the file path
            ignore_warning (bool): Whether to ignore the warning print
        """
        with _file_handler(fp, "w") as f:
            f.write(self.dumps(ignore_warning=ignore_warning))

    @classmethod
    def loads(cls, s: AnyStr) -> Model:
        """Deserialize `s`, a JSON formatted `str`, to a Model

        Args:
            s (str | bytes): A JSON-formatted `str` | `bytes`
        """
        new_instance = cls()
        new_instance._model = APIModel.parse_raw(s)
        return new_instance

    @classmethod
    def load(cls, fp: Optional[_SupportedIO]) -> Model:
        """Deserialize `fp` (a `.read()`-supporting file-like object) containing a JSON formatted document to a Model

        Args:
            fp (IO | str): a file-like object
                if str -> this will be treated as the file path
        """
        with _file_handler(fp, "r") as f:
            return cls.loads(f.read())

    def create_library(self) -> None:
        self._function_library = FunctionLibrary(
            *self._model.function_library.functions
        )
        self._model.function_library = self._function_library.data
