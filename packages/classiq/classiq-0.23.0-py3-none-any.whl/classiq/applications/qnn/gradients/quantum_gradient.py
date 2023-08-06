import abc
import functools

from torch import Tensor

from classiq.interface.generator.result import GeneratedCircuit

from classiq.applications.qnn.circuit_utils import extract_parameters, validate_circuit
from classiq.applications.qnn.types import ExecuteFunciton, PostProcessFunction


class QuantumGradient(abc.ABC):
    def __init__(
        self,
        circuit: GeneratedCircuit,
        execute: ExecuteFunciton,
        post_process: PostProcessFunction,
        *args,
        **kwargs
    ):
        self._execute = execute
        self._post_process = post_process

        validate_circuit(circuit)
        self._circuit = circuit
        self._parameters_names = extract_parameters(circuit)

        self.execute = functools.partial(execute, circuit)

    @abc.abstractmethod
    def gradient_weights(
        self, inputs: Tensor, weights: Tensor, *args, **kwargs
    ) -> Tensor:
        pass

    @abc.abstractmethod
    def gradient_inputs(
        self, inputs: Tensor, weights: Tensor, *args, **kwargs
    ) -> Tensor:
        pass
