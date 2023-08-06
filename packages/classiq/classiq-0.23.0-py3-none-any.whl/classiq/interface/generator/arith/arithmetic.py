from typing import Any, Dict, Optional, Set

import pydantic

from classiq.interface.generator.arith import arithmetic_expression_parser
from classiq.interface.generator.arith.arithmetic_expression_abc import (
    ArithmeticExpressionABC,
    MappingMethods,
)
from classiq.interface.generator.arith.arithmetic_param_getters import (
    id2op,
    operation_allows_target,
)
from classiq.interface.generator.arith.arithmetic_result_builder import (
    ArithmeticResultBuilder,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput

DEFAULT_TARGET_NAME = "arithmetic_target"


class Arithmetic(ArithmeticExpressionABC):
    output_name: str = "expression_result"
    target: Optional[RegisterUserInput] = None
    uncomputation_method: MappingMethods = MappingMethods.optimized
    inputs_to_save: Set[str] = pydantic.Field(default_factory=set)

    @pydantic.validator("target", always=True)
    def _validate_target_name(
        cls, target: Optional[RegisterUserInput], values: Dict[str, Any]
    ) -> Optional[RegisterUserInput]:
        if target is None:
            return None
        if not cls._expression_allows_target(expression=values.get("expression", "")):
            raise ValueError("Expression does not support target assignment")
        return target if target.name else target.revalued(name=DEFAULT_TARGET_NAME)

    @staticmethod
    def _expression_allows_target(expression: str) -> bool:
        graph = arithmetic_expression_parser.parse_expression(
            expression, validate_degrees=True
        )
        return all(
            degree or operation_allows_target(id2op(node))
            for node, degree in graph.out_degree
        )

    @pydantic.validator("inputs_to_save", always=True)
    def _validate_inputs_to_save(
        cls, inputs_to_save: Set[str], values: Dict[str, Any]
    ) -> Set[str]:
        assert all(reg in values.get("definitions", {}) for reg in inputs_to_save)
        return inputs_to_save

    def _create_ios(self) -> None:
        self._inputs = {
            name: register
            for name, register in self.definitions.items()
            if name in self._get_literal_set()
            and isinstance(register, RegisterUserInput)
        }
        self._outputs = {
            name: self._inputs[name]
            for name in self.inputs_to_save
            if name in self._inputs
        }
        self._outputs[self.output_name] = ArithmeticResultBuilder(
            graph=arithmetic_expression_parser.parse_expression(
                self.expression, validate_degrees=True
            ),
            definitions=self.definitions,
            max_fraction_places=self.max_fraction_places,
            output_name=self.output_name,
        ).result
        if self.target:
            self._inputs[self.target.name] = self.target
