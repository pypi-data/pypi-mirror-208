from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class PortBinding(HashablePydanticBaseModel):
    name: str
    start: Expression
    end: Expression

    def add_prefix(self, prefix: str) -> "PortBinding":
        return self.copy(update={"name": prefix + self.name})

    class Config:
        frozen = True


class InoutPortBinding(HashablePydanticBaseModel):
    input_name: str
    output_name: str
    start: Expression
    end: Expression

    @property
    def source_binding(self) -> PortBinding:
        return PortBinding(
            name=self.input_name,
            start=self.start,
            end=self.end,
        )

    @property
    def destination_binding(self) -> PortBinding:
        return PortBinding(
            name=self.output_name,
            start=self.start,
            end=self.end,
        )

    class Config:
        frozen = True
