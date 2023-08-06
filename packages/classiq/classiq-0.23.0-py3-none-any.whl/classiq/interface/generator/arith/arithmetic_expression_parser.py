import ast
from typing import Collection, List, Optional, cast

import networkx as nx

from classiq.interface.generator.arith.arithmetic_expression_validator import (
    DEFAULT_EXPRESSION_TYPE,
    DEFAULT_SUPPORTED_FUNC_NAMES,
    ExpressionValidator,
    SupportedNodesTypes,
)
from classiq.interface.generator.arith.ast_node_rewrite import (
    OUTPUT_SIZE,
    AstNodeRewrite,
)

from classiq.exceptions import ClassiqArithmeticError

_ILLEGAL_PARSED_GRAPH_ERROR_MESSAGE: str = "parsed graph contains multiple result nodes"
_ALLOWED_MULTI_ARGUMENT_FUNCTIONS = ("min", "max")


class ExpressionVisitor(ExpressionValidator):
    def __init__(
        self,
        supported_nodes,
        expression_type: str = DEFAULT_EXPRESSION_TYPE,
        supported_functions: Optional[Collection[str]] = None,
    ) -> None:
        super().__init__(supported_nodes, expression_type, supported_functions)
        self.graph = nx.DiGraph()

    def visit_Compare(self, node: ast.Compare) -> None:
        self.validate_Compare(node)
        self.update_graph(
            node,
            cast(SupportedNodesTypes, node.left),
            cast(SupportedNodesTypes, node.comparators[0]),
        )
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.validate_BinOp(node)
        self.update_graph(
            node,
            cast(SupportedNodesTypes, node.left),
            cast(SupportedNodesTypes, node.right),
        )
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        self.update_graph(node, cast(SupportedNodesTypes, node.operand))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self.validate_Call(node)
        self.update_graph(node, *cast(List[SupportedNodesTypes], node.args))
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.update_graph(node, *cast(List[SupportedNodesTypes], node.values))
        self.generic_visit(node)

    def update_graph(
        self, child_node: SupportedNodesTypes, *parent_nodes: SupportedNodesTypes
    ) -> None:
        child_node_id = AstNodeRewrite().extract_node_id(child_node)

        for parent_node in parent_nodes:
            parent_node_id = AstNodeRewrite().extract_node_id(parent_node)
            self.graph.add_edge(parent_node_id, child_node_id)

        mod_output_size = getattr(child_node, OUTPUT_SIZE, None)
        if mod_output_size:
            self.graph.nodes[child_node_id][OUTPUT_SIZE] = mod_output_size

            for node in parent_nodes:
                node_output_size = getattr(node, OUTPUT_SIZE, mod_output_size)

                new_output_size = min(mod_output_size, node_output_size)
                node.output_size = new_output_size  # type: ignore[union-attr]

                node_id = AstNodeRewrite().extract_node_id(node)
                self.graph.nodes[node_id][OUTPUT_SIZE] = new_output_size


class InDegreeLimiter:
    @staticmethod
    def _condition(graph: nx.DiGraph, node: str) -> bool:
        return graph.in_degree[node] > 2 and node in _ALLOWED_MULTI_ARGUMENT_FUNCTIONS

    @staticmethod
    def _node_conversion(graph: nx.DiGraph, node: str) -> nx.DiGraph:
        relevant_in_edges = graph.in_edges(node)
        last_node_added = node
        for idx, in_edge in enumerate(list(relevant_in_edges)[2:]):
            graph.remove_edge(*in_edge)
            new_node = node + f"_copy_{idx}"
            graph.add_node(new_node)
            for out_edge in list(graph.out_edges(last_node_added)):
                graph.add_edge(new_node, out_edge[1])
                graph.remove_edge(*out_edge)
            graph.add_edge(last_node_added, new_node)
            graph.add_edge(in_edge[0], new_node)
            last_node_added = new_node
        return graph

    @classmethod
    def graph_conversion(cls, graph: nx.DiGraph) -> nx.DiGraph:
        for node in list(graph.nodes):
            if cls._condition(graph, node):
                graph = cls._node_conversion(graph, node)
        if num_of_result_nodes(graph) != 1:
            raise ClassiqArithmeticError(_ILLEGAL_PARSED_GRAPH_ERROR_MESSAGE)
        return graph


def parse_expression(
    expression: str,
    *,
    validate_degrees: bool,
    supported_nodes=SupportedNodesTypes,
    expression_type: str = DEFAULT_EXPRESSION_TYPE,
    supported_functions: Optional[Collection[str]] = None,
) -> nx.DiGraph:
    supported_functions = supported_functions or DEFAULT_SUPPORTED_FUNC_NAMES

    visitor = ExpressionVisitor(supported_nodes, expression_type, supported_functions)
    visitor.visit_str(expression)
    if validate_degrees:
        return InDegreeLimiter.graph_conversion(graph=visitor.graph)
    return visitor.graph


def num_of_result_nodes(graph: nx.DiGraph) -> int:
    return sum(int(graph.out_degree(node) == 0) for node in graph.nodes)


def validate_expression_graph(
    expression: str,
    *,
    supported_nodes=SupportedNodesTypes,
    expression_type: str = DEFAULT_EXPRESSION_TYPE,
    supported_functions: Optional[Collection[str]] = None,
):
    parse_expression(
        expression,
        validate_degrees=True,
        supported_nodes=supported_nodes,
        expression_type=expression_type,
        supported_functions=supported_functions,
    )
