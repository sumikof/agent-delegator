"""
Resource Monitor for parallel agent execution.

This module provides monitoring capabilities for:
- System resource usage (CPU, memory)
- Task execution metrics
- Worker health monitoring
- Performance benchmarking
"""

import threading
import time
import psutil
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from collections import deque

from .task_queue import Task, TaskStatus


@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    memory_total: float
    disk_usage: float
    
    @classmethod
    def capture(cls) -> 'SystemMetrics':
        """Capture current system metrics."""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return cls(
                timestamp=time.time(),
                cpu_usage=cpu,
                memory_usage=memory.used,
                memory_total=memory.total,
                disk_usage=disk.used
            )
        except Exception:
            # Fallback to dummy metrics if psutil is not available
            return cls(
                timestamp=time.time(),
                cpu_usage=0.0,
                memory_usage=0,
                memory_total=1,
                disk_usage=0
            )


@dataclass
class TaskMetrics:
    """Task execution metrics."""
    task_id: str
    agent_type: str
    priority: str
    status: str
    execution_time: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None


class ResourceMonitor:
    """Resource monitor for parallel agent execution."""

    def __init__(self, monitoring_interval: float = 5.0, history_size: int = 100):
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        self.system_metrics_history = deque(maxlen=history_size)
        self.task_metrics_history = deque(maxlen=history_size)
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        self.callbacks = []

    def start(self):
        """Start the resource monitor."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop(self):
        """Stop the resource monitor."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Capture system metrics
                system_metrics = SystemMetrics.capture()
                
                with self.lock:
                    self.system_metrics_history.append(system_metrics)
                
                # Notify callbacks
                self._notify_callbacks(system_metrics)
                
                # Sleep for the monitoring interval
                time.sleep(self.monitoring_interval)
            except Exception as e:
                # Log error and continue
                print(f"Monitoring error: {e}")
                time.sleep(self.monitoring_interval)

    def record_task_metrics(self, task: Task):
        """Record metrics for a completed task."""
        metrics = TaskMetrics(
            task_id=task.task_id,
            agent_type=task.agent_type,
            priority=task.priority.name,
            status=task.status.name,
            execution_time=task.completed_at - task.started_at if task.started_at and task.completed_at else None,
            start_time=task.started_at,
            end_time=task.completed_at,
            error=task.error
        )
        
        with self.lock:
            self.task_metrics_history.append(metrics)

    def get_system_metrics_history(self) -> List[SystemMetrics]:
        """Get the history of system metrics."""
        with self.lock:
            return list(self.system_metrics_history)

    def get_task_metrics_history(self) -> List[TaskMetrics]:
        """Get the history of task metrics."""
        with self.lock:
            return list(self.task_metrics_history)

    def get_current_system_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics."""
        with self.lock:
            if self.system_metrics_history:
                return self.system_metrics_history[-1]
            else:
                # Return dummy metrics if no history available
                return SystemMetrics.capture()

    def register_callback(self, callback: Callable[[SystemMetrics], None]):
        """Register a callback for system metrics updates."""
        with self.lock:
            self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[SystemMetrics], None]):
        """Unregister a callback."""
        with self.lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)

    def _notify_callbacks(self, metrics: SystemMetrics):
        """Notify all registered callbacks."""
        with self.lock:
            for callback in self.callbacks:
                try:
                    callback(metrics)
                except Exception:
                    # Don't let callback errors crash the monitor
                    pass

    def get_average_cpu_usage(self) -> float:
        """Get the average CPU usage over the monitoring period."""
        with self.lock:
            if not self.system_metrics_history:
                return 0.0
            return sum(m.cpu_usage for m in self.system_metrics_history) / len(self.system_metrics_history)

    def get_average_memory_usage(self) -> float:
        """Get the average memory usage over the monitoring period."""
        with self.lock:
            if not self.system_metrics_history:
                return 0.0
            return sum(m.memory_usage for m in self.system_metrics_history) / len(self.system_metrics_history)