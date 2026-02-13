"""Control Theory Service.

Provides PID control for self-healing feedback loops:
- PID controller for health metric stabilization
- Setpoint tracking for system health
- Anti-windup and derivative filtering

Standalone -- no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from arqera_math.constants import get_constant


@dataclass
class ControllerState:
    """State of a PID controller."""

    controller_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    setpoint: float = 1.0
    current_value: float = 0.0
    error: float = 0.0
    error_integral: float = 0.0
    error_derivative: float = 0.0
    last_error: float = 0.0
    output: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "controller_id": self.controller_id,
            "name": self.name,
            "setpoint": self.setpoint,
            "current_value": self.current_value,
            "error": self.error,
            "output": self.output,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ControlAction:
    """A control action computed by the controller."""

    action_id: str = field(default_factory=lambda: str(uuid4()))
    controller_id: str = ""
    correction: float = 0.0
    p_term: float = 0.0
    i_term: float = 0.0
    d_term: float = 0.0
    clamped: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "controller_id": self.controller_id,
            "correction": self.correction,
            "p_term": self.p_term,
            "i_term": self.i_term,
            "d_term": self.d_term,
            "clamped": self.clamped,
            "timestamp": self.timestamp.isoformat(),
        }


class PIDController:
    """PID Controller for system health management.

    Implements the standard PID control law:
    u(t) = Kp x e(t) + Ki x integral(e) + Kd x de/dt

    With anti-windup to prevent integral accumulation when saturated.
    """

    def __init__(
        self,
        name: str = "health_controller",
        setpoint: float = 1.0,
        kp: float | None = None,
        ki: float | None = None,
        kd: float | None = None,
        output_min: float = -1.0,
        output_max: float = 1.0,
    ):
        """Initialize the PID controller.

        Args:
            name: Controller name for identification
            setpoint: Target value (default: 1.0 for health)
            kp: Proportional gain (default from constants)
            ki: Integral gain (default from constants)
            kd: Derivative gain (default from constants)
            output_min: Minimum control output
            output_max: Maximum control output
        """
        self.name = name
        self.setpoint = setpoint
        self.kp = kp if kp is not None else get_constant("K_P_PROPORTIONAL")
        self.ki = ki if ki is not None else get_constant("K_I_INTEGRAL")
        self.kd = kd if kd is not None else get_constant("K_D_DERIVATIVE")
        self.output_min = output_min
        self.output_max = output_max

        # Internal state
        self._error_integral = 0.0
        self._last_error = 0.0
        self._last_time: datetime | None = None
        self._controller_id = str(uuid4())

    def compute(
        self,
        current_value: float,
        dt: float | None = None,
    ) -> ControlAction:
        """Compute control output.

        Args:
            current_value: Current measured value
            dt: Time step (seconds). If None, computed from last call.

        Returns:
            ControlAction with the computed correction
        """
        now = datetime.now(UTC)

        # Compute dt
        if dt is None:
            dt = (now - self._last_time).total_seconds() if self._last_time is not None else 1.0

        dt = max(dt, 0.001)  # Prevent division by zero

        # Compute error
        error = self.setpoint - current_value

        # Proportional term
        p_term = self.kp * error

        # Integral term (with anti-windup)
        self._error_integral += error * dt
        i_term = self.ki * self._error_integral

        # Derivative term
        error_derivative = (error - self._last_error) / dt
        d_term = self.kd * error_derivative

        # Total output
        output = p_term + i_term + d_term

        # Clamp output and apply anti-windup
        clamped = False
        if output > self.output_max:
            output = self.output_max
            clamped = True
            if error > 0:
                self._error_integral -= error * dt
        elif output < self.output_min:
            output = self.output_min
            clamped = True
            if error < 0:
                self._error_integral -= error * dt

        # Update state
        self._last_error = error
        self._last_time = now

        return ControlAction(
            controller_id=self._controller_id,
            correction=output,
            p_term=p_term,
            i_term=i_term,
            d_term=d_term,
            clamped=clamped,
        )

    def reset(self) -> None:
        """Reset controller state."""
        self._error_integral = 0.0
        self._last_error = 0.0
        self._last_time = None

    def get_state(self, current_value: float) -> ControllerState:
        """Get current controller state."""
        return ControllerState(
            controller_id=self._controller_id,
            name=self.name,
            setpoint=self.setpoint,
            current_value=current_value,
            error=self.setpoint - current_value,
            error_integral=self._error_integral,
            error_derivative=(self.setpoint - current_value - self._last_error),
            last_error=self._last_error,
        )


# =============================================================================
# Utility Functions
# =============================================================================


def simple_pid_step(
    error: float,
    error_integral: float,
    last_error: float,
    dt: float = 1.0,
    kp: float = 0.5,
    ki: float = 0.1,
    kd: float = 0.05,
) -> tuple[float, float]:
    """Simple PID step calculation.

    Returns (output, new_error_integral).
    """
    p = kp * error
    i = ki * (error_integral + error * dt)
    d = kd * (error - last_error) / dt if dt > 0 else 0

    return p + i + d, error_integral + error * dt
