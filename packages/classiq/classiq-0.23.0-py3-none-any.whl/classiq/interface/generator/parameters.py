from typing import TYPE_CHECKING, Any, Union

import pydantic

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = Any

ParameterType: TypeAlias = str
ParameterFloatType: TypeAlias = Union[float, ParameterType]


class ParameterMap(pydantic.BaseModel):
    original: str = pydantic.Field(description="the name of the parameter")
    new_parameter: ParameterFloatType = pydantic.Field(
        description="the new parameter or value the original parameter is mapped to"
    )

    class Config:
        frozen = True
