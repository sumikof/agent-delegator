"""
Parallel Processing Orchestrator.

This module integrates all parallel processing components to provide
a high-level interface for parallel agent execution.
"""

import threading
import time
from typing import Any, Dict, List, Optional

from orchestrator.context import ContextManager
from orchestrator.agents.registry import AgentRegistry, registry

from .task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from .worker_pool import WorkerPool
from .load_balancer import LoadBalancer
from .monitor import ResourceMonitor


class ParallelOrchestrator:
    """High-level orchestrator for parallel agent execution."""

    def __init__(self, max_workers: int = 4, agent_registry: Optional[AgentRegistry] = None):
        self.agent_registry = agent_registry or registry
        
        # Create worker pools (for now, just one pool)
        self.worker_pools = [WorkerPool(max_workers, self.agent_registry)]
        
        # Create load balancer
        self.load_balancer = LoadBalancer(self.worker_pools)
        
        # Create task queue
        self.task_queue = TaskQueue()
        
        # Create resource monitor
        self.resource_monitor = ResourceMonitor()
        
        # Start monitoring
        self.resource_monitor.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.running = True
        self.processing_thread.start()

    def submit_task(self, agent_type: str, payload: Dict[str, Any],
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   timeout: Optional[float] = None,
                   dependencies: Optional[List[str]] = None) -> str:
        """Submit a new task for parallel execution."""
        task_id = self.task_queue.add_task(
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            timeout=timeout,
            dependencies=dependencies
        )
        return task_id

    def submit_batch(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Submit a batch of tasks."""
        task_ids = []
        for task in tasks:
            task_id = self.submit_task(
                agent_type=task['agent_type'],
                payload=task['payload'],
                priority=getattr(TaskPriority, task.get('priority', 'MEDIUM')),
                timeout=task.get('timeout'),
                dependencies=task.get('dependencies')
            )
            task_ids.append(task_id)
        return task_ids

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task."""
        status = self.task_queue.get_task_status(task_id)
        return status.name if status else None

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        return self.task_queue.get_task_result(task_id)

    def wait_for_completion(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a task to complete."""
        start_time = time.time()
        while True:
            status = self.task_queue.get_task_status(task_id)
            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
                return True
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        return self.task_queue.cancel_task(task_id)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        metrics = self.resource_monitor.get_current_system_metrics()
        if metrics:
            return {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'memory_total': metrics.memory_total,
                'disk_usage': metrics.disk_usage,
                'timestamp': metrics.timestamp
            }
        return {}

    def get_worker_status(self) -> Dict[str, Any]:
        """Get the status of worker pools."""
        status = {}
        for i, pool in enumerate(self.worker_pools):
            status[f"pool_{i}"] = {
                'active_tasks': pool.get_active_task_count(),
                'max_workers': pool.max_workers,
                'utilization': pool.get_worker_utilization()
            }
        return status

    def scale_workers(self, pool_index: int = 0, new_size: int = 4):
        """Scale the number of workers in a pool."""
        if 0 <= pool_index < len(self.worker_pools):
            self.worker_pools[pool_index].scale_workers(new_size)

    def shutdown(self):
        """Shutdown the parallel orchestrator."""
        self.running = False
        
        # Shutdown components
        self.resource_monitor.stop()
        
        for pool in self.worker_pools:
            pool.shutdown()
        
        self.task_queue.shutdown()
        
        # Wait for processing thread to finish
        if self.processing_thread:
            self.processing_thread.join()

    def _process_tasks(self):
        """Main task processing loop."""
        while self.running:
            try:
                # Get next task from queue
                task = self.task_queue.get_next_task(timeout=1.0)
                
                if task:
                    # Select worker pool using load balancer
                    worker_pool = self.load_balancer.select_worker(task)
                    
                    if worker_pool:
                        # Create execution context
                        context = ContextManager()
                        
                        # Execute task
                        worker_pool.execute_task(task, context)
                        
                        # Record task metrics
                        self.resource_monitor.record_task_metrics(task)
                        
                        # Update worker status
                        worker_id = f"pool_{self.worker_pools.index(worker_pool)}"
                        utilization = worker_pool.get_worker_utilization()
                        self.load_balancer.update_worker_status(worker_id, utilization)
                    else:
                        # No available workers, put task back in queue
                        self.task_queue.add_task(
                            agent_type=task.agent_type,
                            payload=task.payload,
                            priority=task.priority,
                            timeout=task.timeout,
                            dependencies=task.dependencies
                        )
                        time.sleep(0.1)
                
            except Exception as e:
                print(f"Task processing error: {e}")
                time.sleep(1.0)