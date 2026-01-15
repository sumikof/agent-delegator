"""
Performance Metrics Collector

Collects and aggregates performance metrics from agent execution,
including response times, success rates, and resource utilization.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import psutil
import json
import os


@dataclass
class AgentMetric:
    """Performance metric for a single agent execution."""
    agent_name: str
    task_name: str
    start_time: float
    end_time: float
    success: bool
    error_message: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

    @property
    def duration_seconds(self) -> float:
        """Calculate execution duration in seconds."""
        return self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "task_name": self.task_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "additional_data": self.additional_data,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat(),
        }


class MetricsCollector:
    """Collects and manages performance metrics for agent execution."""

    def __init__(self, storage_dir: str = "/tmp/agent_metrics"):
        """Initialize metrics collector.
        
        Args:
            storage_dir: Directory to store metrics data
        """
        self.storage_dir = storage_dir
        self.metrics: List[AgentMetric] = []
        self.lock = threading.Lock()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Start background thread for periodic metrics persistence
        self._stop_event = threading.Event()
        self._persistence_thread = threading.Thread(
            target=self._periodic_persistence, daemon=True
        )
        self._persistence_thread.start()

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage metrics."""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
            
            return {
                "memory_usage_mb": memory_info.rss / (1024 * 1024),
                "cpu_usage_percent": cpu_percent,
            }
        except Exception:
            return {
                "memory_usage_mb": None,
                "cpu_usage_percent": None,
            }

    def start_agent_monitoring(self, agent_name: str, task_name: str) -> "AgentMonitorContext":
        """Start monitoring an agent execution.
        
        Args:
            agent_name: Name of the agent being executed
            task_name: Name of the task being performed
            
        Returns:
            Context manager for tracking the agent execution
        """
        return AgentMonitorContext(self, agent_name, task_name)

    def record_metric(self, metric: AgentMetric):
        """Record a performance metric.
        
        Args:
            metric: AgentMetric to record
        """
        with self.lock:
            self.metrics.append(metric)

    def get_metrics(self, agent_name: Optional[str] = None) -> List[AgentMetric]:
        """Get recorded metrics, optionally filtered by agent name.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            List of matching metrics
        """
        with self.lock:
            if agent_name:
                return [m for m in self.metrics if m.agent_name == agent_name]
            return self.metrics.copy()

    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics across all metrics."""
        with self.lock:
            if not self.metrics:
                return {
                    "total_executions": 0,
                    "success_rate": 0.0,
                    "avg_duration_seconds": 0.0,
                    "agents": {},
                }
            
            total_executions = len(self.metrics)
            successful_executions = sum(1 for m in self.metrics if m.success)
            success_rate = successful_executions / total_executions if total_executions > 0 else 0.0
            avg_duration = sum(m.duration_seconds for m in self.metrics) / total_executions
            
            # Group by agent
            agent_stats = {}
            for metric in self.metrics:
                if metric.agent_name not in agent_stats:
                    agent_stats[metric.agent_name] = {
                        "executions": 0,
                        "successes": 0,
                        "total_duration": 0.0,
                    }
                
                stats = agent_stats[metric.agent_name]
                stats["executions"] += 1
                if metric.success:
                    stats["successes"] += 1
                stats["total_duration"] += metric.duration_seconds
            
            # Calculate agent-level averages
            for agent_name, stats in agent_stats.items():
                stats["success_rate"] = stats["successes"] / stats["executions"] if stats["executions"] > 0 else 0.0
                stats["avg_duration"] = stats["total_duration"] / stats["executions"] if stats["executions"] > 0 else 0.0
            
            return {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "success_rate": success_rate,
                "avg_duration_seconds": avg_duration,
                "agents": agent_stats,
                "timestamp": datetime.now().isoformat(),
            }

    def _periodic_persistence(self):
        """Periodically persist metrics to disk."""
        while not self._stop_event.wait(60):  # Persist every 60 seconds
            self.persist_metrics()

    def persist_metrics(self):
        """Persist current metrics to disk."""
        metrics_to_persist = []
        
        # Copy metrics to persist (minimize lock time)
        with self.lock:
            if not self.metrics:
                return
            metrics_to_persist = self.metrics.copy()
            # Clear metrics after copying
            self.metrics.clear()
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"metrics_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Convert metrics to serializable format
        metrics_data = [metric.to_dict() for metric in metrics_to_persist]
        
        try:
            with open(filepath, "w") as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            print(f"Error persisting metrics: {e}")

    def shutdown(self):
        """Shutdown the metrics collector."""
        self._stop_event.set()
        self._persistence_thread.join()
        self.persist_metrics()  # Final persistence


class AgentMonitorContext:
    """Context manager for monitoring agent execution."""

    def __init__(self, collector: MetricsCollector, agent_name: str, task_name: str):
        self.collector = collector
        self.agent_name = agent_name
        self.task_name = task_name
        self.start_time = time.time()
        self.system_metrics = None

    def __enter__(self):
        """Start monitoring when entering context."""
        self.system_metrics = self.collector._get_system_metrics()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring and record metric when exiting context."""
        end_time = time.time()
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        metric = AgentMetric(
            agent_name=self.agent_name,
            task_name=self.task_name,
            start_time=self.start_time,
            end_time=end_time,
            success=success,
            error_message=error_message,
            memory_usage_mb=self.system_metrics.get("memory_usage_mb"),
            cpu_usage_percent=self.system_metrics.get("cpu_usage_percent"),
        )
        
        self.collector.record_metric(metric)
        
        # Don't suppress exceptions
        return False