import enum
import warnings
from datetime import datetime
from pathlib import Path
from typing import Collection, Dict, List, Optional, Tuple, Union

import pydantic
from typing_extensions import TypeAlias

from classiq.interface.backend.backend_preferences import BackendPreferences
from classiq.interface.backend.quantum_backend_providers import ProviderVendor
from classiq.interface.executor import quantum_program
from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq.interface.executor.register_initialization import RegisterInitialization
from classiq.interface.generator.generated_circuit_data import GeneratedCircuitData
from classiq.interface.generator.model.model import Model
from classiq.interface.generator.model.preferences.preferences import (
    CustomHardwareSettings,
    QuantumFormat,
)
from classiq.interface.helpers.versioned_model import VersionedModel

from classiq._internals.registers_initialization import (
    GeneratedRegister,
    InitialConditions,
    RegisterCategory,
    RegisterName,
    get_registers_from_generated_functions,
)
from classiq.exceptions import ClassiqMissingOutputFormatError

_MAXIMUM_STRING_LENGTH = 250

Code: TypeAlias = str
CodeAndSyntax: TypeAlias = Tuple[Code, QuantumInstructionSet]

_INSTRUCTION_SET_TO_FORMAT: Dict[QuantumInstructionSet, QuantumFormat] = {
    QuantumInstructionSet.QASM: QuantumFormat.QASM,
    QuantumInstructionSet.QSHARP: QuantumFormat.QSHARP,
    QuantumInstructionSet.IONQ: QuantumFormat.IONQ,
}
_VENDOR_TO_INSTRUCTION_SET: Dict[str, QuantumInstructionSet] = {
    ProviderVendor.IONQ: QuantumInstructionSet.IONQ,
    ProviderVendor.AZURE_QUANTUM: QuantumInstructionSet.QSHARP,
    ProviderVendor.IBM_QUANTUM: QuantumInstructionSet.QASM,
    ProviderVendor.NVIDIA: QuantumInstructionSet.QASM,
    ProviderVendor.AMAZON_BRAKET: QuantumInstructionSet.QASM,
}
_DEFAULT_INSTRUCTION_SET = QuantumInstructionSet.QASM


class LongStr(str):
    def __repr__(self):
        if len(self) > _MAXIMUM_STRING_LENGTH:
            length = len(self)
            return f'"{self[:4]}...{self[-4:]}" (length={length})'
        return super().__repr__()


class QasmVersion(str, enum.Enum):
    V2 = "2.0"
    V3 = "3.0"


class HardwareData(pydantic.BaseModel):
    _is_default: bool = pydantic.PrivateAttr(default=False)
    custom_hardware_settings: CustomHardwareSettings
    backend_preferences: Optional[BackendPreferences]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._is_default = (
            self.custom_hardware_settings.is_default
            and self.backend_preferences is None
        )

    @property
    def is_default(self) -> bool:
        return self._is_default


class CircuitWithOutputFormats(pydantic.BaseModel):
    outputs: Dict[QuantumFormat, Code]
    qasm_version: QasmVersion

    @pydantic.validator("outputs")
    def reformat_long_string_output_formats(
        cls, outputs: Dict[QuantumFormat, str]
    ) -> Dict[QuantumFormat, LongStr]:
        return {key: LongStr(value) for key, value in outputs.items()}

    @property
    def qasm(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QASM)

    @property
    def qsharp(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QSHARP)

    @property
    def qir(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QIR)

    @property
    def ionq(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.IONQ)

    @property
    def cirq_json(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.CIRQ_JSON)

    @property
    def qasm_cirq_compatible(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QASM_CIRQ_COMPATIBLE)

    @property
    def output_format(self) -> List[QuantumFormat]:
        return list(self.outputs.keys())


class TranspiledCircuitData(CircuitWithOutputFormats):
    depth: int
    count_ops: Dict[str, int]
    logical_to_physical_input_qubit_map: List[int]
    logical_to_physical_output_qubit_map: List[int]


class GeneratedCircuit(VersionedModel, CircuitWithOutputFormats):
    transpiled_circuit: Optional[TranspiledCircuitData]
    interactive_html: Optional[str]
    data: GeneratedCircuitData
    analyzer_data: Dict
    hardware_data: HardwareData
    model: Model
    creation_time: str = pydantic.Field(default_factory=datetime.utcnow().isoformat)

    def show_interactive(self) -> None:
        warnings.warn(
            "The `show_interactive()` method is deprecated."
            "Use the `show()` method instead",
            DeprecationWarning,
            stacklevel=1,
        )
        self.show()  # type: ignore[attr-defined]

    def save_results(self, filename: Optional[Union[str, Path]] = None) -> None:
        """
        Saves generated circuit results as json.
            Parameters:
                filename (Union[str, Path]): Optional, path + filename of file.
                                             If filename supplied add `.json` suffix.

            Returns:
                  None
        """
        if filename is None:
            filename = f"synthesised_circuit_{self.creation_time}.json"

        with open(filename, "w") as file:
            file.write(self.json(indent=4))

    @staticmethod
    def _get_code_by_priority_from_outputs(
        outputs: Dict[QuantumFormat, Code]
    ) -> Optional[CodeAndSyntax]:
        for instruction_set, quantum_format in _INSTRUCTION_SET_TO_FORMAT.items():
            code = outputs.get(quantum_format)
            if code is not None:
                return code, instruction_set

        return None

    def _hardware_unaware_program_code(self) -> CodeAndSyntax:
        if self.transpiled_circuit:
            transpiled_circuit_code = self._get_code_by_priority_from_outputs(
                self.transpiled_circuit.outputs
            )
            if transpiled_circuit_code is not None:
                return transpiled_circuit_code

        circuit_code = self._get_code_by_priority_from_outputs(self.outputs)
        if circuit_code is not None:
            return circuit_code

        raise ClassiqMissingOutputFormatError(
            missing_formats=list(_INSTRUCTION_SET_TO_FORMAT.values())
        )

    def _default_program_code(self) -> CodeAndSyntax:
        if self.hardware_data.backend_preferences is None:
            return self._hardware_unaware_program_code()

        backend_provider = (
            self.hardware_data.backend_preferences.backend_service_provider
        )
        instruction_set: QuantumInstructionSet = _VENDOR_TO_INSTRUCTION_SET.get(
            backend_provider, _DEFAULT_INSTRUCTION_SET
        )
        return self._get_code(instruction_set), instruction_set

    def _get_code(self, instruction_set: QuantumInstructionSet) -> Code:
        quantum_format: QuantumFormat = _INSTRUCTION_SET_TO_FORMAT[instruction_set]
        code = (
            self.transpiled_circuit.outputs.get(quantum_format)
            if self.transpiled_circuit
            else self.outputs.get(quantum_format)
        )
        if code is None:
            raise ClassiqMissingOutputFormatError(missing_formats=[quantum_format])
        return code

    def to_base_program(self) -> quantum_program.QuantumBaseProgram:
        code, syntax = self._default_program_code()
        return quantum_program.QuantumBaseProgram(code=code, syntax=syntax)

    def to_program(
        self,
        initial_values: Optional[InitialConditions] = None,
        instruction_set: Optional[QuantumInstructionSet] = None,
    ) -> quantum_program.QuantumProgram:
        if instruction_set is not None:
            code, syntax = self._get_code(instruction_set), instruction_set
        else:
            code, syntax = self._default_program_code()

        if initial_values is not None:
            registers_initialization = self.get_registers_initialization(
                initial_values=initial_values
            )
        else:
            registers_initialization = None
        return quantum_program.QuantumProgram(
            code=code,
            syntax=syntax,
            output_qubits_map=self.data.qubit_mapping.physical_outputs,
            registers_initialization=registers_initialization,
        )

    def get_registers(
        self,
        register_category: RegisterCategory,
        register_names: Collection[RegisterName],
    ) -> List[GeneratedRegister]:
        return get_registers_from_generated_functions(
            generated_functions=self.data.generated_functions,
            register_names=register_names,
            register_category=register_category,
        )

    def get_registers_initialization(
        self,
        initial_values: InitialConditions,
    ) -> Dict[RegisterName, RegisterInitialization]:
        registers = self.get_registers(
            register_names=initial_values.keys(),
            register_category=RegisterCategory.DANGLING_INPUTS,
        )
        registers_initialization = RegisterInitialization.initialize_registers(
            registers=registers, initial_conditions=initial_values
        )
        return registers_initialization

    @pydantic.validator("interactive_html")
    def reformat_long_strings(cls, v):
        if v is None:
            return v
        return LongStr(v)
