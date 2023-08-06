from typing import Any, Dict, Iterable, Optional, Set, Union

import networkx as nx
import pydantic

from classiq.interface.generator.arith import arithmetic_param_getters, number_utils
from classiq.interface.generator.arith.argument_utils import RegisterOrConst
from classiq.interface.generator.arith.ast_node_rewrite import OUTPUT_SIZE
from classiq.interface.generator.arith.register_user_input import RegisterUserInput

from classiq.exceptions import ClassiqArithmeticError

SingleArithmeticDefinition = Union[
    pydantic.StrictInt, pydantic.StrictFloat, RegisterUserInput
]
ArithmeticDefinitions = Dict[str, SingleArithmeticDefinition]


class ArithmeticResultBuilder:
    def __init__(
        self,
        *,
        graph: nx.DiGraph,
        definitions: ArithmeticDefinitions,
        output_name: str,
        max_fraction_places: int,
    ) -> None:
        self.result = self._fill_operation_results(
            output_name=output_name,
            graph=graph,
            result_definitions=definitions,
            max_fraction_places=max_fraction_places,
        )

    @staticmethod
    def convert_result_definition(
        node: Any,
        definition: Optional[SingleArithmeticDefinition],
        max_fraction_places: int,
    ) -> RegisterOrConst:
        if definition:
            return definition
        elif isinstance(node, int):
            return node
        elif isinstance(node, float):
            return number_utils.limit_fraction_places(
                node, max_fraction_places=max_fraction_places
            )
        raise ClassiqArithmeticError("Incompatible argument definition type")

    @classmethod
    def _compute_inputs_data(
        cls,
        *,
        inputs_node_set: Set[str],
        result_definitions: ArithmeticDefinitions,
        max_fraction_places: int,
    ) -> Dict[str, RegisterOrConst]:
        return {
            str(node): cls.convert_result_definition(
                node, result_definitions.get(node), max_fraction_places
            )
            for node in inputs_node_set
        }

    @classmethod
    def _fill_operation_results(
        cls,
        *,
        output_name: str,
        graph: nx.DiGraph,
        result_definitions: ArithmeticDefinitions,
        max_fraction_places: int,
    ) -> RegisterUserInput:
        inputs_node_set: Set[str] = {
            vertex for vertex, deg in graph.in_degree if deg == 0
        }
        node_results: Dict[str, RegisterOrConst] = cls._compute_inputs_data(
            inputs_node_set=inputs_node_set,
            result_definitions=result_definitions,
            max_fraction_places=max_fraction_places,
        )
        for node in nx.topological_sort(graph):
            if node in inputs_node_set:
                continue

            args = (
                node_results[str(predecessor_node)]
                for predecessor_node in graph.predecessors(node)
            )
            if graph.out_degree(node) == 0:
                return cls._get_node_result(graph, args, node, output_name=output_name)
            node_results[node] = cls._get_node_result(graph, args, node)
        raise ClassiqArithmeticError("Expression has no result")

    @classmethod
    def _get_node_result(
        cls,
        graph: nx.DiGraph,
        args: Iterable[RegisterOrConst],
        node: str,
        *,
        output_name: Optional[str] = None,
    ) -> RegisterUserInput:
        return arithmetic_param_getters.get_params(
            node_id=node,
            args=args,
            output_name=output_name or cls.generate_output_name(node),
            output_size=graph.nodes[node].get(OUTPUT_SIZE, None),
        ).result_register

    @staticmethod
    def generate_output_name(name: str) -> str:
        return f"out_{name}"
