import logging
from typing import List

_logger = logging.getLogger(__name__)


class ClassiqError(Exception):
    def __init__(self, message: str, log_level: int = logging.ERROR) -> None:
        super().__init__(message)
        _logger.log(log_level, "%s\n", message)


class ClassiqExecutionError(ClassiqError):
    pass


class ClassiqMissingOutputFormatError(ClassiqError):
    def __init__(self, missing_formats: List[str]) -> None:
        msg = (
            f"Cannot create program because output format is missing. "
            f"Expected one of the following formats: {missing_formats}"
        )
        super().__init__(message=msg)


class ClassiqCombinatorialOptimizationError(ClassiqError):
    pass


class ClassiqArithmeticError(ClassiqError):
    pass


class ClassiqOracleError(ClassiqError):
    pass


class ClassiqAnalyzerError(ClassiqError):
    pass


class ClassiqAnalyzerGraphError(ClassiqError):
    pass


class ClassiqAPIError(ClassiqError):
    pass


class ClassiqVersionError(ClassiqError):
    pass


class ClassiqValueError(ClassiqError, ValueError):
    pass


class ClassiqIndexError(ClassiqError, IndexError):
    pass


class ClassiqWiringError(ClassiqValueError):
    pass


class ClassiqControlError(ClassiqError):
    def __init__(self) -> None:
        message = "Repeated control names, please rename the control states"
        super().__init__(message=message)


class ClassiqQRegError(ClassiqValueError):
    pass


class ClassiqQFuncError(ClassiqValueError):
    pass


class ClassiqQSVMError(ClassiqValueError):
    pass


class ClassiqQNNError(ClassiqValueError):
    pass


class ClassiqTorchError(ClassiqQNNError):
    pass


class ClassiqChemistryError(ClassiqError):
    pass


class ClassiqRemoveOrbitalsError(ClassiqChemistryError):
    pass


class ClassiqAuthenticationError(ClassiqError):
    pass


class ClassiqExpiredTokenError(ClassiqAuthenticationError):
    pass


class ClassiqFileNotFoundError(FileNotFoundError):
    pass


class ClassiqStateInitializationError(ClassiqError):
    pass


class ClassiqPasswordManagerSelectionError(ClassiqError):
    pass


class ClassiqMismatchIOsError(ClassiqError):
    pass


class ClassiqNotImplementedError(ClassiqError, NotImplementedError):
    pass
