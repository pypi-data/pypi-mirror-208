from typing import Any, Dict, Optional, Union

import numpy as np
import pydantic

from classiq.interface.generator.range_types import NonNegativeFloatRange
from classiq.interface.generator.state_preparation.distributions import (
    PMF,
    Amplitudes,
    FlexibleAmplitudes,
    FlexibleProbabilities,
    GaussianMixture,
    Probabilities,
    num_of_qubits,
)
from classiq.interface.generator.state_preparation.metrics import Metrics
from classiq.interface.generator.state_preparation.state_preparation_abc import (
    StatePreparationABC,
)
from classiq.interface.generator.validations.validator_functions import (
    validate_amplitudes,
)


class StatePreparation(StatePreparationABC):
    amplitudes: Optional[Amplitudes] = pydantic.Field(
        description="vector of probabilities", default=None
    )
    probabilities: Optional[Probabilities] = pydantic.Field(
        description="vector of amplitudes", default=None
    )
    error_metric: Dict[Metrics, NonNegativeFloatRange] = pydantic.Field(
        default_factory=lambda: {
            Metrics.L2: NonNegativeFloatRange(lower_bound=0, upper_bound=1e-4)
        }
    )
    is_uniform_start: bool = True

    # The order of validations is important: amplitudes, probabilities, error_metric

    @pydantic.validator("amplitudes", always=True, pre=True)
    def _initialize_amplitudes(
        cls, amplitudes: Optional[FlexibleAmplitudes]
    ) -> Optional[Amplitudes]:
        if amplitudes is None:
            return None
        amplitudes = np.array(amplitudes).squeeze()
        if amplitudes.ndim == 1:
            return validate_amplitudes(tuple(amplitudes))

        raise ValueError(
            "Invalid amplitudes were given, please ensure the amplitude is a vector of float in the form of either tuple or list or numpy array"
        )

    @pydantic.validator("probabilities", always=True, pre=True)
    def _initialize_probabilities(
        cls, probabilities: Optional[FlexibleProbabilities]
    ) -> Optional[Union[PMF, GaussianMixture, dict]]:
        if probabilities is None:
            return None
        if isinstance(probabilities, Probabilities.__args__):  # type: ignore[attr-defined]
            return probabilities
        if isinstance(probabilities, dict):  # a pydantic object
            return probabilities
        probabilities = np.array(probabilities).squeeze()
        if probabilities.ndim == 1:
            return PMF(pmf=probabilities.tolist())

        raise ValueError(
            "Invalid probabilities were given, please ensure the probabilities is a vector of float in the form of either tuple or list or numpy array"
        )

    @pydantic.validator("error_metric", always=True, pre=True)
    def _validate_error_metric(
        cls, error_metric: Dict[Metrics, NonNegativeFloatRange], values: Dict[str, Any]
    ) -> Dict[Metrics, NonNegativeFloatRange]:
        if not values.get("amplitudes"):
            return error_metric
        unsupported_metrics = {
            Metrics(metric).value
            for metric in error_metric
            if not Metrics(metric).supports_amplitudes
        }
        if unsupported_metrics:
            raise ValueError(
                f"{unsupported_metrics} are not supported for amplitude preparation"
            )
        return error_metric

    @pydantic.root_validator
    def _validate_either_probabilities_or_amplitudes(
        cls,
        values: Dict[str, Any],
    ) -> Optional[Union[PMF, GaussianMixture, dict]]:
        amplitudes = values.get("amplitudes")
        probabilities = values.get("probabilities")
        if amplitudes is not None and probabilities is not None:
            raise ValueError(
                "StatePreparation can't get both probabilities and amplitudes"
            )
        return values

    @property
    def num_state_qubits(self) -> int:
        distribution = self.probabilities or self.amplitudes
        if distribution is None:
            raise ValueError("Must have either probabilities or amplitudes")
        return num_of_qubits(distribution)
