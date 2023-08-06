"""Executor module, implementing facilities for executing quantum programs using Classiq platform."""

import asyncio
import itertools
import sys
from typing import (
    Awaitable,
    Callable,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from typing_extensions import TypeAlias

from classiq.interface.backend.backend_preferences import BackendPreferencesTypes
from classiq.interface.executor import execution_request
from classiq.interface.executor.aws_execution_cost import (
    ExecutionCostForTimePeriod,
    ExecutionCostForTimePeriodResponse,
)
from classiq.interface.executor.estimation import OperatorsEstimation
from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.executor.execution_request import (
    ExecutionPayloads,
    ExecutionRequest,
    QuantumProgramExecution,
)
from classiq.interface.executor.hamiltonian_minimization_problem import (
    HamiltonianMinimizationProblem,
)
from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq.interface.executor.quantum_program import (
    Arguments,
    MultipleArguments,
    QuantumBaseProgram,
    QuantumProgram,
)
from classiq.interface.executor.result import (
    EstimationResult,
    ExecutionDetails,
    FinanceSimulationResults,
    GroverSimulationResults,
    MultipleExecutionDetails,
    QaeWithQpeResult,
)
from classiq.interface.executor.vqe_result import VQESolverResult
from classiq.interface.generator import finance, grover_operator, identity
from classiq.interface.generator.result import GeneratedCircuit

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import Asyncify, syncify_function
from classiq._internals.registers_initialization import InitialConditions
from classiq.exceptions import ClassiqExecutionError, ClassiqValueError

BatchExecutionResult: TypeAlias = Union[ExecutionDetails, BaseException]
ProgramAndResult: TypeAlias = Tuple[QuantumProgram, BatchExecutionResult]
BackendPreferencesProgramAndResult: TypeAlias = Tuple[
    BackendPreferencesTypes, QuantumProgram, BatchExecutionResult
]

QuantumProgramLike: TypeAlias = Union[
    GeneratedCircuit, QuantumProgram, QuantumBaseProgram, str
]
SpecialExecutionResult: TypeAlias = Union[
    FinanceSimulationResults, GroverSimulationResults
]
SpecialExecutionParams: TypeAlias = Union[
    grover_operator.GroverOperator, finance.Finance
]
SpecialExecutionCallMethod: TypeAlias = Callable[
    [ExecutionRequest], Awaitable[SpecialExecutionResult]
]

_SPECIAL_EXECUTION_METHODS: Dict[
    Type[SpecialExecutionParams], SpecialExecutionCallMethod
] = {
    grover_operator.GroverOperator: ApiWrapper.call_execute_grover,
    finance.Finance: ApiWrapper.call_execute_finance,
}

SINGLE_ARGUMENTS_ERROR_MESSAGE = "Arguments should be provided either as "
"positional arguments, keyword arguments or as a quantum_program. "
"Defining more than one option is not allowed."


class Executor(metaclass=Asyncify):
    """Executor is the entry point for executing quantum programs on multiple quantum hardware vendors."""

    def __init__(
        self, preferences: Optional[ExecutionPreferences] = None, **kwargs
    ) -> None:
        """Init self.

        Args:
            preferences (): Execution preferences, such as number of shots.
        """
        self._preferences = preferences or ExecutionPreferences(**kwargs)

    @property
    def preferences(self) -> ExecutionPreferences:
        return self._preferences

    def _create_payload(
        self, payload: Union[ExecutionPayloads, dict]
    ) -> ExecutionRequest:
        return ExecutionRequest(
            preferences=self._preferences,
            execution_payload=payload,
        )

    @staticmethod
    def _combine_arguments(
        arguments_list: MultipleArguments,
        arguments: MultipleArguments,
        arguments_from_quantum_program: MultipleArguments,
        is_assert_multiple_definitions: bool = False,
    ) -> MultipleArguments:
        # Allow `arguments` to be a single dict, for backwards compatibility
        arguments_as_tuple = (arguments,) if isinstance(arguments, dict) else arguments
        # Allow a single positional arguments which is a tuple of arguments
        #   (This goes agains mypy, since it's parsing `arguments_list` as `Tuple[Tuple[dict]]`, whereas mypy expects `Tuple[dict]`)
        if len(arguments_list) == 1 and isinstance(arguments_list[0], tuple):  # type: ignore[unreachable]
            arguments_list = arguments_list[0]  # type: ignore[unreachable]

        if (
            is_assert_multiple_definitions
            and sum(
                [
                    bool(arguments_list),
                    bool(arguments_as_tuple),
                    bool(arguments_from_quantum_program),
                ]
            )
            > 1
        ):
            raise ClassiqExecutionError(SINGLE_ARGUMENTS_ERROR_MESSAGE)

        return (
            arguments_list or arguments_as_tuple or arguments_from_quantum_program or ()
        )

    def _pre_process_quantum_program_request(
        self,
        quantum_program_like: QuantumProgramLike,
        *arguments_list: Arguments,
        arguments: MultipleArguments = (),
        initial_values: Optional[InitialConditions] = None,
    ) -> ExecutionRequest:
        quantum_program = _convert_to_quantum_program(
            quantum_program_like, initial_values
        )

        quantum_program.arguments = self._combine_arguments(
            arguments_list,
            arguments,
            quantum_program.arguments,
            is_assert_multiple_definitions=True,
        )

        return self._create_payload(quantum_program.dict())

    def _post_process_quantum_program_request(
        self,
        result: MultipleExecutionDetails,
        request: ExecutionRequest,
        arguments_list: MultipleArguments,
        arguments: MultipleArguments,
    ) -> Union[ExecutionDetails, MultipleExecutionDetails]:
        request.execution_payload = cast(
            QuantumProgramExecution, request.execution_payload
        )

        if self._should_return_single_item(
            request.execution_payload, result, arguments_list, arguments
        ):
            return result[0]
        else:
            return result

    def _should_return_single_item(
        self,
        execution_payload: QuantumProgramExecution,
        result: MultipleExecutionDetails,
        arguments_list: MultipleArguments,
        arguments: MultipleArguments,
    ) -> bool:
        is_passed_as_single_arguments = (
            len(arguments_list) == 1 and not arguments
        ) or (isinstance(arguments, dict))

        is_no_arguments_at_all = not self._combine_arguments(
            arguments_list, arguments, execution_payload.arguments
        )

        should_return_single_item = len(result.details) == 1 and (
            is_no_arguments_at_all or is_passed_as_single_arguments
        )
        return should_return_single_item

    async def _execute_quantum_program(
        self,
        quantum_program_like: QuantumProgramLike,
        *arguments_list: Arguments,
        arguments: MultipleArguments = (),
        initial_values: Optional[InitialConditions] = None,
    ) -> Union[ExecutionDetails, MultipleExecutionDetails]:
        request = self._pre_process_quantum_program_request(
            quantum_program_like,
            *arguments_list,
            arguments=arguments,
            initial_values=initial_values,
        )

        result = await ApiWrapper.call_execute_quantum_program(request=request)

        return self._post_process_quantum_program_request(
            result,
            request,
            arguments_list,
            arguments,
        )

    async def batch_execute_quantum_program_async(
        self, quantum_programs: Collection[QuantumProgram]
    ) -> List[ProgramAndResult]:
        results = await asyncio.gather(
            *map(self._execute_quantum_program, quantum_programs),
            return_exceptions=True,
        )
        return list(zip(quantum_programs, results))

    async def _execute_amplitude_estimation(
        self,
        quantum_program_like: QuantumProgramLike,
    ) -> ExecutionDetails:
        quantum_base_program = _convert_to_quantum_base_program(quantum_program_like)

        request = self._create_payload(
            execution_request.AmplitudeEstimationExecution(
                **quantum_base_program.dict()
            )
        )

        return await ApiWrapper.call_execute_amplitude_estimation(request=request)

    async def _execute_amplitude_estimation_with_qpe(
        self,
        circuit: GeneratedCircuit,
    ) -> QaeWithQpeResult:
        request = self._create_payload(
            execution_request.AmplitudeEstimationWithQPEExecution(**circuit.dict())
        )

        return await ApiWrapper.call_execute_amplitude_estimation_with_qpe(
            request=request
        )

    async def _execute_operators_estimation(
        self, operators_estimation: OperatorsEstimation
    ) -> EstimationResult:
        request = self._create_payload(
            execution_request.EstimateOperatorsExecution.parse_obj(operators_estimation)
        )

        return await ApiWrapper.call_execute_estimate(request)

    async def _execute_hamiltonian_minimization(
        self,
        hamiltonian_minimization_problem: HamiltonianMinimizationProblem,
    ) -> VQESolverResult:
        payload = execution_request.HamiltonianMinimizationProblemExecution(
            **hamiltonian_minimization_problem.dict()
        )
        request = ExecutionRequest(
            preferences=self._preferences,
            execution_payload=payload,
        )
        return await ApiWrapper.call_execute_vqe(request=request)

    @staticmethod
    def _extract_special_execution_params(
        generated_circuit: GeneratedCircuit,
    ) -> Optional[SpecialExecutionParams]:
        if not generated_circuit.model:
            return None
        non_identity_params = [
            call.function_params
            for call in generated_circuit.model.logic_flow
            if not isinstance(call.function_params, identity.Identity)
        ]
        if len(non_identity_params) != 1:
            return None
        params = non_identity_params[0]
        return params if type(params) in _SPECIAL_EXECUTION_METHODS else None  # type: ignore[return-value]

    async def _execute_special_params(
        self, generation_result: GeneratedCircuit
    ) -> SpecialExecutionResult:
        special_params = self._extract_special_execution_params(generation_result)
        assert (
            special_params is not None
        )  # this line is here for mypy, since we're sure
        # to enter this functino if this is not None
        api = _SPECIAL_EXECUTION_METHODS[type(special_params)]

        request = self._create_payload(
            execution_request.GeneratedCircuitExecution(**generation_result.dict())
        )

        return await api(request)

    async def _execute_with_qctrl_optimization(
        self,
        quantum_program_like: QuantumProgramLike,
        *arguments_list: Arguments,
        arguments: MultipleArguments = (),
        initial_values: Optional[InitialConditions] = None,
    ) -> Union[ExecutionDetails, MultipleExecutionDetails]:
        if sys.version_info < (3, 8):
            raise ClassiqExecutionError("Cannot run QCtrl with python < 3.8")
        else:
            from classiq import qctrl_execution_tools

            self.preferences.backend_preferences.qctrl_preferences = (
                await qctrl_execution_tools.validate_qctrl(self.preferences)
            )
            return await self._execute_quantum_program(
                quantum_program_like, *arguments_list
            )

    async def execute_async(
        self,
        execution_payload: Union[
            QuantumProgramLike, HamiltonianMinimizationProblem, OperatorsEstimation
        ],
        *args,
        **kwargs,
    ) -> Union[
        VQESolverResult,
        SpecialExecutionResult,
        ExecutionDetails,
        MultipleExecutionDetails,
        EstimationResult,
    ]:
        method: Callable

        if isinstance(execution_payload, HamiltonianMinimizationProblem):
            method = self._execute_hamiltonian_minimization
        elif isinstance(execution_payload, OperatorsEstimation):
            method = self._execute_operators_estimation
        elif (
            isinstance(execution_payload, GeneratedCircuit)
            and self._extract_special_execution_params(execution_payload) is not None
        ):
            method = self._execute_special_params
        elif self._preferences.amplitude_estimation is not None:
            method = self._execute_amplitude_estimation
        elif self._preferences.amplitude_estimation_with_qpe is not None:
            method = self._execute_amplitude_estimation_with_qpe
        elif self.preferences.backend_preferences.qctrl_preferences.use_qctrl:
            method = self._execute_with_qctrl_optimization
        else:
            method = self._execute_quantum_program

        return await method(execution_payload, *args, **kwargs)


def _convert_to_quantum_program(
    arg: QuantumProgramLike,
    initial_values: Optional[InitialConditions] = None,
) -> QuantumProgram:
    if isinstance(arg, GeneratedCircuit):
        program = arg.to_program(initial_values)
    elif isinstance(arg, QuantumProgram):
        program = arg
    elif isinstance(arg, QuantumBaseProgram):
        program = QuantumProgram(**arg.dict())
    elif isinstance(arg, str):
        program = QuantumProgram(code=arg)
    else:
        raise ClassiqValueError("Invalid executor input")

    return program


def _convert_to_quantum_base_program(
    arg: QuantumProgramLike,
) -> QuantumBaseProgram:
    if isinstance(arg, GeneratedCircuit):
        code = arg.to_base_program()
    elif isinstance(arg, QuantumProgram):
        code = QuantumBaseProgram(code=arg.code, syntax=arg.syntax)
    elif isinstance(arg, QuantumBaseProgram):
        code = arg
    elif isinstance(arg, str):
        code = QuantumBaseProgram(code=arg)
    else:
        raise ClassiqValueError("Invalid executor input")

    return code


async def get_aws_execution_cost_async(
    cost_time_period: ExecutionCostForTimePeriod,
) -> ExecutionCostForTimePeriodResponse:
    return await ApiWrapper.get_aws_execution_costs(cost_time_period)


get_aws_execution_cost = syncify_function(get_aws_execution_cost_async)


async def batch_execute_multiple_backends_async(
    preferences_template: ExecutionPreferences,
    backend_preferences: Sequence[BackendPreferencesTypes],
    quantum_programs: Collection[QuantumProgram],
) -> List[BackendPreferencesProgramAndResult]:
    """
    Execute all the provided quantum programs (n) on all the provided backends (m).
    In total, m * n executions.
    The return value is a list of the following tuples:

    - An element from `backend_preferences`
    - An element from `quantum_programs`
    - The execution result of the quantum program on the backend. If the execution failed,
      the value is an exception.

    The length of the list is m * n.

    The `preferences_template` argument is used to supplement all other preferences.

    The code is equivalent to:
    ```
    for backend in backend_preferences:
        for program in quantum_programs:
            preferences = preferences_template.copy()
            preferences.backend_preferences = backend
            Executor(preferences).execute(program)
    ```
    """
    executors = [
        Executor(
            preferences=preferences_template.copy(
                update={"backend_preferences": backend}
            )
        )
        for backend in backend_preferences
    ]
    results = await asyncio.gather(
        *(
            executor.batch_execute_quantum_program_async(quantum_programs)
            for executor in executors
        ),
        return_exceptions=True,
    )

    def map_return_value(
        executor: Executor,
        result: Union[List[ProgramAndResult], BaseException],
    ) -> Iterable[BackendPreferencesProgramAndResult]:
        nonlocal quantum_programs
        preferences = executor.preferences.backend_preferences
        if isinstance(result, BaseException):
            return ((preferences, program, result) for program in quantum_programs)
        else:
            return (
                (preferences, program, single_result)
                for program, single_result in result
            )

    return list(
        itertools.chain.from_iterable(
            map_return_value(executor, result)
            for executor, result in zip(executors, results)
        )
    )


batch_execute_multiple_backends = syncify_function(
    batch_execute_multiple_backends_async
)

__all__ = [
    "QuantumProgram",
    "QuantumInstructionSet",
    "batch_execute_multiple_backends",
    "OperatorsEstimation",
]
