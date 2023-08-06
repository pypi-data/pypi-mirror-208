import enum
from typing import Any, Dict, Optional, Union

import pydantic

from classiq.interface.helpers.custom_pydantic_types import (
    PydanticNonZeroProbabilityFloat,
)


class KnownFunctions(str, enum.Enum):
    VAR = "var"
    SHORTFALL = "expected short fall"
    X_SQUARE = "x**2"
    EUROPEAN_CALL_OPTION = "european call option"


class FunctionCondition(pydantic.BaseModel):
    threshold: float
    larger: bool = pydantic.Field(
        default=False,
        description="When true, function is set when input is larger to threshold and otherwise 0. Default is False.",
    )

    class Config:
        frozen = True


class FinanceFunctionInput(pydantic.BaseModel):
    f: Union[str, KnownFunctions] = pydantic.Field(
        description="A callable function to solve the model"
    )
    variable: str = pydantic.Field(
        default="x", description="Variable/s of the function"
    )
    condition: FunctionCondition = pydantic.Field(
        description="The condition for the function"
    )
    polynomial_degree: Optional[int] = pydantic.Field(
        default=None,
        description="The polynomial degree of approximation, uses linear approximation by default",
    )
    use_chebyshev_polynomial_approximation: bool = pydantic.Field(
        default=False,
        description="Flag if to use chebyshev polynomial approximation for target function",
    )

    tail_probability: Optional[PydanticNonZeroProbabilityFloat] = pydantic.Field(
        default=None,
        description="The required probability on the tail of the distribution (1 - percentile)",
    )

    @pydantic.validator("use_chebyshev_polynomial_approximation")
    def _validate_polynomial_flag(
        cls, use_chebyshev_flag: bool, values: Dict[str, Any]
    ) -> bool:
        if use_chebyshev_flag ^ (values.get("polynomial_degree") is None):
            return use_chebyshev_flag
        raise ValueError(
            "Degree must be positive and use_chebyshev_polynomial_approximation set to True"
        )

    @pydantic.validator("tail_probability", always=True)
    def _validate_tail_probability_assignment_for_shortfall(
        cls,
        tail_probability: Optional[PydanticNonZeroProbabilityFloat],
        values: Dict[str, Any],
    ) -> Optional[PydanticNonZeroProbabilityFloat]:
        if values.get("f") == KnownFunctions.SHORTFALL and not tail_probability:
            raise ValueError("Tail probability must be set for expected short fall")
        return tail_probability

    class Config:
        frozen = True
