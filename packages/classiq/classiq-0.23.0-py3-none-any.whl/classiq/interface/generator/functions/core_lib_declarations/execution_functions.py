from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalList,
    Integer,
    Real,
    StructInstance,
)
from classiq.interface.generator.functions.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

SAMPLE_OPERATOR = QuantumFunctionDeclaration(
    name="sample",
    param_decls={"num_shots": Integer()},
    operand_declarations={
        "qfunc_call": QuantumFunctionDeclaration(
            name="qfunc_call",
        )
    },
)

ESTIMATE_OPERATOR = QuantumFunctionDeclaration(
    name="estimate",
    param_decls={
        "num_shots": Integer(),
        "hamiltonian": ClassicalList(
            element_type=StructInstance(struct_type="PauliTerm")
        ),
    },
    operand_declarations={
        "qfunc_call": QuantumFunctionDeclaration(
            name="qfunc_call",
        )
    },
)

QAE_WITH_QPE_POST_PROCESS_OPERATOR = QuantumFunctionDeclaration(
    name="qae_with_qpe_result_post_processing",
    param_decls={"estimation_register_size": Integer(), "estimation_method": Integer()},
    operand_declarations={},
)


VQE_OPERATOR = QuantumFunctionDeclaration(
    name="vqe",
    param_decls={
        "hamiltonian": ClassicalList(
            element_type=StructInstance(struct_type="PauliTerm")
        ),
        "num_shots": Integer(),
        "maximize": Bool(),
        "initial_point": ClassicalList(element_type=Integer()),
        "optimizer_name": Integer(),
        "max_iteration": Integer(),
        "tolerance": Real(),
        "step_size": Real(),
        "skip_compute_variance": Bool(),
        "alpha_cvar": Real(),
    },
    operand_declarations={
        "qfunc_call": QuantumFunctionDeclaration(
            name="qfunc_call",
            param_decls={
                "runtime_params": ClassicalList(element_type=Integer()),
            },
        ),
    },
)


QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS.update(
    {
        "sample": SAMPLE_OPERATOR,
        "estimate": ESTIMATE_OPERATOR,
        "qae_with_qpe_result_post_processing": QAE_WITH_QPE_POST_PROCESS_OPERATOR,
        "vqe": VQE_OPERATOR,
    }
)
