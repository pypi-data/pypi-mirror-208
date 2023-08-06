import enum
from typing import Dict

from sympy import Basic, Integer


class Optimizer(int, enum.Enum):
    COBYLA = 1
    SPSA = 2
    L_BFGS_B = 3
    NELDER_MEAD = 4
    ADAM = 5

    def to_sympy(self) -> Basic:
        return Integer(self.value)

    @staticmethod
    def sympy_locals() -> Dict[str, Basic]:
        return {
            f"Optimizer_{optimizer.name}": optimizer.to_sympy()
            for optimizer in Optimizer
        }
