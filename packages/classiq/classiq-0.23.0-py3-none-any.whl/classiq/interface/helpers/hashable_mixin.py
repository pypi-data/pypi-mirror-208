import itertools
from typing import Any, Iterator, Tuple


def _immutable_version(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_immutable_version(elem) for elem in value)
    elif isinstance(value, set):
        return frozenset(_immutable_version(elem) for elem in value)
    elif isinstance(value, dict):
        return tuple(sorted(value.items()))
    return value


class HashableMixin:
    def __hash__(self) -> int:
        return hash(self._value_tuple())

    def _values_to_hash(self) -> Iterator[Any]:
        yield from self.__dict__.values()

    def _immutable_fields(self) -> Iterator[Any]:
        for val in self._values_to_hash():
            yield _immutable_version(val)

    def _value_tuple(self) -> Tuple[Any, ...]:
        return tuple(itertools.chain((str(type(self))), self._immutable_fields()))
