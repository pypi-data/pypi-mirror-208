import re

from classiq.interface.analyzer.result import QasmCode

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function

QASM_VERSION_REGEX = re.compile("OPENQASM (\\d*.\\d*);")


async def qasm_show_interactive_async(qasm_code: str) -> None:
    circuit = await ApiWrapper.get_generated_circuit_from_qasm(QasmCode(code=qasm_code))
    circuit.show()  # type: ignore[attr-defined]


qasm_show_interactive = syncify_function(qasm_show_interactive_async)
