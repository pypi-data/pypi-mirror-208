"""Classiq SDK."""
from classiq.interface._version import VERSION as _VERSION
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.control_state import ControlState
from classiq.interface.generator.functions import *  # noqa: F403
from classiq.interface.generator.functions import __all__ as _ifunc_all
from classiq.interface.generator.result import GeneratedCircuit

from classiq import applications, builtin_functions, exceptions, execution, model
from classiq._internals import _qfunc_ext, logger
from classiq._internals.async_utils import (
    enable_jupyter_notebook,
    is_notebook as _is_notebook,
)
from classiq._internals.authentication.authentication import authenticate
from classiq._internals.client import configure
from classiq._internals.config import Configuration
from classiq._internals.help import open_help
from classiq.analyzer import Analyzer
from classiq.executor import Executor
from classiq.model import *  # noqa: F403
from classiq.model import __all__ as _md_all
from classiq.quantum_functions import *  # noqa: F403
from classiq.quantum_functions import __all__ as _qfuncs_all
from classiq.quantum_register import *  # noqa: F403
from classiq.quantum_register import __all__ as _qregs_all

__version__ = _VERSION

if _is_notebook():
    enable_jupyter_notebook()

_sub_modules = [
    "analyzer",
    "applications",
    "builtin_functions",
    "exceptions",
    "execution",
    "model",
    "open_help",
]

__all__ = (
    ["RegisterUserInput", "ControlState", "Analyzer", "Executor", "GeneratedCircuit"]
    + _qregs_all
    + _qfuncs_all
    + _md_all
    + _ifunc_all
    + _sub_modules
)


def __dir__():
    return __all__
