from typing import Tuple, Union

from classiq.interface.generator.arith import number_utils
from classiq.interface.generator.arith.register_user_input import RegisterUserInput

RegisterOrConst = Union[RegisterUserInput, float]


def fraction_places(argument: RegisterOrConst) -> int:
    if isinstance(argument, RegisterUserInput):
        return argument.fraction_places
    return number_utils.fraction_places(argument)


def integer_part_size(argument: RegisterOrConst) -> int:
    if isinstance(argument, RegisterUserInput):
        return argument.integer_part_size
    return number_utils.integer_part_size(argument)


def size(argument: RegisterOrConst) -> int:
    if isinstance(argument, RegisterUserInput):
        return argument.size
    return number_utils.size(argument)


def is_signed(argument: RegisterOrConst) -> bool:
    if isinstance(argument, RegisterUserInput):
        return argument.is_signed
    return argument < 0


def upper_bound(argument: RegisterOrConst) -> float:
    if isinstance(argument, RegisterUserInput):
        return max(argument.bounds)
    return argument


def lower_bound(argument: RegisterOrConst) -> float:
    if isinstance(argument, RegisterUserInput):
        return min(argument.bounds)
    return argument


def bounds(argument: RegisterOrConst) -> Tuple[float, float]:
    if isinstance(argument, RegisterUserInput):
        return argument.bounds
    return argument, argument
