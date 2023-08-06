from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import (
    ClassicalList,
    Integer,
    Pauli,
    Real,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclaration,
    PortDeclarationDirection,
)
from classiq.interface.generator.functions.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

H_FUNCTION = QuantumFunctionDeclaration(
    name="H",
    port_declarations={
        "target": PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    },
)

PHASE_FUNCTION = QuantumFunctionDeclaration(
    name="PHASE",
    param_decls={"theta": Real()},
    port_declarations={
        "target": PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    },
)

SWAP_FUNCTION = QuantumFunctionDeclaration(
    name="SWAP",
    port_declarations={
        "qbit0": PortDeclaration(
            name="qbit0",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        "qbit1": PortDeclaration(
            name="qbit1",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    },
)


IDENTITY_FUNCTION = QuantumFunctionDeclaration(
    name="IDENTITY",
    param_decls={"port_size": Integer()},
    port_declarations={
        "p": PortDeclaration(
            name="p",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
)


SINGLE_PAULI_EXPONENT_FUNCTION = QuantumFunctionDeclaration(
    name="single_pauli_exponent",
    param_decls={
        "port_size": Integer(),
        "pauli_string": ClassicalList(element_type=Pauli()),
        "coefficient": Real(),
    },
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
)


RX_FUNCTION = QuantumFunctionDeclaration(
    name="RX",
    param_decls={
        "theta": Real(),
    },
    port_declarations={
        "target": PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        )
    },
)


_BUILTIN_QUANTUM_FUNCTION_LIST = [
    func.resolve_expressions()
    for func in [
        H_FUNCTION,
        PHASE_FUNCTION,
        SWAP_FUNCTION,
        IDENTITY_FUNCTION,
        SINGLE_PAULI_EXPONENT_FUNCTION,
        RX_FUNCTION,
    ]
]

QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS.update(
    {func.name: func for func in _BUILTIN_QUANTUM_FUNCTION_LIST}
)
