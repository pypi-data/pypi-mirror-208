import pydantic

from classiq.interface.generator import function_params
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.parameters import ParameterFloatType
from classiq.interface.generator.standard_gates.standard_gates import (
    DEFAULT_STANDARD_GATE_ARG_NAME,
)


class UGate(function_params.FunctionParams):
    """
    Matrix representation:

    U(gam, phi,theta, lam) =
    e^(i*gam) *
    cos(theta/2) & -e^(i*lam)*sin(theta/2) \\
    e^(i*phi)*sin(theta/2) & e^(i*(phi+lam))*cos(theta/2) \\
    """

    theta: ParameterFloatType = pydantic.Field(
        description="Angle to rotate by the Y-axis.",
        is_exec_param=True,
    )

    phi: ParameterFloatType = pydantic.Field(
        description="First angle to rotate by the Z-axis.",
        is_exec_param=True,
    )

    lam: ParameterFloatType = pydantic.Field(
        description="Second angle to rotate by the Z-axis.",
        is_exec_param=True,
    )

    gam: ParameterFloatType = pydantic.Field(
        description="Angle to apply phase gate by.",
        is_exec_param=True,
    )

    _inputs = pydantic.PrivateAttr(
        default={
            DEFAULT_STANDARD_GATE_ARG_NAME: RegisterUserInput(
                name=DEFAULT_STANDARD_GATE_ARG_NAME, size=1
            )
        }
    )
    _outputs = pydantic.PrivateAttr(
        default={
            DEFAULT_STANDARD_GATE_ARG_NAME: RegisterUserInput(
                name=DEFAULT_STANDARD_GATE_ARG_NAME, size=1
            )
        }
    )

    @property
    def is_parametric(self) -> bool:
        return not all(
            isinstance(getattr(self, angle), (float, int)) for angle in self._params
        )
