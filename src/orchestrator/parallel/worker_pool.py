"""
Worker Pool for parallel agent execution.

This module implements a pool of worker threads that execute agent tasks
in parallel, with support for:
- Dynamic worker scaling
- Task timeout handling
- Error recovery
- Resource monitoring
"""

import threading
import time
import queue
from typing import Any, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from orchestrator.agents.loader import AgentLoader
from orchestrator.agents.registry import AgentRegistry
from orchestrator.context import ContextManager

from .task_queue import Task, TaskStatus


class WorkerPool:
    """Pool of workers for parallel agent execution."""

    def __init__(self, max_workers: int = 4, agent_registry: Optional[AgentRegistry] = None):
        self.max_workers = max_workers
        self.agent_registry = agent_registry or AgentRegistry()
        self.agent_loader = AgentLoader()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}  # task_id -> future
        self.lock = threading.Lock()
        self.running = True

    def execute_task(self, task: Task, context: ContextManager) -> str:
        """Execute a task using the worker pool."""
        if not self.running:
            raise RuntimeError("Worker pool is not running")
        
        future = self.executor.submit(self._execute_task_worker, task, context)
        
        with self.lock:
            self.active_tasks[task.task_id] = future
        
        return task.task_id

    def _execute_task_worker(self, task: Task, context: ContextManager):
        """Worker function to execute a single task."""
        try:
            # Load the appropriate agent
            agent = self.agent_loader.load_agent(task.agent_type)
            
            # Execute the agent with the task payload as context
            result = agent.run(task.payload)
            
            # Mark task as completed
            task.status = TaskStatus.COMPLETED
            task.result = result
            
        except Exception as e:
            # Mark task as failed
            task.status = TaskStatus.FAILED
            task.error = str(e)
            print(f"Agent execution failed: {e}")
            
        finally:
            # Clean up
            with self.lock:
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]

    def get_active_task_count(self) -> int:
        """Get the number of currently active tasks."""
        with self.lock:
            return len(self.active_tasks)

    def shutdown(self, wait: bool = True):
        """Shutdown the worker pool."""
        self.running = False
        self.executor.shutdown(wait=wait)

    def scale_workers(self, new_size: int):
        """Scale the number of workers in the pool."""
        if new_size <= 0:
            raise ValueError("Worker pool size must be positive")
        
        # Create a new executor with the desired size
        new_executor = ThreadPoolExecutor(max_workers=new_size)
        
        # Wait for current tasks to complete
        self.executor.shutdown(wait=True)
        
        # Replace the executor
        self.executor = new_executor
        self.max_workers = new_size

    def get_worker_utilization(self) -> float:
        """Get current worker utilization (0.0 to 1.0)."""
        active = self.get_active_task_count()
        return min(active / self.max_workers, 1.0) if self.max_workers > 0 else 0.0