from sympy import AtomicExpr

from classiq.interface.generator.types.struct_declaration import StructDeclaration


class SympyTypeHandle(AtomicExpr):
    def __init__(self, struct_declaration: StructDeclaration):
        super().__init__()
        self._struct_declaration = struct_declaration

    def __str__(self):
        return f"get_type({self.args[0].name})"

    @property
    def struct_declaration(self) -> StructDeclaration:
        return self.args[0]
