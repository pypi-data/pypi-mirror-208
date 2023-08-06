from typing import List, Tuple

from classiq.interface.generator.expressions import pauli
from classiq.interface.generator.functions.classical_type import (
    ClassicalList,
    Pauli,
    Real,
)
from classiq.interface.generator.types.struct_declaration import StructDeclaration

PAULI_TERM = StructDeclaration(
    name="PauliTerm",
    variables={
        "pauli": ClassicalList(element_type=Pauli()),
        "coefficient": Real(),
    },
)

# Following are type aliases provided as convenience for Qmod user-defined foreign
# functions with Pauli-based Hamiltonian parameters/return values

QmodPyPauliTerm = Tuple[List[pauli.Pauli], float]

QmodPyHamiltonian = List[QmodPyPauliTerm]
