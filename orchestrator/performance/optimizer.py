"""Performance Optimizer.

This module implements performance optimization algorithms and strategies
for the distributed orchestrator system.
"""

from __future__ import annotations

import time
import threading
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class OptimizationStrategy(str, Enum):
    """Performance optimization strategies."""
    LOAD_BALANCING = "load_balancing"
    RESOURCE_ALLOCATION = "resource_allocation"
    TASK_SCHEDULING = "task_scheduling"
    CACHING = "caching"
    BATCH_PROCESSING = "batch_processing"
    PARALLELIZATION = "parallelization"


@dataclass
class OptimizationRule:
    """Represents an optimization rule."""
    rule_id: str
    name: str
    strategy: OptimizationStrategy
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert optimization rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "strategy": self.strategy,
            "conditions": self.conditions,
            "actions": self.actions,
            "priority": self.priority,
            "description": self.description
        }


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    metric_id: str
    name: str
    value: float
    timestamp: float
    threshold: Optional[float]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert performance metric to dictionary."""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "threshold": self.threshold,
            "status": self.status
        }


class PerformanceOptimizer:
    """Performance optimizer for the distributed orchestrator."""

    def __init__(self):
        self._optimization_rules: Dict[str, OptimizationRule] = {}
        self._performance_metrics: Dict[str, PerformanceMetric] = {}
        self._lock = threading.Lock()
        self._running = False
        self._optimization_thread = None
        self._optimization_interval = 60.0  # seconds

    def add_optimization_rule(self, rule: OptimizationRule) -> None:
        """Add an optimization rule."""
        with self._lock:
            self._optimization_rules[rule.rule_id] = rule
        
        logger.info(f"Added optimization rule: {rule.name}")

    def add_performance_metric(self, metric: PerformanceMetric) -> None:
        """Add a performance metric."""
        with self._lock:
            self._performance_metrics[metric.metric_id] = metric
        
        logger.debug(f"Added performance metric: {metric.name} = {metric.value}")

    def start_optimization(self, interval: float = 60.0) -> None:
        """Start the performance optimization loop."""
        self._optimization_interval = interval
        self._running = True
        
        self._optimization_thread = threading.Thread(
            target=self._optimization_loop, daemon=True
        )
        self._optimization_thread.start()
        
        logger.info(f"Started performance optimizer with interval {interval} seconds")

    def stop_optimization(self) -> None:
        """Stop the performance optimization loop."""
        self._running = False
        if self._optimization_thread:
            self._optimization_thread.join(timeout=5.0)
        
        logger.info("Stopped performance optimizer")

    def _optimization_loop(self) -> None:
        """Main optimization loop."""
        while self._running:
            try:
                self._apply_optimizations()
                time.sleep(self._optimization_interval)
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                time.sleep(5.0)  # Wait before retrying

    def _apply_optimizations(self) -> None:
        """Apply optimization rules based on current performance metrics."""
        with self._lock:
            # Get current metrics
            metrics = list(self._performance_metrics.values())
            
            # Apply each optimization rule
            for rule in self._optimization_rules.values():
                if self._check_rule_conditions(rule, metrics):
                    self._execute_rule_actions(rule)

    def _check_rule_conditions(self, rule: OptimizationRule, 
                              metrics: List[PerformanceMetric]) -> bool:
        """Check if optimization rule conditions are met."""
        # Simplified condition checking
        # In a real implementation, this would be more sophisticated
        
        for condition_key, condition_value in rule.conditions.items():
            # Find metric that matches the condition
            metric_found = False
            for metric in metrics:
                if metric.name == condition_key:
                    if isinstance(condition_value, dict):
                        # Range condition
                        if "min" in condition_value and metric.value < condition_value["min"]:
                            return False
                        if "max" in condition_value and metric.value > condition_value["max"]:
                            return False
                    else:
                        # Exact value condition
                        if metric.value != condition_value:
                            return False
                    metric_found = True
                    break
            
            if not metric_found:
                return False
        
        return True

    def _execute_rule_actions(self, rule: OptimizationRule) -> None:
        """Execute optimization rule actions."""
        logger.info(f"Executing optimization rule: {rule.name}")
        
        # Simulate action execution
        if rule.strategy == OptimizationStrategy.LOAD_BALANCING:
            self._optimize_load_balancing(rule.actions)
        elif rule.strategy == OptimizationStrategy.RESOURCE_ALLOCATION:
            self._optimize_resource_allocation(rule.actions)
        elif rule.strategy == OptimizationStrategy.TASK_SCHEDULING:
            self._optimize_task_scheduling(rule.actions)
        elif rule.strategy == OptimizationStrategy.CACHING:
            self._optimize_caching(rule.actions)
        elif rule.strategy == OptimizationStrategy.BATCH_PROCESSING:
            self._optimize_batch_processing(rule.actions)
        elif rule.strategy == OptimizationStrategy.PARALLELIZATION:
            self._optimize_parallelization(rule.actions)

    def _optimize_load_balancing(self, actions: Dict[str, Any]) -> None:
        """Optimize load balancing."""
        # Simulate load balancing optimization
        logger.info("Optimizing load balancing")
        
        # In a real implementation, this would adjust load balancing algorithms
        # based on current system load and performance metrics

    def _optimize_resource_allocation(self, actions: Dict[str, Any]) -> None:
        """Optimize resource allocation."""
        # Simulate resource allocation optimization
        logger.info("Optimizing resource allocation")
        
        # In a real implementation, this would reallocate resources based on
        # current usage patterns and performance requirements

    def _optimize_task_scheduling(self, actions: Dict[str, Any]) -> None:
        """Optimize task scheduling."""
        # Simulate task scheduling optimization
        logger.info("Optimizing task scheduling")
        
        # In a real implementation, this would adjust task scheduling algorithms
        # based on current workload and performance metrics

    def _optimize_caching(self, actions: Dict[str, Any]) -> None:
        """Optimize caching strategy."""
        # Simulate caching optimization
        logger.info("Optimizing caching strategy")
        
        # In a real implementation, this would adjust cache sizes and
        # eviction policies based on current usage patterns

    def _optimize_batch_processing(self, actions: Dict[str, Any]) -> None:
        """Optimize batch processing."""
        # Simulate batch processing optimization
        logger.info("Optimizing batch processing")
        
        # In a real implementation, this would adjust batch sizes and
        # processing intervals based on current workload

    def _optimize_parallelization(self, actions: Dict[str, Any]) -> None:
        """Optimize parallel processing."""
        # Simulate parallelization optimization
        logger.info("Optimizing parallel processing")
        
        # In a real implementation, this would adjust parallel processing
        # parameters based on current system capabilities

    def get_optimization_status(self) -> Dict[str, Any]:
        """Get the current optimization status."""
        with self._lock:
            return {
                "optimization_rules": len(self._optimization_rules),
                "performance_metrics": len(self._performance_metrics),
                "status": "running" if self._running else "stopped",
                "last_optimization": time.time()
            }

    def create_default_optimization_rules(self) -> None:
        """Create default optimization rules."""
        import uuid
        
        # Load balancing rule
        load_balancing_rule = OptimizationRule(
            rule_id=str(uuid.uuid4()),
            name="high_load_balancing",
            strategy=OptimizationStrategy.LOAD_BALANCING,
            conditions={
                "cpu_usage": {"min": 0.8},
                "memory_usage": {"min": 0.75}
            },
            actions={
                "algorithm": "least_connections",
                "threshold": 0.9
            },
            priority=1,
            description="Optimize load balancing when system is under high load"
        )
        
        # Resource allocation rule
        resource_allocation_rule = OptimizationRule(
            rule_id=str(uuid.uuid4()),
            name="resource_allocation_optimization",
            strategy=OptimizationStrategy.RESOURCE_ALLOCATION,
            conditions={
                "task_queue_length": {"min": 50},
                "average_task_time": {"max": 5.0}
            },
            actions={
                "scale_up": True,
                "additional_resources": 2
            },
            priority=2,
            description="Allocate additional resources when task queue is long"
        )
        
        # Task scheduling rule
        task_scheduling_rule = OptimizationRule(
            rule_id=str(uuid.uuid4()),
            name="priority_task_scheduling",
            strategy=OptimizationStrategy.TASK_SCHEDULING,
            conditions={
                "high_priority_tasks": {"min": 10}
            },
            actions={
                "algorithm": "priority_based",
                "preempt_lower_priority": True
            },
            priority=1,
            description="Optimize task scheduling for high priority tasks"
        )
        
        with self._lock:
            self._optimization_rules[load_balancing_rule.rule_id] = load_balancing_rule
            self._optimization_rules[resource_allocation_rule.rule_id] = resource_allocation_rule
            self._optimization_rules[task_scheduling_rule.rule_id] = task_scheduling_rule
        
        logger.info("Created default optimization rules")


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global performance_optimizer
    return performance_optimizer