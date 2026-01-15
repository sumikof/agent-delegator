"""
Performance Monitor

Monitors overall system performance and task queue status for the self-organizing
agent system. Provides real-time metrics and queue monitoring capabilities.
"""

import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import deque
import json
import os


@dataclass
class TaskQueueStatus:
    """Current status of the task queue."""
    pending_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    queue_length: int
    average_wait_time: float
    max_wait_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task queue status to dictionary."""
        return {
            "pending_tasks": self.pending_tasks,
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "queue_length": self.queue_length,
            "average_wait_time": self.average_wait_time,
            "max_wait_time": self.max_wait_time,
            "timestamp": time.time()
        }


@dataclass
class PerformanceMetrics:
    """Current performance metrics."""
    system_load: float
    memory_usage_mb: float
    cpu_usage_percent: float
    agent_success_rate: float
    average_response_time: float
    error_rate: float
    throughput: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert performance metrics to dictionary."""
        return {
            "system_load": self.system_load,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "agent_success_rate": self.agent_success_rate,
            "average_response_time": self.average_response_time,
            "error_rate": self.error_rate,
            "throughput": self.throughput,
            "timestamp": time.time()
        }


class PerformanceMonitor:
    """Monitors system performance and task queue status."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self._task_queue_status = TaskQueueStatus(
            pending_tasks=0,
            active_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            queue_length=0,
            average_wait_time=0.0,
            max_wait_time=0.0
        )
        
        self._performance_metrics = PerformanceMetrics(
            system_load=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            agent_success_rate=1.0,
            average_response_time=0.0,
            error_rate=0.0,
            throughput=0.0
        )
        
        self._lock = threading.Lock()
        self._metrics_history = deque(maxlen=100)
        self._queue_history = deque(maxlen=100)
    
    def get_task_queue_status(self) -> Dict[str, Any]:
        """Get current task queue status."""
        with self._lock:
            return self._task_queue_status.to_dict()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        with self._lock:
            return self._performance_metrics.to_dict()
    
    def update_task_queue_status(
        self,
        pending_tasks: int,
        active_tasks: int,
        completed_tasks: int,
        failed_tasks: int,
        queue_length: int,
        average_wait_time: float,
        max_wait_time: float
    ) -> None:
        """Update task queue status."""
        with self._lock:
            self._task_queue_status = TaskQueueStatus(
                pending_tasks=pending_tasks,
                active_tasks=active_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                queue_length=queue_length,
                average_wait_time=average_wait_time,
                max_wait_time=max_wait_time
            )
            self._queue_history.append(self._task_queue_status.to_dict())
    
    def update_performance_metrics(
        self,
        system_load: float,
        memory_usage_mb: float,
        cpu_usage_percent: float,
        agent_success_rate: float,
        average_response_time: float,
        error_rate: float,
        throughput: float
    ) -> None:
        """Update performance metrics."""
        with self._lock:
            self._performance_metrics = PerformanceMetrics(
                system_load=system_load,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                agent_success_rate=agent_success_rate,
                average_response_time=average_response_time,
                error_rate=error_rate,
                throughput=throughput
            )
            self._metrics_history.append(self._performance_metrics.to_dict())
    
    def get_metrics_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics history."""
        with self._lock:
            return list(self._metrics_history)[-limit:]
    
    def get_queue_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent queue history."""
        with self._lock:
            return list(self._queue_history)[-limit:]