import functools
import operator
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional, Tuple
from uuid import UUID

import pydantic
from pydantic import BaseModel

from classiq.interface.executor.quantum_program import OutputQubitsMap, Qubits
from classiq.interface.generator.arith import number_utils
from classiq.interface.generator.complex_type import Complex
from classiq.interface.generator.generated_circuit_data import GeneratedRegister
from classiq.interface.helpers.custom_pydantic_types import PydanticNonNegIntTuple
from classiq.interface.helpers.versioned_model import VersionedModel
from classiq.interface.jobs import JobDescription

from classiq.exceptions import ClassiqError

_ILLEGAL_QUBIT_ERROR_MSG: str = "Illegal qubit index requested"
_REPEATED_QUBIT_ERROR_MSG: str = "Requested a qubit more than once"
_UNAVAILABLE_OUTPUT_ERROR_MSG: str = "Requested output doesn't exist in the circuit"

State = str
Name = str
RegisterValue = float
Counts = Dict[State, pydantic.NonNegativeInt]


class VaRResult(BaseModel):
    var: Optional[float] = None
    alpha: Optional[float] = None


class FinanceSimulationResults(VersionedModel):
    var_results: Optional[VaRResult] = None
    result: Optional[float] = None

    @pydantic.root_validator()
    def validate_atleast_one_field(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        is_var_results_defined = values.get("var_results") is not None
        is_result_defined = values.get("result") is not None

        if not is_var_results_defined and not is_result_defined:
            raise ValueError(
                "At least one of var_results and result should be defined."
            )

        return values


class GroverSimulationResults(VersionedModel):
    result: Dict[str, Any]


def _validate_qubit_indices(counts: Counts, indices: Tuple[int, ...]) -> None:
    if not indices:
        raise ClassiqError(_ILLEGAL_QUBIT_ERROR_MSG)

    if max(indices) >= len(list(counts.keys())[0]):
        raise ClassiqError(_ILLEGAL_QUBIT_ERROR_MSG)

    if len(set(indices)) < len(indices):
        raise ClassiqError(_REPEATED_QUBIT_ERROR_MSG)


def _slice_str(s: str, indices: Tuple[int, ...]) -> str:
    return "".join(s[i] for i in indices)


class ExecutionDetails(VersionedModel):
    vendor_format_result: Dict[str, Any] = pydantic.Field(
        ..., description="Result in proprietary vendor format"
    )
    counts: Counts = pydantic.Field(
        default_factory=dict, description="Number of counts per state"
    )
    histogram: Optional[Dict[State, pydantic.NonNegativeFloat]] = pydantic.Field(
        None,
        description="Histogram of probability per state (an alternative to counts)",
    )
    output_qubits_map: OutputQubitsMap = pydantic.Field(
        default_factory=dict,
        description="The map of outputs to their qubits in the circuit.",
    )
    state_vector: Optional[Dict[str, Any]] = pydantic.Field(
        None, description="The state vector when executed on a simulator"
    )

    @pydantic.validator("counts", pre=True)
    def clean_spaces_from_counts_keys(cls, v: Counts):
        if not v or " " not in list(v.keys())[0]:
            return v
        return {state.replace(" ", ""): v[state] for state in v}

    def flip_execution_counts_bitstring(self) -> None:
        """Backends should return result count bitstring in right to left form"""
        self.counts = {key[::-1]: value for key, value in self.counts.items()}

    def counts_of_qubits(self, *qubits: int) -> Counts:
        _validate_qubit_indices(self.counts, qubits)

        reduced_counts: DefaultDict[State, int] = defaultdict(int)
        for state_str, state_count in self.counts.items():
            reduced_counts[_slice_str(state_str, qubits)] += state_count

        return dict(reduced_counts)

    def counts_of_output(self, output_name: Name) -> Counts:
        if output_name not in self.output_qubits_map:
            raise ClassiqError(_UNAVAILABLE_OUTPUT_ERROR_MSG)

        return self.counts_of_qubits(*self.output_qubits_map[output_name])

    def counts_of_multiple_outputs(
        self, output_names: Tuple[Name, ...]
    ) -> Dict[Tuple[State, ...], pydantic.NonNegativeInt]:
        if any(name not in self.output_qubits_map for name in output_names):
            raise ClassiqError(_UNAVAILABLE_OUTPUT_ERROR_MSG)

        output_regs: Tuple[Qubits, ...] = tuple(
            self.output_qubits_map[name] for name in output_names
        )
        reduced_counts: DefaultDict[Tuple[State, ...], int] = defaultdict(int)
        for state_str, state_count in self.counts.items():
            reduced_strs = tuple(_slice_str(state_str, reg) for reg in output_regs)
            reduced_counts[reduced_strs] += state_count
        return dict(reduced_counts)

    def register_output_from_result(
        self, register_data: GeneratedRegister
    ) -> Dict[float, int]:
        register_output: Dict[float, int] = {}
        value_from_str_bin = functools.partial(
            self._get_register_value_from_binary_string_results,
            register_qubits=register_data.qubit_indexes_absolute,
        )
        for results_binary_key, counts in self.counts.items():
            value = value_from_str_bin(binary_string=results_binary_key)
            register_output[value] = register_output.get(value, 0) + counts

        return register_output

    @staticmethod
    def _get_register_value_from_binary_string_results(
        binary_string: str, register_qubits: List[int]
    ) -> RegisterValue:
        register_binary_string = "".join(
            operator.itemgetter(*register_qubits)(binary_string)
        )[::-1]
        return number_utils.binary_to_float_or_int(bin_rep=register_binary_string)


class MultipleExecutionDetails(VersionedModel):
    details: List[ExecutionDetails]

    def __getitem__(self, index) -> ExecutionDetails:
        return self.details[index]


class GroverAdaptiveSearchResult(VersionedModel):
    opt_x_string: List[int] = pydantic.Field(
        ..., description="Result in proprietary vendor format"
    )
    min_value: float = pydantic.Field(
        ..., description="Result in proprietary vendor format"
    )


class QaeWithQpeResult(ExecutionDetails):
    probability_estimation: float = pydantic.Field(
        ..., description="Probability estimation"
    )


class EstimationMetadata(VersionedModel, extra=pydantic.Extra.allow):
    shots: Optional[pydantic.NonNegativeInt] = None
    remapped_qubits: bool = False
    input_qubit_map: Optional[List[PydanticNonNegIntTuple]] = None


class EstimationResult(VersionedModel):
    value: List[Complex] = pydantic.Field(
        ..., description="Estimates for the operators"
    )
    variance: List[Complex] = pydantic.Field(
        ..., description="Standard deviation of the estimates"
    )
    metadata: Optional[List[EstimationMetadata]] = pydantic.Field(
        None, description="Metadata for the estimation"
    )

    @pydantic.root_validator()
    def validate_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        value = values.get("value")
        variance = values.get("variance")
        if len(value) != len(variance):  # type: ignore[arg-type]
            raise ValueError("Value and variance lists should have the same length.")
        metadata = values.get("metadata")
        if metadata is not None and len(value) != len(  # type: ignore[arg-type]
            metadata
        ):
            raise ValueError(
                "If metadata list is defined, it should have the same length of value."
            )
        return values


class ExecutionJobDescription(VersionedModel, JobDescription[Dict[str, Any]]):
    job_uuid: UUID
