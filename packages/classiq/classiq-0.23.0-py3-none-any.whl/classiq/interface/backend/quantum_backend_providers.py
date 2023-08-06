from enum import Enum

from typing_extensions import Literal


class AnalyzerProviderVendor(str, Enum):
    IBM_QUANTUM = "IBM Quantum"
    AZURE_QUANTUM = "Azure Quantum"
    AMAZON_BRAKET = "Amazon Braket"


class ProviderVendor(str, Enum):
    IBM_QUANTUM = "IBM Quantum"
    AZURE_QUANTUM = "Azure Quantum"
    AMAZON_BRAKET = "Amazon Braket"
    IONQ = "IonQ"
    NVIDIA = "Nvidia"


class ProviderTypeVendor:
    IBM_QUANTUM = Literal[ProviderVendor.IBM_QUANTUM]
    AZURE_QUANTUM = Literal[ProviderVendor.AZURE_QUANTUM]
    AWS_BRAKET = Literal[ProviderVendor.AMAZON_BRAKET]
    IONQ = Literal[ProviderVendor.IONQ]
    NVIDIA = Literal[ProviderVendor.NVIDIA]


class IonqBackendNames(str, Enum):
    SIMULATOR = "simulator"
    HARMONY = "qpu.harmony"
    ARIA = "qpu.aria-1"
    S11 = "qpu.s11"


class AzureQuantumBackendNames(str, Enum):
    IONQ_ARIA = "ionq.qpu.aria-1"
    IONQ_QPU = "ionq.qpu"
    IONQ_SIMULATOR = "ionq.simulator"
    MICROSOFT_ESTIMATOR = "microsoft.estimator"
    MICROSOFT_FULLSTATE_SIMULATOR = "microsoft.simulator.fullstate"
    RIGETTI_ASPEN2 = "rigetti.qpu.aspen-m-2"
    RIGETTI_ASPEN3 = "rigetti.qpu.aspen-m-3"
    RIGETTI_SIMULATOR = "rigetti.sim.qvm"
    QCI_MACHINE1 = "qci.machine1"
    QCI_NOISY_SIMULATOR = "qci.simulator.noisy"
    QCI_SIMULATOR = "qci.simulator"
    QUANTINUUM_API_VALIDATOR1 = "quantinuum.sim.h1-1sc"
    QUANTINUUM_API_VALIDATOR1_OLD = "quantinuum.hqs-lt-s1-apival"
    QUANTINUUM_API_VALIDATOR2 = "quantinuum.sim.h1-2sc"
    QUANTINUUM_API_VALIDATOR2_OLD = "quantinuum.hqs-lt-s2-apival"
    QUANTINUUM_QPU1 = "quantinuum.qpu.h1-1"
    QUANTINUUM_QPU1_OLD = "quantinuum.hqs-lt-s1"
    QUANTINUUM_QPU2 = "quantinuum.qpu.h1-2"
    QUANTINUUM_QPU2_OLD = "quantinuum.hqs-lt-s2"
    QUANTINUUM_SIMULATOR1 = "quantinuum.sim.h1-1e"
    QUANTINUUM_SIMULATOR1_OLD = "quantinuum.hqs-lt-s1-sim"
    QUANTINUUM_SIMULATOR2 = "quantinuum.sim.h1-2e"
    QUANTINUUM_SIMULATOR2_OLD = "quantinuum.hqs-lt-s2-sim"


class AWSBackendNames(str, Enum):
    AMAZON_BRAKET_SV1 = "SV1"
    AMAZON_BRAKET_TN1 = "TN1"
    AMAZON_BRAKET_DM1 = "dm1"
    AMAZON_BRAKET_ASPEN_11 = "Aspen-11"
    AMAZON_BRAKET_M_1 = "Aspen-M-1"
    AMAZON_BRAKET_IONQ = "IonQ Device"
    AMAZON_BRAKET_LUCY = "Lucy"


class IBMQBackendNames(str, Enum):
    IBMQ_AER_SIMULATOR = "aer_simulator"
    IBMQ_AER_SIMULATOR_STATEVECTOR = "aer_simulator_statevector"
    IBMQ_AER_SIMULATOR_DENSITY_MATRIX = "aer_simulator_density_matrix"
    IBMQ_AER_SIMULATOR_MATRIX_PRODUCT_STATE = "aer_simulator_matrix_product_state"


class NvidiaBackendNames(str, Enum):
    STATEVECTOR = "statevector"


EXACT_SIMULATORS = {
    IonqBackendNames.SIMULATOR,
    AzureQuantumBackendNames.IONQ_SIMULATOR,
    AzureQuantumBackendNames.MICROSOFT_FULLSTATE_SIMULATOR,
    AWSBackendNames.AMAZON_BRAKET_SV1,
    AWSBackendNames.AMAZON_BRAKET_TN1,
    AWSBackendNames.AMAZON_BRAKET_DM1,
    NvidiaBackendNames.STATEVECTOR,
    *IBMQBackendNames,
}
