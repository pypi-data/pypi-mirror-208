import math
from typing import List, Optional

import pydantic

from classiq.interface.finance.model_input import FinanceModelInput
from classiq.interface.helpers.custom_pydantic_types import PydanticProbabilityFloat


class GaussianModelInput(FinanceModelInput):
    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits represent"
        "the latent normal random variable Z (Resolution of "
        "the random variable Z)."
    )
    normal_max_value: float = pydantic.Field(
        description="Min/max value to truncate the " "latent normal random variable Z"
    )
    default_probabilities: List[PydanticProbabilityFloat] = pydantic.Field(
        description="default probabilities for each asset"
    )

    rhos: List[pydantic.PositiveFloat] = pydantic.Field(
        description="Sensitivities of default probability of assets "
        "with respect to Z (1/sigma(Z))"
    )
    loss: List[int] = pydantic.Field(
        description="List of ints signifying loss per asset"
    )
    min_loss: Optional[int] = pydantic.Field(
        description="Minimum possible loss for the model "
    )

    @property
    def num_model_qubits(self) -> int:
        return len(self.rhos)

    @property
    def distribution_range(self) -> List[int]:
        return [0, sum(self.loss)]

    @property
    def num_output_qubits(self) -> int:
        return int(math.log2(sum(self.loss))) + 1

    @property
    def num_bernoulli_qubits(self) -> int:
        return self.num_qubits + self.num_model_qubits
