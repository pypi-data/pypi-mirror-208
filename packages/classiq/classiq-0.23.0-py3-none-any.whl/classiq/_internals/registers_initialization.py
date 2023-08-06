from enum import Enum
from typing import Collection, Dict, Iterator, List, Optional

from classiq.interface.generator.generated_circuit_data import (
    GeneratedFunction,
    GeneratedRegister,
)

from classiq.exceptions import ClassiqStateInitializationError

RegisterName = str
InitialConditions = Dict[RegisterName, int]


class RegisterCategory(str, Enum):
    DANGLING_INPUTS = "dangling_inputs"
    DANGLING_OUTPUTS = "dangling_outputs"


def get_registers_from_generated_functions(
    generated_functions: List[GeneratedFunction],
    register_category: RegisterCategory,
    register_names: Optional[Collection[RegisterName]] = None,
) -> List[GeneratedRegister]:
    dangling_registers = _get_all_dangling_registers(
        generated_functions=generated_functions, register_category=register_category
    )
    if register_names is None:
        return list(dangling_registers)

    registers: List[GeneratedRegister] = list()
    remain_register = list(register_names)

    for register in _get_participating_dangling_registers(
        dangling_registers=dangling_registers,
        remain_register=remain_register,
    ):
        registers.append(register)
        remain_register.remove(register.name)
        if not remain_register:
            return registers

    raise ClassiqStateInitializationError(
        f"The circuit doesn't contain {register_category} registers that match: {', '.join(remain_register)}."
    )


def _get_participating_dangling_registers(
    dangling_registers: Iterator[GeneratedRegister],
    remain_register: List[RegisterName],
) -> Iterator[GeneratedRegister]:
    return filter(lambda register: register.name in remain_register, dangling_registers)


def _get_all_dangling_registers(
    generated_functions: List[GeneratedFunction],
    register_category: RegisterCategory,
) -> Iterator[GeneratedRegister]:
    return (
        register
        for function in generated_functions
        if getattr(function, register_category)
        for register in function.registers
        if register.name in getattr(function, register_category)
    )
