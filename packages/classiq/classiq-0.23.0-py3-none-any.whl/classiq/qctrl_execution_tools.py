import sys

import fireopal
import qctrlclient

from classiq.interface.backend.backend_preferences import (
    IBMBackendPreferences,
    QctrlOptimizationPreferences,
)
from classiq.interface.executor.execution_preferences import ExecutionPreferences

from classiq.exceptions import ClassiqExecutionError

VALID_QASM_FOR_QCTRL = [
    'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[1];\ncreg c[1];\nx q[0];\nmeasure q[0] -> c[0];\n'
]


def _get_qctrl_auth_token(_preferences: ExecutionPreferences) -> dict:
    ibm_credentials = handle_ibm_credentials_for_qctrl(_preferences)
    circuit_errors = fireopal.validate(
        circuits=VALID_QASM_FOR_QCTRL, credentials=ibm_credentials
    )
    if len(circuit_errors["results"]) > 0:
        raise ClassiqExecutionError(
            f"QCtrl validation errors {circuit_errors['results']}"
        )
    qctrl_auth = qctrlclient.globals._REGISTRY["DEFAULT_CLI_AUTH"]
    return qctrl_auth._get_saved_token()


def handle_ibm_credentials_for_qctrl(preferences: ExecutionPreferences):
    if isinstance(preferences.backend_preferences, IBMBackendPreferences):
        ibm_credentials = {"token": preferences.backend_preferences.access_token}
        ibm_credentials.update(preferences.backend_preferences.provider.dict())
    else:
        raise ClassiqExecutionError("QCtrl can only be used with IBM backend")
    return ibm_credentials


async def validate_qctrl(preferences) -> QctrlOptimizationPreferences:
    qctrl_prefs = preferences.backend_preferences.qctrl_preferences
    if qctrl_prefs.use_qctrl:
        if sys.version_info < (3, 8):
            raise ClassiqExecutionError("Cannot run QCtrl with python < 3.8")

    qctrl_prefs.qctrl_access_token = _get_qctrl_auth_token(preferences)
    return qctrl_prefs
