from typing import List, Optional

from classiq.interface.chemistry import ground_state_problem
from classiq.interface.chemistry.ground_state_problem import (
    CHEMISTRY_PROBLEMS_TYPE,
    GroundStateProblemAndExcitations,
    HamiltonianProblem,
)
from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator.excitations import EXCITATIONS_TYPE

from classiq._internals import async_utils
from classiq._internals.api_wrapper import ApiWrapper


async def generate_hamiltonian_async(
    problem: CHEMISTRY_PROBLEMS_TYPE,
) -> PauliOperator:
    return await ApiWrapper.call_generate_hamiltonian_task(problem)


ground_state_problem.GroundStateProblem.generate_hamiltonian = async_utils.syncify_function(generate_hamiltonian_async)  # type: ignore[attr-defined]
ground_state_problem.GroundStateProblem.generate_hamiltonian_async = generate_hamiltonian_async  # type: ignore[attr-defined]


async def generate_ucc_operators_async(
    problem: CHEMISTRY_PROBLEMS_TYPE,
    excitations: EXCITATIONS_TYPE,
) -> List[PauliOperator]:
    problem_and_excitations = GroundStateProblemAndExcitations(
        problem=problem, excitations=excitations
    )
    pauli_operators = await ApiWrapper.call_generate_ucc_operators_task(
        problem=problem_and_excitations
    )
    return pauli_operators.operators


ground_state_problem.GroundStateProblem.generate_ucc_operators = async_utils.syncify_function(generate_ucc_operators_async)  # type: ignore[attr-defined]
ground_state_problem.GroundStateProblem.generate_ucc_operators_async = generate_ucc_operators_async  # type: ignore[attr-defined]


async def _get_num_qubits(problem: CHEMISTRY_PROBLEMS_TYPE) -> int:
    if isinstance(problem, HamiltonianProblem) and not problem.z2_symmetries:
        return problem.hamiltonian.num_qubits
    hamiltonian = await generate_hamiltonian_async(problem)
    return hamiltonian.num_qubits


async def update_problem_async(
    problem: CHEMISTRY_PROBLEMS_TYPE, num_qubits: Optional[int] = None
) -> CHEMISTRY_PROBLEMS_TYPE:
    if num_qubits is None:
        num_qubits = await _get_num_qubits(problem)
    return problem.copy(update={"num_qubits": num_qubits})


ground_state_problem.GroundStateProblem.update_problem = async_utils.syncify_function(  # type: ignore[attr-defined]
    update_problem_async
)
ground_state_problem.GroundStateProblem.update_problem_async = update_problem_async  # type: ignore[attr-defined]
