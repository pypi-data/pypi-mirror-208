import enum


class QuantumInstructionSet(str, enum.Enum):
    QASM = "qasm"
    QSHARP = "qsharp"
    IONQ = "ionq"

    @classmethod
    def from_suffix(cls, suffix) -> "QuantumInstructionSet":
        if suffix == "qasm":
            return QuantumInstructionSet.QASM
        if suffix == "qs":
            return QuantumInstructionSet.QSHARP
        if suffix == "ionq":
            return QuantumInstructionSet.IONQ
        raise ValueError("Illegal suffix")
