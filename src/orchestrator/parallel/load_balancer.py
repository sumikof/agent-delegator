"""
Load Balancer for parallel agent execution.

This module implements intelligent load balancing algorithms for:
- Task distribution across workers
- Resource-aware scheduling
- Priority-based routing
- Worker health monitoring
"""

import threading
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .task_queue import Task, TaskPriority
from .worker_pool import WorkerPool


@dataclass
class WorkerStatus:
    """Status information for a worker."""
    worker_id: str
    current_load: float = 0.0
    last_active: float = 0.0
    healthy: bool = True
    
    def update_load(self, load: float):
        """Update the worker's current load."""
        self.current_load = load
        self.last_active = time.time()


class LoadBalancer:
    """Intelligent load balancer for parallel agent execution."""

    def __init__(self, worker_pools: List[WorkerPool]):
        self.worker_pools = worker_pools
        self.worker_status = {}  # worker_id -> WorkerStatus
        self.lock = threading.Lock()
        
        # Initialize worker status
        for i, pool in enumerate(worker_pools):
            worker_id = f"pool_{i}"
            self.worker_status[worker_id] = WorkerStatus(worker_id)

    def select_worker(self, task: Task) -> Optional[WorkerPool]:
        """Select the best worker pool for a given task."""
        with self.lock:
            # Filter healthy workers
            healthy_workers = [
                (worker_id, status) 
                for worker_id, status in self.worker_status.items() 
                if status.healthy
            ]
            
            if not healthy_workers:
                return None
            
            # Select based on task priority and worker load
            if task.priority in (TaskPriority.CRITICAL, TaskPriority.HIGH):
                # For high priority tasks, select the least loaded worker
                selected_worker_id = min(
                    healthy_workers, 
                    key=lambda x: x[1].current_load
                )[0]
            else:
                # For normal priority tasks, use round-robin with load awareness
                selected_worker_id = self._select_round_robin_with_load_awareness(healthy_workers)
            
            # Get the corresponding worker pool
            pool_index = int(selected_worker_id.split("_")[1])
            return self.worker_pools[pool_index]

    def update_worker_status(self, worker_id: str, load: float, healthy: bool = True):
        """Update the status of a worker."""
        with self.lock:
            if worker_id in self.worker_status:
                status = self.worker_status[worker_id]
                status.update_load(load)
                status.healthy = healthy

    def get_worker_status(self) -> Dict[str, WorkerStatus]:
        """Get the current status of all workers."""
        with self.lock:
            return self.worker_status.copy()

    def _select_round_robin_with_load_awareness(self, workers: List[Tuple[str, WorkerStatus]]) -> str:
        """Select worker using round-robin with load awareness."""
        # Simple implementation: select the worker with lowest load
        # In a more sophisticated implementation, this could track
        # the last selected worker and implement true round-robin
        return min(workers, key=lambda x: x[1].current_load)[0]

    def mark_worker_unhealthy(self, worker_id: str):
        """Mark a worker as unhealthy."""
        with self.lock:
            if worker_id in self.worker_status:
                self.worker_status[worker_id].healthy = False

    def mark_worker_healthy(self, worker_id: str):
        """Mark a worker as healthy."""
        with self.lock:
            if worker_id in self.worker_status:
                self.worker_status[worker_id].healthy = True