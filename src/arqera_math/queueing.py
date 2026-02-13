"""Queueing Theory Service.

Provides queueing models for multi-agent coordination:
- M/M/1 and M/M/c queue analysis
- Wait time estimation
- Queue stability checking
- Utilization monitoring

Standalone -- no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass
class QueueMetrics:
    """Metrics for a queue."""

    queue_id: str = field(default_factory=lambda: str(uuid4()))
    queue_name: str = ""
    arrival_rate: float = 0.0
    service_rate: float = 1.0
    num_servers: int = 1
    utilization: float = 0.0
    avg_queue_length: float = 0.0
    avg_wait_time: float = 0.0
    avg_system_time: float = 0.0
    is_stable: bool = True
    prob_wait: float = 0.0
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "queue_id": self.queue_id,
            "queue_name": self.queue_name,
            "arrival_rate": self.arrival_rate,
            "service_rate": self.service_rate,
            "num_servers": self.num_servers,
            "utilization": self.utilization,
            "avg_queue_length": self.avg_queue_length,
            "avg_wait_time": self.avg_wait_time,
            "avg_system_time": self.avg_system_time,
            "is_stable": self.is_stable,
            "prob_wait": self.prob_wait,
            "measured_at": self.measured_at.isoformat(),
        }


@dataclass
class AgentQueue:
    """An agent work queue with queueing theory modeling."""

    queue_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    arrival_rate: float = 0.0
    service_rate: float = 1.0
    num_servers: int = 1
    current_depth: int = 0
    total_arrivals: int = 0
    total_completions: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "queue_id": self.queue_id,
            "name": self.name,
            "arrival_rate": self.arrival_rate,
            "service_rate": self.service_rate,
            "num_servers": self.num_servers,
            "current_depth": self.current_depth,
            "total_arrivals": self.total_arrivals,
            "total_completions": self.total_completions,
            "created_at": self.created_at.isoformat(),
        }


class QueueingService:
    """Service for queueing theory analysis.

    Implements M/M/1 and M/M/c queue models for:
    - Wait time estimation
    - Capacity planning
    - Stability analysis
    - Utilization monitoring

    Key formulas:
    - M/M/1: L = lambda / (mu - lambda), W = 1 / (mu - lambda)
    - Utilization: rho = lambda / (c x mu)
    - Stability requires: rho < 1
    """

    def calculate_mm1_metrics(
        self,
        arrival_rate: float,
        service_rate: float,
    ) -> QueueMetrics:
        """Calculate M/M/1 queue metrics.

        Single-server queue analysis.

        Args:
            arrival_rate: lambda - arrivals per second
            service_rate: mu - services per second

        Returns:
            Queue metrics
        """
        if arrival_rate >= service_rate:
            return QueueMetrics(
                queue_name="M/M/1",
                arrival_rate=arrival_rate,
                service_rate=service_rate,
                num_servers=1,
                utilization=(
                    arrival_rate / service_rate if service_rate > 0 else float("inf")
                ),
                avg_queue_length=float("inf"),
                avg_wait_time=float("inf"),
                is_stable=False,
            )

        rho = arrival_rate / service_rate
        avg_length = arrival_rate / (service_rate - arrival_rate)
        avg_wait = 1 / (service_rate - arrival_rate)
        avg_system = (1 / service_rate) + avg_wait

        return QueueMetrics(
            queue_name="M/M/1",
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            num_servers=1,
            utilization=rho,
            avg_queue_length=avg_length,
            avg_wait_time=avg_wait,
            avg_system_time=avg_system,
            is_stable=True,
            prob_wait=rho,
        )

    def calculate_mmc_metrics(
        self,
        arrival_rate: float,
        service_rate: float,
        num_servers: int,
    ) -> QueueMetrics:
        """Calculate M/M/c queue metrics.

        Multi-server queue analysis using Erlang-C formula.

        Args:
            arrival_rate: lambda - arrivals per second
            service_rate: mu - services per second per server
            num_servers: c - number of servers

        Returns:
            Queue metrics
        """
        num_servers = max(num_servers, 1)
        total_capacity = num_servers * service_rate
        rho = arrival_rate / total_capacity if total_capacity > 0 else float("inf")

        if rho >= 1:
            return QueueMetrics(
                queue_name=f"M/M/{num_servers}",
                arrival_rate=arrival_rate,
                service_rate=service_rate,
                num_servers=num_servers,
                utilization=rho,
                avg_queue_length=float("inf"),
                avg_wait_time=float("inf"),
                is_stable=False,
            )

        # Erlang-C calculation
        a = arrival_rate / service_rate  # Offered load

        # P(0) calculation
        sum_term = sum(
            (a**n) / math.factorial(n) for n in range(num_servers)
        )
        last_term = (a**num_servers) / (
            math.factorial(num_servers) * (1 - rho)
        )
        p0 = 1 / (sum_term + last_term)

        # P(wait)
        p_wait = (
            ((a**num_servers) / math.factorial(num_servers)) * p0 / (1 - rho)
        )

        # Average queue length
        avg_length = (
            p_wait * rho / (1 - rho) if rho < 1 else float("inf")
        )

        # Average wait time
        avg_wait = avg_length / arrival_rate if arrival_rate > 0 else 0

        # Average system time
        avg_system = (
            avg_wait + (1 / service_rate) if service_rate > 0 else float("inf")
        )

        return QueueMetrics(
            queue_name=f"M/M/{num_servers}",
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            num_servers=num_servers,
            utilization=rho,
            avg_queue_length=avg_length,
            avg_wait_time=avg_wait,
            avg_system_time=avg_system,
            is_stable=True,
            prob_wait=p_wait,
        )

    def estimate_wait_time(
        self,
        current_queue_depth: int,
        service_rate: float,
        num_servers: int = 1,
    ) -> float:
        """Estimate wait time for a new arrival.

        Args:
            current_queue_depth: Items currently in queue
            service_rate: Service rate per server
            num_servers: Number of servers

        Returns:
            Estimated wait time in seconds
        """
        if num_servers < 1:
            return float("inf")

        total_service_rate = num_servers * service_rate
        if total_service_rate <= 0:
            return float("inf")

        return current_queue_depth / total_service_rate

    def required_servers_for_target_wait(
        self,
        arrival_rate: float,
        service_rate: float,
        target_wait: float,
    ) -> int:
        """Calculate required servers to achieve target wait time.

        Args:
            arrival_rate: Expected arrivals per second
            service_rate: Service rate per server
            target_wait: Target wait time in seconds

        Returns:
            Required number of servers
        """
        if arrival_rate <= 0 or service_rate <= 0 or target_wait <= 0:
            return 1

        min_servers = math.ceil(arrival_rate / service_rate)

        for c in range(min_servers, min_servers + 100):
            metrics = self.calculate_mmc_metrics(arrival_rate, service_rate, c)
            if metrics.is_stable and metrics.avg_wait_time <= target_wait:
                return c

        return min_servers + 100
