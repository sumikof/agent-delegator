"""
Task Queue for parallel agent processing.

This module implements a priority-based task queue that supports:
- Task prioritization
- Task dependencies
- Timeout handling
- Task cancellation
"""

import heapq
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


class TaskStatus(Enum):
    """Task status."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    TIMEOUT = auto()


@dataclass(order=True)
class PrioritizedTask:
    """Task with priority for queue ordering."""
    priority: int
    task_id: str = field(compare=False)
    task: 'Task' = field(compare=False)


@dataclass
class Task:
    """Representation of a task to be executed by agents."""
    task_id: str
    agent_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class TaskQueue:
    """Priority-based task queue for parallel agent processing."""

    def __init__(self):
        self._queue = []
        self._tasks = {}  # task_id -> Task
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._running = True

    def add_task(self, agent_type: str, payload: Dict[str, Any], 
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 timeout: Optional[float] = None,
                 dependencies: Optional[List[str]] = None) -> str:
        """Add a new task to the queue."""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            timeout=timeout,
            dependencies=dependencies or []
        )
        
        with self._lock:
            self._tasks[task_id] = task
            # Convert priority to numeric value for heapq
            priority_value = self._priority_to_value(priority)
            heapq.heappush(self._queue, PrioritizedTask(priority_value, task_id, task))
            self._condition.notify()
        
        return task_id

    def get_next_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """Get the next task from the queue."""
        with self._lock:
            if not self._running and not self._queue:
                return None
            
            if not self._queue:
                if timeout is None:
                    self._condition.wait()
                else:
                    if not self._condition.wait(timeout):
                        return None
            
            if not self._queue:
                return None
            
            prioritized_task = heapq.heappop(self._queue)
            task = self._tasks[prioritized_task.task_id]
            
            # Check if task can be executed (dependencies satisfied)
            if not self._can_execute_task(task):
                # Put it back in the queue
                heapq.heappush(self._queue, prioritized_task)
                return None
            
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            return task

    def complete_task(self, task_id: str, result: Any = None):
        """Mark a task as completed."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.time()
                self._condition.notify_all()

    def fail_task(self, task_id: str, error: str):
        """Mark a task as failed."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = error
                task.completed_at = time.time()
                self._condition.notify_all()

    def cancel_task(self, task_id: str):
        """Cancel a task."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = time.time()
                    self._condition.notify_all()
                    return True
        return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            return task.status if task else None

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.COMPLETED:
                return task.result
            return None

    def shutdown(self):
        """Shutdown the task queue."""
        with self._lock:
            self._running = False
            self._condition.notify_all()

    def _priority_to_value(self, priority: TaskPriority) -> int:
        """Convert priority enum to numeric value for heapq."""
        priority_map = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        return priority_map[priority]

    def _can_execute_task(self, task: Task) -> bool:
        """Check if a task can be executed (dependencies satisfied)."""
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            dep_task = self._tasks.get(dep_id)
            if not dep_task or dep_task.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                return False
        return True