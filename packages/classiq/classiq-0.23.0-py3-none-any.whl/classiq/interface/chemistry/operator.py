from functools import reduce
from typing import Any, Collection, Dict, List, Optional, Tuple, Union

import numpy as np
import pydantic
from more_itertools import all_equal

from classiq.interface.generator.complex_type import Complex
from classiq.interface.generator.expressions.pauli import Pauli
from classiq.interface.helpers.custom_pydantic_types import (
    PydanticPauliList,
    PydanticPauliMonomial,
    PydanticPauliMonomialStr,
)
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)
from classiq.interface.helpers.versioned_model import VersionedModel


class PauliOperator(HashablePydanticBaseModel, VersionedModel):
    """
    Specification of a Pauli sum operator.
    """

    pauli_list: PydanticPauliList = pydantic.Field(
        description="A list of tuples each containing a pauli string comprised of I,X,Y,Z characters and a complex coefficient; for example [('IZ', 0.1), ('XY', 0.2)].",
    )
    is_hermitian: bool = pydantic.Field(default=False)

    def show(self) -> str:
        if self.is_hermitian:
            return "\n".join(
                f"{summand[1].real:+.3f} * {summand[0]}" for summand in self.pauli_list
            )
        return "\n".join(
            f"+({summand[1]:+.3f}) * {summand[0]}" for summand in self.pauli_list
        )

    @pydantic.validator("pauli_list", each_item=True)
    def _validate_pauli_monomials(
        cls, monomial: Tuple[PydanticPauliMonomialStr, complex]
    ) -> Tuple[PydanticPauliMonomialStr, complex]:
        _PauliMonomialLengthValidator(  # type: ignore[call-arg]
            monomial=monomial
        )  # Validate the length of the monomial.
        parsed_monomial = _PauliMonomialParser(string=monomial[0], coeff=monomial[1])  # type: ignore[call-arg]
        return (parsed_monomial.string, parsed_monomial.coeff)

    @pydantic.validator("pauli_list")
    def _validate_pauli_list(cls, pauli_list: PydanticPauliList) -> PydanticPauliList:
        if not all_equal(len(summand[0]) for summand in pauli_list):
            raise ValueError("Pauli strings have incompatible lengths.")
        return pauli_list

    @pydantic.root_validator
    def _validate_hermitianity(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        pauli_list = values.get("pauli_list", [])
        values["is_hermitian"] = all(
            np.isclose(complex(summand[1]).real, summand[1]) for summand in pauli_list
        )
        if values.get("is_hermitian", False):
            values["pauli_list"] = [
                (summand[0], complex(summand[1].real)) for summand in pauli_list
            ]
        return values

    def __mul__(self, coefficient: complex) -> "PauliOperator":
        multiplied_ising = [
            (monomial[0], monomial[1] * coefficient) for monomial in self.pauli_list
        ]
        return self.__class__(pauli_list=multiplied_ising)

    @property
    def is_commutative(self) -> bool:
        return all(
            self._is_sub_pauli_commutative(
                [summand[0][qubit_num] for summand in self.pauli_list]
            )
            for qubit_num in range(self.num_qubits)
        )

    @staticmethod
    def _is_sub_pauli_commutative(qubit_pauli_string: Union[List[str], str]) -> bool:
        unique_paulis = set(qubit_pauli_string) - {"I"}
        return len(unique_paulis) <= 1

    @property
    def num_qubits(self) -> int:
        return len(self.pauli_list[0][0])

    def to_matrix(self) -> np.ndarray:
        return sum(
            summand[1] * to_pauli_matrix(summand[0]) for summand in self.pauli_list
        )  # type: ignore[return-value]

    @staticmethod
    def _extend_pauli_string(
        pauli_string: PydanticPauliMonomialStr, num_extra_qubits: int
    ) -> PydanticPauliMonomialStr:
        return "I" * num_extra_qubits + pauli_string

    def extend(self, num_extra_qubits: int) -> "PauliOperator":
        new_pauli_list = [
            (self._extend_pauli_string(pauli_string, num_extra_qubits), coeff)
            for (pauli_string, coeff) in self.pauli_list
        ]
        return self.copy(update={"pauli_list": new_pauli_list}, deep=True)

    @staticmethod
    def _reorder_pauli_string(
        pauli_string: PydanticPauliMonomialStr,
        order: Collection[int],
        new_num_qubits: int,
    ) -> PydanticPauliMonomialStr:
        reversed_pauli_string = pauli_string[::-1]
        reversed_new_pauli_string = ["I"] * new_num_qubits

        for logical_pos, actual_pos in enumerate(order):
            reversed_new_pauli_string[actual_pos] = reversed_pauli_string[logical_pos]

        return "".join(reversed(reversed_new_pauli_string))

    @staticmethod
    def _validate_reorder(
        order: Collection[int],
        num_qubits: int,
        num_extra_qubits: int,
    ) -> None:
        if num_extra_qubits < 0:
            raise ValueError("Number of extra qubits cannot be negative")

        if len(order) != num_qubits:
            raise ValueError("The qubits order doesn't match the Pauli operator")

        if len(order) != len(set(order)):
            raise ValueError("The qubits order is not one-to-one")

        if not all(pos < num_qubits + num_extra_qubits for pos in order):
            raise ValueError("The qubits order contains qubits which do no exist")

    @classmethod
    def reorder(
        cls,
        operator: "PauliOperator",
        order: Collection[int],
        num_extra_qubits: int = 0,
    ) -> "PauliOperator":
        cls._validate_reorder(order, operator.num_qubits, num_extra_qubits)

        new_num_qubits = operator.num_qubits + num_extra_qubits
        new_pauli_list = [
            (cls._reorder_pauli_string(pauli_string, order, new_num_qubits), coeff)
            for pauli_string, coeff in operator.pauli_list
        ]
        return cls(pauli_list=new_pauli_list)

    @classmethod
    def from_unzipped_lists(
        cls,
        operators: List[List[Pauli]],
        coefficients: Optional[List[complex]] = None,
    ) -> "PauliOperator":
        if coefficients is None:
            coefficients = [1] * len(operators)

        if len(operators) != len(coefficients):
            raise ValueError(
                f"The number of coefficients ({len(coefficients)}) must be equal to the number of pauli operators ({len(operators)})"
            )

        return cls(
            pauli_list=[
                (pauli_integers_to_str(op), coeff)
                for op, coeff in zip(operators, coefficients)
            ]
        )

    class Config:
        frozen = True


# This class validates the length of a monomial.
@pydantic.dataclasses.dataclass
class _PauliMonomialLengthValidator:
    monomial: PydanticPauliMonomial


@pydantic.dataclasses.dataclass
class _PauliMonomialParser:
    string: PydanticPauliMonomialStr
    coeff: Complex


_PAULI_MATRICES = {
    "I": np.array([[1, 0], [0, 1]]),
    "X": np.array([[0, 1], [1, 0]]),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.array([[1, 0], [0, -1]]),
}


def to_pauli_matrix(pauli_op: PydanticPauliMonomialStr) -> np.ndarray:
    return reduce(np.kron, [_PAULI_MATRICES[pauli] for pauli in reversed(pauli_op)])


def validate_operator_is_hermitian(pauli_operator: PauliOperator) -> PauliOperator:
    if not pauli_operator.is_hermitian:
        raise ValueError("Coefficients of the Hamiltonian must be real numbers")
    return pauli_operator


def pauli_integers_to_str(paulis: List[Pauli]) -> str:
    return "".join([Pauli(pauli).name for pauli in paulis])


class PauliOperators(VersionedModel):
    operators: List[PauliOperator]
