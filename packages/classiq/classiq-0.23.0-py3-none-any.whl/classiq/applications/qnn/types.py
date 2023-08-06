from typing import Callable, Dict, List, Tuple, Union

import torch
from torch import Tensor

from classiq.interface.executor.result import ExecutionDetails, MultipleExecutionDetails
from classiq.interface.generator.result import GeneratedCircuit

Arguments = Dict[str, float]
MultipleArguments = Tuple[Arguments, ...]

Circuit = GeneratedCircuit
ExecuteFunciton = Callable[
    [GeneratedCircuit, MultipleArguments], MultipleExecutionDetails
]
ExecuteFuncitonOnlyArguments = Callable[[MultipleArguments], MultipleExecutionDetails]
PostProcessFunction = Callable[[ExecutionDetails], Tensor]
TensorToArgumentsCallable = Callable[[Tensor, Tensor], MultipleArguments]

Shape = Union[torch.Size, Tuple[int, ...]]

GradientFunction = Callable[[Tensor, Tensor], Tensor]
SimulateFunction = Callable[[Tensor, Tensor], Tensor]

DataAndLabel = Tuple[List[int], List[int]]
Transform = Callable[[Tensor], Tensor]
