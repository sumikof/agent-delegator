"""Auto Scaler.

This module implements automatic scaling algorithms for the distributed orchestrator,
enabling dynamic resource allocation based on workload and performance metrics.
"""

from __future__ import annotations

import time
import threading
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class ScalingStrategy(str, Enum):
    """Scaling strategies."""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"


class ScalingDirection(str, Enum):
    """Scaling directions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"


@dataclass
class ScalingPolicy:
    """Represents a scaling policy."""
    policy_id: str
    name: str
    strategy: ScalingStrategy
    conditions: Dict[str, Any]
    min_instances: int
    max_instances: int
    cooldown_period: float
    scaling_factor: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert scaling policy to dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "strategy": self.strategy,
            "conditions": self.conditions,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "cooldown_period": self.cooldown_period,
            "scaling_factor": self.scaling_factor,
            "description": self.description
        }


@dataclass
class ScalingEvent:
    """Represents a scaling event."""
    event_id: str
    policy_id: str
    direction: ScalingDirection
    timestamp: float
    current_instances: int
    target_instances: int
    reason: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert scaling event to dictionary."""
        return {
            "event_id": self.event_id,
            "policy_id": self.policy_id,
            "direction": self.direction,
            "timestamp": self.timestamp,
            "current_instances": self.current_instances,
            "target_instances": self.target_instances,
            "reason": self.reason,
            "status": self.status
        }


class AutoScaler:
    """Automatic scaler for the distributed orchestrator."""

    def __init__(self):
        self._scaling_policies: Dict[str, ScalingPolicy] = {}
        self._scaling_events: List[ScalingEvent] = []
        self._lock = threading.Lock()
        self._running = False
        self._scaling_thread = None
        self._monitoring_interval = 30.0  # seconds
        self._last_scaling_time = 0.0
        self._current_instances = 1

    def add_scaling_policy(self, policy: ScalingPolicy) -> None:
        """Add a scaling policy."""
        with self._lock:
            self._scaling_policies[policy.policy_id] = policy
        
        logger.info(f"Added scaling policy: {policy.name}")

    def start_scaling(self, interval: float = 30.0) -> None:
        """Start the auto scaling loop."""
        self._monitoring_interval = interval
        self._running = True
        
        self._scaling_thread = threading.Thread(
            target=self._scaling_loop, daemon=True
        )
        self._scaling_thread.start()
        
        logger.info(f"Started auto scaler with interval {interval} seconds")

    def stop_scaling(self) -> None:
        """Stop the auto scaling loop."""
        self._running = False
        if self._scaling_thread:
            self._scaling_thread.join(timeout=5.0)
        
        logger.info("Stopped auto scaler")

    def _scaling_loop(self) -> None:
        """Main scaling loop."""
        while self._running:
            try:
                self._check_scaling_conditions()
                time.sleep(self._monitoring_interval)
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                time.sleep(5.0)  # Wait before retrying

    def _check_scaling_conditions(self) -> None:
        """Check if scaling conditions are met."""
        current_time = time.time()
        
        # Check cooldown period
        if (current_time - self._last_scaling_time) < 60.0:  # 1 minute cooldown
            return
        
        with self._lock:
            # Get current metrics (simulated)
            metrics = self._get_current_metrics()
            
            # Check each scaling policy
            for policy in self._scaling_policies.values():
                if self._check_policy_conditions(policy, metrics):
                    self._execute_scaling(policy)
                    self._last_scaling_time = current_time
                    break

    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics (simulated)."""
        # In a real implementation, this would get real metrics
        return {
            "cpu_usage": 0.6 + (self._current_instances * 0.1),  # Simulate increasing load
            "memory_usage": 0.5 + (self._current_instances * 0.05),
            "task_queue_length": 20 + (self._current_instances * 5),
            "response_time": 100 + (self._current_instances * 10)
        }

    def _check_policy_conditions(self, policy: ScalingPolicy, 
                                metrics: Dict[str, Any]) -> bool:
        """Check if scaling policy conditions are met."""
        for condition_key, condition_value in policy.conditions.items():
            if condition_key not in metrics:
                return False
            
            metric_value = metrics[condition_key]
            
            if isinstance(condition_value, dict):
                # Range condition
                if "min" in condition_value and metric_value < condition_value["min"]:
                    return False
                if "max" in condition_value and metric_value > condition_value["max"]:
                    return False
            else:
                # Exact value condition
                if metric_value != condition_value:
                    return False
        
        return True

    def _execute_scaling(self, policy: ScalingPolicy) -> None:
        """Execute scaling based on policy."""
        # Determine scaling direction
        metrics = self._get_current_metrics()
        
        # Simple scaling logic based on CPU usage
        cpu_usage = metrics.get("cpu_usage", 0.5)
        
        if cpu_usage > 0.8:
            # Scale up
            target_instances = min(
                self._current_instances + 1, 
                policy.max_instances
            )
            
            if target_instances > self._current_instances:
                self._scale_instances(target_instances, ScalingDirection.SCALE_UP, policy)
        elif cpu_usage < 0.3 and self._current_instances > policy.min_instances:
            # Scale down
            target_instances = max(
                self._current_instances - 1, 
                policy.min_instances
            )
            
            if target_instances < self._current_instances:
                self._scale_instances(target_instances, ScalingDirection.SCALE_DOWN, policy)

    def _scale_instances(self, target_instances: int, direction: ScalingDirection,
                        policy: ScalingPolicy) -> None:
        """Scale the number of instances."""
        import uuid
        
        event_id = str(uuid.uuid4())
        
        scaling_event = ScalingEvent(
            event_id=event_id,
            policy_id=policy.policy_id,
            direction=direction,
            timestamp=time.time(),
            current_instances=self._current_instances,
            target_instances=target_instances,
            reason=f"{direction} due to policy {policy.name}",
            status="pending"
        )
        
        with self._lock:
            self._scaling_events.append(scaling_event)
        
        logger.info(f"Scaling {direction} from {self._current_instances} to {target_instances} instances")
        
        # Simulate scaling operation
        time.sleep(2)  # Simulate scaling time
        
        # Update current instances
        self._current_instances = target_instances
        
        # Update scaling event status
        with self._lock:
            for event in self._scaling_events:
                if event.event_id == event_id:
                    event.status = "completed"
                    break
        
        logger.info(f"Successfully scaled to {target_instances} instances")

    def get_scaling_status(self) -> Dict[str, Any]:
        """Get the current scaling status."""
        with self._lock:
            return {
                "scaling_policies": len(self._scaling_policies),
                "scaling_events": len(self._scaling_events),
                "current_instances": self._current_instances,
                "status": "running" if self._running else "stopped",
                "last_scaling_time": self._last_scaling_time
            }

    def get_scaling_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get scaling event history."""
        with self._lock:
            return [event.to_dict() for event in self._scaling_events[-limit:]]

    def create_default_scaling_policies(self) -> None:
        """Create default scaling policies."""
        import uuid
        
        # CPU-based scaling policy
        cpu_scaling_policy = ScalingPolicy(
            policy_id=str(uuid.uuid4()),
            name="cpu_based_scaling",
            strategy=ScalingStrategy.REACTIVE,
            conditions={
                "cpu_usage": {"min": 0.8}
            },
            min_instances=1,
            max_instances=10,
            cooldown_period=300.0,  # 5 minutes
            scaling_factor=1.0,
            description="Scale based on CPU usage"
        )
        
        # Task queue-based scaling policy
        task_queue_policy = ScalingPolicy(
            policy_id=str(uuid.uuid4()),
            name="task_queue_scaling",
            strategy=ScalingStrategy.REACTIVE,
            conditions={
                "task_queue_length": {"min": 50}
            },
            min_instances=2,
            max_instances=8,
            cooldown_period=600.0,  # 10 minutes
            scaling_factor=1.0,
            description="Scale based on task queue length"
        )
        
        # Memory-based scaling policy
        memory_scaling_policy = ScalingPolicy(
            policy_id=str(uuid.uuid4()),
            name="memory_based_scaling",
            strategy=ScalingStrategy.REACTIVE,
            conditions={
                "memory_usage": {"min": 0.75}
            },
            min_instances=1,
            max_instances=6,
            cooldown_period=300.0,  # 5 minutes
            scaling_factor=1.0,
            description="Scale based on memory usage"
        )
        
        with self._lock:
            self._scaling_policies[cpu_scaling_policy.policy_id] = cpu_scaling_policy
            self._scaling_policies[task_queue_policy.policy_id] = task_queue_policy
            self._scaling_policies[memory_scaling_policy.policy_id] = memory_scaling_policy
        
        logger.info("Created default scaling policies")


# Global auto scaler instance
auto_scaler = AutoScaler()


def get_auto_scaler() -> AutoScaler:
    """Get the global auto scaler instance."""
    global auto_scaler
    return auto_scaler