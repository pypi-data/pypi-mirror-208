from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class FinanceModelInput(HashablePydanticBaseModel):
    @property
    def num_output_qubits(self) -> int:
        return 0

    class Config:
        frozen = True
