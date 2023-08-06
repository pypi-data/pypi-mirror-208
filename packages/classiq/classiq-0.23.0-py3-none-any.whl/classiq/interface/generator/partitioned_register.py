import itertools
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence, Tuple, TypeVar

from classiq.interface.generator.slice_parsing_utils import parse_io_slicing

from classiq.exceptions import ClassiqValueError


@dataclass(frozen=True)
class PartitionedRegister:
    name: str

    # There are up to num_qubits qubits within the partitions, with unique values from 0 to num_qubits-1
    num_qubits: int
    partitions: Tuple[Tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if not self.partitions:
            message = f"Error creating {self.name}. Must contain at least one partition"
            raise ClassiqValueError(message)

        if not all(self.partitions):
            message = f"Error creating {self.name}. Each partition must have at least one qubit"
            raise ClassiqValueError(message)

        partition_sets = [frozenset(part) for part in self.partitions]
        intersection = frozenset.intersection(*partition_sets)
        if len(self.partitions) > 1 and intersection:
            message = (
                f"Overlapping partitions in {self.name}. Intersection: {intersection}"
            )
            raise ClassiqValueError(message)

        union = frozenset.union(*partition_sets)
        possible_qubits = frozenset(range(self.num_qubits))
        if not union <= possible_qubits:
            message = f"Extra qubits in {self.name}: {union - possible_qubits}"
            raise ClassiqValueError(message)

    @staticmethod
    def from_partitions_auto_size(
        name: str,
        partitions: Sequence[Sequence[int]],
    ) -> "PartitionedRegister":
        if partitions and all(partitions):
            num_qubits = max(max(qubit_indices) for qubit_indices in partitions) + 1
        else:
            num_qubits = 0
        return PartitionedRegister(
            name=name,
            partitions=tuple(tuple(part) for part in partitions),
            num_qubits=num_qubits,
        )

    def get_partition(self, index: int) -> "RegisterPartition":
        return RegisterPartition(self, index)

    # Special partition containing qubits from [0..num_qubits) not in any other
    # partition. May contain no qubits.
    @property
    def leftover_partition(self):
        return RegisterPartition(self, _index=None)

    @property
    def _leftover_qubits(self) -> Tuple[int, ...]:
        total_qubits = set(itertools.chain.from_iterable(self.partitions))
        return tuple(
            qubit for qubit in range(self.num_qubits) if qubit not in total_qubits
        )

    @property
    def all_qubits_in_partitions(self) -> Iterator[int]:
        return itertools.chain.from_iterable(self.partitions)

    def all_register_partitions(
        self, include_leftover_partition: bool = False
    ) -> List["RegisterPartition"]:
        all_partitions = [self.get_partition(i) for i in range(len(self.partitions))]
        if include_leftover_partition:
            all_partitions.append(self.leftover_partition)
        return all_partitions


@dataclass(frozen=True)
class RegisterPartition:
    partitioned_register: PartitionedRegister

    # index == None means this is the partition containing the leftover qubits.
    _index: Optional[int]

    def __post_init__(self) -> None:
        num_partitions = len(self.partitioned_register.partitions)
        if self._index is not None and (
            self._index >= num_partitions or self._index < 0
        ):
            message = f"Partition does not exist in {self.partitioned_register.name}. Index {self._index} not in range [0, {num_partitions})"
            raise ClassiqValueError(message)

    @property
    def qubits(self) -> Tuple[int, ...]:
        if self._index is None:
            return self.partitioned_register._leftover_qubits
        return self.partitioned_register.partitions[self._index]

    @property
    def _is_single_qubit(self) -> bool:
        return len(self.qubits) == 1

    # io_string is, for example, 'input' or 'foo[3:5]'
    def matches_string(self, io_string: str) -> bool:
        name, slice_ = parse_io_slicing(io_string)
        qubits = tuple(range(self.partitioned_register.num_qubits)[slice_])
        return self.partitioned_register.name == name and self.qubits == qubits


T = TypeVar("T")


# NOTE: Does not preserve order.
def slices_to_partitions_with_payload(
    register_name: str,
    register_domain: Sequence[int],
    slices_with_payloads: Sequence[Tuple[slice, T]],
) -> List[Tuple[RegisterPartition, T]]:
    unsorted_qubits_with_payloads = [
        (tuple(register_domain[slice_]), payload)
        for slice_, payload in slices_with_payloads
    ]
    qubits_with_payloads = sorted(
        unsorted_qubits_with_payloads, key=lambda x: min(x[0])
    )
    partitions, payloads = tuple(zip(*qubits_with_payloads))

    register = PartitionedRegister(
        name=register_name, num_qubits=len(register_domain), partitions=partitions
    )

    return [
        (register.get_partition(index), payload)
        for index, payload in enumerate(payloads)
    ]
