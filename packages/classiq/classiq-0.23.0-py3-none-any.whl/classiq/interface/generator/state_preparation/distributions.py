from typing import Collection, Tuple, Union

import pydantic
from numpy.typing import ArrayLike

from classiq.interface.generator.validations.validator_functions import (
    validate_probabilities,
)
from classiq.interface.helpers.custom_pydantic_types import PydanticProbabilityFloat


class PMF(pydantic.BaseModel):
    pmf: Tuple[PydanticProbabilityFloat, ...]
    _validate_amplitudes = pydantic.validator("pmf", allow_reuse=True)(
        validate_probabilities
    )

    class Config:
        frozen = True


class GaussianMoments(pydantic.BaseModel):
    mu: float
    sigma: pydantic.PositiveFloat

    class Config:
        frozen = True


class GaussianMixture(pydantic.BaseModel):
    gaussian_moment_list: Tuple[GaussianMoments, ...]
    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="Number of qubits for the provided state."
    )

    class Config:
        frozen = True


Probabilities = Union[PMF, GaussianMixture]
FlexibleProbabilities = Union[Probabilities, ArrayLike, dict, Collection[float]]
Amplitudes = Tuple[float, ...]
FlexibleAmplitudes = Union[ArrayLike, Collection[float]]
Distribution = Union[Amplitudes, Probabilities]


def num_of_qubits(distribution: Distribution) -> int:
    if isinstance(distribution, GaussianMixture):
        return distribution.num_qubits
    if isinstance(distribution, PMF):
        return len(distribution.pmf).bit_length() - 1
    return len(distribution).bit_length() - 1
