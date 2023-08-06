from sympy import AtomicExpr, Dict as SympyDict

from classiq.interface.generator.expressions.sympy_str import SympyStr
from classiq.interface.generator.types.struct_declaration import StructDeclaration

from classiq.exceptions import ClassiqValueError


class SympyStructInstance(SympyStr, AtomicExpr):
    def __init__(self, struct_declaration: StructDeclaration, fields: SympyDict):
        if set(struct_declaration.variables.keys()) != {
            field.name for field in fields.keys()
        }:
            raise ClassiqValueError(
                f"Invalid fields for {struct_declaration.name} instance"
            )
        self._fields = fields

    @property
    def fields(self) -> SympyDict:
        return self.args[1]

    def __str__(self) -> str:
        return f"struct_literal({self.fields})"
