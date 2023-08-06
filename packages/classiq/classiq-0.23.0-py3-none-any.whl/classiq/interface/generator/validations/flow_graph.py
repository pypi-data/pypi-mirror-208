from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import Collection, Iterable, List, Mapping, Optional, Sequence, TypeVar

import networkx as nx

from classiq.interface.generator.quantum_function_call import (
    QuantumFunctionCall,
    WireName,
    WireNameOrPortBinding,
)
from classiq.interface.generator.wiring.sliced_wire import PortBinding
from classiq.interface.helpers.custom_pydantic_types import PydanticNonEmptyString

IO_MULTI_USE_ERROR_MSG = "Input and output names can only be used once"
UNCONNECTED_WIRES_ERROR_MSG = "Wires connected only on one end"
UNCONNECTED_FLOW_IO_ERROR_MSG = "Flow IOs not connected to inner calls"
CYCLE_ERROR_MSG = "Inputs and outputs cannot form a cycle"
UNKNOWN_ERROR_MSG = "Unknown error in the flow graph"
RECURRING_NAMES_ERROR_MSG = "Recurring wire names"


@dataclass
class Wire:
    start: Optional[PydanticNonEmptyString] = None
    end: Optional[PydanticNonEmptyString] = None


def _parse_call_inputs(
    function_call: QuantumFunctionCall,
    wires: Mapping[WireName, Wire],
    flow_input_names: Collection[str],
) -> None:
    if not function_call.non_zero_input_wires:
        return

    for wire_name_or_slice in function_call.non_zero_input_wires:
        wire_name = get_wire_name(wire_name_or_slice)
        if wire_name in flow_input_names:
            continue

        wire = wires[wire_name]

        if wire.end and not isinstance(wire_name_or_slice, PortBinding):
            raise ValueError(
                IO_MULTI_USE_ERROR_MSG
                + f". The name {wire_name} is used multiple times."
            )
        wire.end = function_call.name


def _parse_call_outputs(
    function_call: QuantumFunctionCall,
    wires: Mapping[WireName, Wire],
    flow_output_names: Collection[str],
) -> None:
    if not function_call.non_zero_output_wires:
        return

    for wire_name_or_slice in function_call.non_zero_output_wires:
        wire_name = get_wire_name(wire_name_or_slice)
        if wire_name in flow_output_names:
            continue

        wire = wires[wire_name]

        if wire.start and not isinstance(wire_name_or_slice, PortBinding):
            raise ValueError(
                IO_MULTI_USE_ERROR_MSG
                + f". The name {wire_name} is used multiple times."
            )
        wire.start = function_call.name


def _create_flow_graph(
    logic_flow: Collection[QuantumFunctionCall],
    flow_input_names: Collection[str],
    flow_output_names: Collection[str],
) -> nx.DiGraph:
    wires: Mapping[str, Wire] = defaultdict(Wire)

    for function_call in logic_flow:
        _parse_call_inputs(
            function_call=function_call, wires=wires, flow_input_names=flow_input_names
        )
        _parse_call_outputs(
            function_call=function_call,
            wires=wires,
            flow_output_names=flow_output_names,
        )

    edges = [(wire.start, wire.end) for wire in wires.values()]

    graph = nx.DiGraph()
    graph.add_nodes_from(
        (function_call.name, {"function_call": function_call})
        for function_call in logic_flow
    )
    graph.add_edges_from(edges)
    return graph


def get_wire_name(wire: WireNameOrPortBinding) -> str:
    if isinstance(wire, PortBinding):
        return wire.name
    return wire


def _wire_name_and_unique_slice_names(wires: Sequence[WireNameOrPortBinding]):
    port_binding_names = {wire.name for wire in wires if isinstance(wire, PortBinding)}
    wire_names = [wire for wire in wires if isinstance(wire, str)]
    return [*port_binding_names, *wire_names]


def validate_legal_wiring(
    logic_flow: Collection[QuantumFunctionCall],
    *,
    flow_input_names: Collection[str],
    flow_output_names: Collection[str],
) -> None:
    call_input_names = _wire_name_and_unique_slice_names(
        list(
            chain(*(function_call.non_zero_input_wires for function_call in logic_flow))
        )
    )
    call_output_names = _wire_name_and_unique_slice_names(
        list(
            chain(
                *(function_call.non_zero_output_wires for function_call in logic_flow)
            )
        )
    )

    if (
        len(set(call_input_names)) == len(call_input_names)
        and len(set(call_output_names)) == len(call_output_names)
        and sorted([*call_input_names, *flow_output_names])
        == sorted([*call_output_names, *flow_input_names])
    ):
        return

    error_messages = list()

    recurring_names: Collection[str] = {
        *_recurring_names([*call_input_names, *flow_output_names]),
        *_recurring_names([*call_output_names, *flow_input_names]),
    }

    if recurring_names:
        error_messages.append(f"{RECURRING_NAMES_ERROR_MSG}: {recurring_names}")

    unconnected_flow_ios = [
        name for name in flow_input_names if name not in call_input_names
    ] + [name for name in flow_output_names if name not in call_output_names]
    if unconnected_flow_ios:
        error_messages.append(
            f"{UNCONNECTED_FLOW_IO_ERROR_MSG}: {unconnected_flow_ios}"
        )

    unconnected_wires = [
        name
        for name in call_input_names
        if name not in call_output_names and name not in flow_input_names
    ] + [
        name
        for name in call_output_names
        if name not in call_input_names and name not in flow_output_names
    ]
    if unconnected_wires:
        error_messages.append(f"{UNCONNECTED_WIRES_ERROR_MSG}: {unconnected_wires}")

    raise ValueError(_join_errors(error_messages))


def _join_errors(error_messages: List[str]) -> str:
    if not error_messages:
        error_messages.append(f"{UNKNOWN_ERROR_MSG}")

    return "\n".join(error_messages)


T = TypeVar("T")


def _recurring_names(name_list: List[T]) -> Iterable[T]:
    name_counter = Counter(name_list)
    return (name for name, appearances in name_counter.items() if appearances > 1)


def validate_acyclic_logic_flow(
    logic_flow: Collection[QuantumFunctionCall],
    *,
    flow_input_names: Collection[str],
    flow_output_names: Collection[str],
) -> nx.DiGraph:
    graph = _create_flow_graph(
        logic_flow=logic_flow,
        flow_input_names=flow_input_names,
        flow_output_names=flow_output_names,
    )

    if not nx.algorithms.is_directed_acyclic_graph(graph):
        cycles = list(nx.algorithms.simple_cycles(graph))
        raise ValueError(CYCLE_ERROR_MSG + ". Cycles are: " + str(cycles))

    return graph


def validate_acyclicity_and_topologically_sort_logic_flow(
    logic_flow: List[QuantumFunctionCall],
    *,
    flow_input_names: Collection[str],
    flow_output_names: Collection[str],
) -> List[QuantumFunctionCall]:
    graph = validate_acyclic_logic_flow(
        logic_flow=logic_flow,
        flow_input_names=flow_input_names,
        flow_output_names=flow_output_names,
    )

    return [
        graph.nodes[call_name].get("function_call")
        for call_name in nx.topological_sort(graph)
    ]
