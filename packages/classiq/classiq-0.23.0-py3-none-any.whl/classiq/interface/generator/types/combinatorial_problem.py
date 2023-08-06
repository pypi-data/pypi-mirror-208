from enum import Enum
from typing import List

import pydantic

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.types.struct_declaration import StructDeclaration


class ObjectiveType(Enum):
    Min = 0
    Max = 1


class CombinatorialOptimizationStructDeclaration(StructDeclaration):
    variable_lower_bound: int = pydantic.Field(default=0)
    variable_upper_bound: int = pydantic.Field(default=1)
    constraints: List[Expression] = pydantic.Field(
        default_factory=list, description="List of constraint expressions"
    )
    objective_type: ObjectiveType = pydantic.Field(
        description="Specify whether the optimization problem is Min or Max"
    )
    objective_function: Expression = pydantic.Field(
        description="The expression to optimize, according to the objective type"
    )
