from typing import Any, Callable, Dict, List, TypeVar

from pydantic import BaseModel

ModelNode = TypeVar("ModelNode", bound=BaseModel)
ReductionType = Callable[[ModelNode], ModelNode]


def reduce_node(node: ModelNode, reductions: List[ReductionType]) -> ModelNode:
    new_node = _reduce_subtree(node, reductions)
    for reduction_function in reductions:
        new_node = reduction_function(new_node)
    return new_node


def _reduce_elem(elem: Any, reduce_functions: List[ReductionType]) -> Any:
    if isinstance(elem, BaseModel):
        return reduce_node(elem, reduce_functions)
    elif isinstance(elem, list):
        return [_reduce_elem(sub_elem, reduce_functions) for sub_elem in elem]
    elif isinstance(elem, dict):
        return {
            key: _reduce_elem(sub_elem, reduce_functions)
            for key, sub_elem in elem.items()
        }
    return elem


def _reduce_subtree(
    node: ModelNode, reduce_functions: List[ReductionType]
) -> ModelNode:
    result: Dict[str, Any] = dict()
    for name, value in node:
        result[name] = _reduce_elem(value, reduce_functions)
    return node.copy(update=result)
