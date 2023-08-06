from abc import abstractmethod
from typing import Any, Dict, List, Union

import pydantic
from pydantic import Field
from sympy import Array, Basic, IndexedBase, Symbol, symbols
from typing_extensions import Annotated, Literal

from classiq.interface.generator.expressions.pauli import Pauli as PauliEnum
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class ClassicalTypeBase(HashablePydanticBaseModel):
    def sympy_symbol(self, name: str) -> Basic:
        return Symbol(name)

    @property
    @abstractmethod
    def default_value(self) -> Any:
        raise NotImplementedError(
            f"{self.__class__.__name__} type has no default value"
        )


class Integer(ClassicalTypeBase):
    kind: Literal["int"] = pydantic.Field(default="int")

    @property
    def default_value(self) -> int:
        return 0


class Real(ClassicalTypeBase):
    kind: Literal["real"] = pydantic.Field(default="real")

    @property
    def default_value(self) -> float:
        return 0


class Bool(ClassicalTypeBase):
    kind: Literal["bool"] = pydantic.Field(default="bool")

    @property
    def default_value(self) -> bool:
        return False


class ClassicalList(ClassicalTypeBase):
    kind: Literal["list"] = pydantic.Field(default="list")
    element_type: "ClassicalType"

    def sympy_symbol(self, name: str) -> Basic:
        return IndexedBase(name)

    @property
    def default_value(self) -> Any:
        return super().default_value


class Pauli(ClassicalTypeBase):
    kind: Literal["pauli"] = pydantic.Field(default="pauli")

    @property
    def default_value(self) -> PauliEnum:
        return PauliEnum.I


class TypeHandle(ClassicalTypeBase):
    kind: Literal["type_handle"] = pydantic.Field(default="type_handle")

    @property
    def default_value(self) -> Any:
        return super().default_value


class StructInstance(ClassicalTypeBase):
    kind: Literal["struct_instance"] = pydantic.Field(default="struct_instance")
    struct_type: str = pydantic.Field(description="The struct type of the instance")

    @property
    def default_value(self) -> str:
        return f"get_default(get_type({self.struct_type}))"


class ClassicalArray(ClassicalTypeBase):
    kind: Literal["array"] = pydantic.Field(default="array")
    element_type: "ClassicalType"
    size: pydantic.PositiveInt

    def sympy_symbol(self, name: str) -> Basic:
        symbol_string = "".join(f":{shape}" for shape in self._shape())
        return Array(symbols(f"{name}{symbol_string}"), shape=self._shape())

    def _shape(self) -> List[pydantic.PositiveInt]:
        ret = [self.size]
        if isinstance(self.element_type, ClassicalArray):
            ret += self.element_type._shape()

        return ret

    @property
    def default_value(self) -> Any:
        return super().default_value


ClassicalType = Annotated[
    Union[
        Integer,
        Real,
        Bool,
        ClassicalList,
        Pauli,
        TypeHandle,
        StructInstance,
        ClassicalArray,
    ],
    Field(discriminator="kind"),
]
ClassicalList.update_forward_refs()
ClassicalArray.update_forward_refs()


def sympy_symbols(symbols: Dict[str, ClassicalType]) -> Dict[str, Basic]:
    return {
        param_name: param_type.sympy_symbol(param_name)
        for param_name, param_type in symbols.items()
    }
