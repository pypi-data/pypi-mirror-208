from enum import Enum
from typing import FrozenSet

from classiq.interface.generator.preferences.optimization import (
    StatePrepOptimizationMethod,
)

_AMPLITUDE_SUPPORTING_METRICS: FrozenSet = frozenset(
    {"L2", "L1", "MAX_PROBABILITY", "TOTAL_VARIATION"}
)


class Metrics(str, Enum):
    KL = "KL"
    L2 = "L2"
    L1 = "L1"
    MAX_PROBABILITY = "MAX_PROBABILITY"
    LOSS_OF_FIDELITY = "LOSS_OF_FIDELITY"
    TOTAL_VARIATION = "TOTAL_VARIATION"
    HELLINGER = "HELLINGER"
    BHATTACHARYYA = "BHATTACHARYYA"

    @classmethod
    def from_sp_optimization_method(
        cls, sp_opt_method: StatePrepOptimizationMethod
    ) -> "Metrics":
        try:
            return Metrics(sp_opt_method.value)
        except ValueError:
            raise ValueError(
                f"Failed to convert {sp_opt_method} to an error metric"
            ) from None

    @property
    def supports_amplitudes(self) -> bool:
        return self.value in _AMPLITUDE_SUPPORTING_METRICS
