"""
Netflix Hystrix-Inspired Circuit Breaker & Bulkhead System
==========================================================
Provides enterprise fault-tolerance, non-blocking asynchronous SLA enforcement,
concurrency bulkheads, and graceful fallback cascades for D.E.E.P Sovereign AI.

States:
- CLOSED: Normal operation. All requests pass through. Failures increment counter.
- OPEN: Tripped. Short-circuits immediately with zero wait; executes fallback.
- HALF_OPEN: Probing state. Allows a single canary request to test recovery.

Adheres strictly to AGENTS.md Directive 3 (Circuit Breakers & Non-Blocking Asynchronous SLA).
"""

import time
import threading
import functools
from enum import Enum
from typing import Callable, Any, Optional, Dict, List


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    """Raised when an operation is attempted on an OPEN circuit breaker without a fallback."""
    pass


class HystrixCircuitBreaker:
    """
    Enterprise Circuit Breaker with Bulkhead Concurrency Limiting
    and Automatic Canary Probing.
    """
    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: float = 10.0,
        bulkhead_max_concurrent: int = 5,
        default_fallback: Optional[Callable[..., Any]] = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.bulkhead_semaphore = threading.Semaphore(bulkhead_max_concurrent)
        self.bulkhead_max_concurrent = bulkhead_max_concurrent
        self.default_fallback = default_fallback

        self._lock = threading.RLock()
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._last_state_change = time.time()
        self._last_failure_time = 0.0

        # Telemetry Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.short_circuited_requests = 0
        self.fallback_executions = 0

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed to transition to HALF_OPEN
                if (time.time() - self._last_state_change) >= self.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def _transition_to(self, new_state: CircuitState) -> None:
        if self._state != new_state:
            self._state = new_state
            self._last_state_change = time.time()
            if new_state == CircuitState.CLOSED:
                self._consecutive_failures = 0

    def record_success(self) -> None:
        with self._lock:
            self.successful_requests += 1
            if self._state == CircuitState.HALF_OPEN:
                # Canary probe succeeded -> fully recover circuit to CLOSED
                self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                self._consecutive_failures = 0

    def record_failure(self, error: Exception) -> None:
        with self._lock:
            self.failed_requests += 1
            self._last_failure_time = time.time()
            self._consecutive_failures += 1

            if self._state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
                if self._consecutive_failures >= self.failure_threshold or self._state == CircuitState.HALF_OPEN:
                    self._transition_to(CircuitState.OPEN)

    def call(self, func: Callable, *args, fallback: Optional[Callable] = None, **kwargs) -> Any:
        """
        Executes the function protected by the circuit breaker and bulkhead.
        If OPEN, short-circuits immediately to fallback without blocking.
        """
        with self._lock:
            self.total_requests += 1
            current_state = self.state

        effective_fallback = fallback or self.default_fallback

        # 1. Short-circuit if OPEN
        if current_state == CircuitState.OPEN:
            with self._lock:
                self.short_circuited_requests += 1
            if effective_fallback:
                with self._lock:
                    self.fallback_executions += 1
                return effective_fallback(*args, **kwargs)
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is OPEN. Operation short-circuited to preserve system SLA."
            )

        # 2. Concurrency Bulkhead Check (Fail-fast if overloaded)
        acquired = self.bulkhead_semaphore.acquire(blocking=False)
        if not acquired:
            with self._lock:
                self.short_circuited_requests += 1
            if effective_fallback:
                with self._lock:
                    self.fallback_executions += 1
                return effective_fallback(*args, **kwargs)
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' bulkhead saturated (>{self.bulkhead_max_concurrent} active)."
            )

        # 3. Execute with SLA safety
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            if effective_fallback:
                with self._lock:
                    self.fallback_executions += 1
                return effective_fallback(*args, **kwargs)
            raise
        finally:
            self.bulkhead_semaphore.release()

    def __call__(self, fallback: Optional[Callable] = None):
        """Decorator usage: @breaker(fallback=my_fallback)"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.call(func, *args, fallback=fallback, **kwargs)
            return wrapper
        return decorator

    def get_status(self) -> Dict[str, Any]:
        """Returns structured real-time health telemetry for cockpit dashboards."""
        with self._lock:
            current_state = self.state
            return {
                "name": self.name,
                "state": current_state.value,
                "consecutive_failures": self._consecutive_failures,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "time_in_current_state_sec": round(time.time() - self._last_state_change, 2),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "short_circuited_requests": self.short_circuited_requests,
                "fallback_executions": self.fallback_executions,
                "health_ratio": round(
                    (self.successful_requests / self.total_requests * 100)
                    if self.total_requests > 0 else 100.0, 1
                ),
            }


    def trip(self) -> None:
        """Manually forces the circuit breaker into OPEN state for fault injection & testing."""
        with self._lock:
            self._transition_to(CircuitState.OPEN)

    def reset(self) -> None:
        """Manually resets the circuit breaker to CLOSED state and clears failure counters."""
        with self._lock:
            self._consecutive_failures = 0
            self._transition_to(CircuitState.CLOSED)


class CircuitBreakerRegistry:
    """Global manager for all D.E.E.P named circuit breakers."""
    def __init__(self):
        self._breakers: Dict[str, HystrixCircuitBreaker] = {}
        self._lock = threading.Lock()

    def get(self, name: str) -> Optional[HystrixCircuitBreaker]:
        """Retrieves an existing circuit breaker by name."""
        with self._lock:
            return self._breakers.get(name)

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: float = 10.0,
        bulkhead_max_concurrent: int = 5,
        default_fallback: Optional[Callable] = None,
    ) -> HystrixCircuitBreaker:
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = HystrixCircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    bulkhead_max_concurrent=bulkhead_max_concurrent,
                    default_fallback=default_fallback,
                )
            return self._breakers[name]

    def get_telemetry_matrix(self) -> List[Dict[str, Any]]:
        """Returns resilience matrix across all services for the Cockpit HUD."""
        with self._lock:
            return [b.get_status() for b in self._breakers.values()]


# Singleton global registry
global_circuit_registry = CircuitBreakerRegistry()

# Pre-registered core breakers with SLA-tuned parameters
ollama_breaker = global_circuit_registry.get_or_create(
    "ollama_inference",
    failure_threshold=3,
    recovery_timeout=12.0,
    bulkhead_max_concurrent=4,
    default_fallback=lambda *a, **kw: {"status": "circuit_open", "response": "⚠️ Local AI engine temporarily offline. Graceful fallback active."}
)

iot_breaker = global_circuit_registry.get_or_create(
    "iot_smart_home",
    failure_threshold=2,
    recovery_timeout=8.0,
    bulkhead_max_concurrent=2,
    default_fallback=lambda *a, **kw: {"status": "circuit_open", "message": "Smart IoT device unreachable (Circuit Open). Fail-safe maintained."}
)

vision_breaker = global_circuit_registry.get_or_create(
    "vision_hardware",
    failure_threshold=2,
    recovery_timeout=5.0,
    bulkhead_max_concurrent=1,
    default_fallback=lambda *a, **kw: {"status": "circuit_open", "analysis": "Vision sensor busy or unavailable. Circuit breaker engaged."}
)
