import enum
from typing import Dict

from sympy import Basic, Integer


class Pauli(int, enum.Enum):
    I = 0  # noqa: E741
    X = 1
    Y = 2
    Z = 3

    def to_sympy(self) -> Basic:
        return Integer(self.value)

    @staticmethod
    def sympy_locals() -> Dict[str, Basic]:
        return {f"Pauli_{pauli.name}": pauli.to_sympy() for pauli in Pauli}
