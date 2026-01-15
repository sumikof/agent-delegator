"""Coordinated Task Management System.

This module implements a task management system that enables multiple agents
to coordinate their work on related tasks.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from threading import Lock
from collections import defaultdict

from orchestrator.coordination.communication_protocol import (
    MessageType, MessagePriority, communication_protocol
)


class TaskStatus(str, Enum):
    """Task status for coordinated tasks."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskDependencyType(str, Enum):
    """Types of task dependencies."""
    HARD = "hard"  # Must be completed before this task can start
    SOFT = "soft"  # Should be completed before this task starts (but not required)
    COORDINATED = "coordinated"  # Tasks should be coordinated with each other


@dataclass
class TaskDependency:
    """Task dependency information."""
    task_id: str
    dependency_type: TaskDependencyType
    description: str


@dataclass
class CoordinatedTask:
    """Coordinated task information."""
    task_id: str
    name: str
    description: str
    status: TaskStatus
    assigned_agent: Optional[str]
    created_at: float
    updated_at: float
    priority: MessagePriority
    payload: Dict[str, Any]
    dependencies: List[TaskDependency]
    dependents: List[str]
    coordination_group: Optional[str]
    resource_requirements: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "priority": self.priority,
            "payload": self.payload,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "dependents": self.dependents,
            "coordination_group": self.coordination_group,
            "resource_requirements": self.resource_requirements,
            "metadata": self.metadata
        }

    def add_dependency(self, dependency: TaskDependency) -> None:
        """Add a dependency to this task."""
        self.dependencies.append(dependency)

    def add_dependent(self, task_id: str) -> None:
        """Add a dependent task."""
        if task_id not in self.dependents:
            self.dependents.append(task_id)

    def can_start(self, task_states: Dict[str, TaskStatus]) -> bool:
        """Check if this task can start based on its dependencies."""
        for dep in self.dependencies:
            if dep.dependency_type == TaskDependencyType.HARD:
                dep_status = task_states.get(dep.task_id)
                if dep_status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                    return False
        return True

    def is_blocked(self) -> bool:
        """Check if this task is blocked."""
        return self.status == TaskStatus.BLOCKED


class TaskDependencyGraph:
    """Task dependency graph for coordinated task management."""

    def __init__(self):
        self._tasks: Dict[str, CoordinatedTask] = {}
        self._lock = Lock()
        self._coordination_groups: Dict[str, List[str]] = defaultdict(list)
        self._resource_usage: Dict[str, List[str]] = defaultdict(list)

    def add_task(self, task: CoordinatedTask) -> None:
        """Add a task to the dependency graph."""
        with self._lock:
            self._tasks[task.task_id] = task
            
            # Add to coordination group if specified
            if task.coordination_group:
                self._coordination_groups[task.coordination_group].append(task.task_id)
            
            # Track resource usage
            for resource in task.resource_requirements:
                self._resource_usage[resource].append(task.task_id)

    def get_task(self, task_id: str) -> Optional[CoordinatedTask]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        """Update the status of a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = new_status
                task.updated_at = time.time()
                return True
            return False

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to an agent."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.ASSIGNED
                task.assigned_agent = agent_id
                task.updated_at = time.time()
                return True
            return False

    def start_task(self, task_id: str) -> bool:
        """Start a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.ASSIGNED:
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = time.time()
                return True
            return False

    def complete_task(self, task_id: str) -> bool:
        """Complete a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.COMPLETED
                task.updated_at = time.time()
                
                # Notify dependents that they can now start
                self._notify_dependents(task_id)
                return True
            return False

    def fail_task(self, task_id: str) -> bool:
        """Fail a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                task.status = TaskStatus.FAILED
                task.updated_at = time.time()
                return True
            return False

    def get_tasks_by_status(self, status: TaskStatus) -> List[CoordinatedTask]:
        """Get all tasks with a specific status."""
        with self._lock:
            return [task for task in self._tasks.values() if task.status == status]

    def get_tasks_for_agent(self, agent_id: str) -> List[CoordinatedTask]:
        """Get all tasks assigned to a specific agent."""
        with self._lock:
            return [task for task in self._tasks.values() if task.assigned_agent == agent_id]

    def get_ready_tasks(self) -> List[CoordinatedTask]:
        """Get all tasks that are ready to be assigned."""
        with self._lock:
            ready_tasks = []
            task_states = {task_id: task.status for task_id, task in self._tasks.items()}
            
            for task in self._tasks.values():
                if (task.status == TaskStatus.PENDING and 
                    task.can_start(task_states)):
                    ready_tasks.append(task)
            
            return ready_tasks

    def get_coordination_group(self, group_id: str) -> List[CoordinatedTask]:
        """Get all tasks in a coordination group."""
        with self._lock:
            task_ids = self._coordination_groups.get(group_id, [])
            return [self._tasks[task_id] for task_id in task_ids if task_id in self._tasks]

    def get_tasks_using_resource(self, resource_id: str) -> List[CoordinatedTask]:
        """Get all tasks that require a specific resource."""
        with self._lock:
            task_ids = self._resource_usage.get(resource_id, [])
            return [self._tasks[task_id] for task_id in task_ids if task_id in self._tasks]

    def _notify_dependents(self, completed_task_id: str) -> None:
        """Notify dependent tasks that their dependency has been completed."""
        completed_task = self._tasks.get(completed_task_id)
        if not completed_task:
            return

        for dependent_id in completed_task.dependents:
            dependent_task = self._tasks.get(dependent_id)
            if dependent_task:
                # Send notification to the assigned agent (if any)
                if dependent_task.assigned_agent:
                    notification_payload = {
                        "event": "dependency_completed",
                        "completed_task_id": completed_task_id,
                        "dependent_task_id": dependent_id,
                        "message": f"Dependency '{completed_task.name}' has been completed"
                    }
                    
                    communication_protocol.send_message(
                        sender_id="task_manager",
                        recipient_id=dependent_task.assigned_agent,
                        message_type=MessageType.NOTIFICATION,
                        payload=notification_payload,
                        priority=MessagePriority.MEDIUM
                    )

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the task graph."""
        with self._lock:
            visited = set()
            recursion_stack = set()
            cycles = []
            
            def _dfs(task_id: str, path: List[str]) -> bool:
                if task_id in recursion_stack:
                    # Found a cycle
                    cycle_start = path.index(task_id)
                    cycle = path[cycle_start:]
                    cycles.append(cycle)
                    return True
                
                if task_id in visited:
                    return False
                
                visited.add(task_id)
                recursion_stack.add(task_id)
                path.append(task_id)
                
                task = self._tasks.get(task_id)
                if task:
                    for dep in task.dependencies:
                        if dep.task_id in self._tasks:
                            _dfs(dep.task_id, path.copy())
                
                recursion_stack.remove(task_id)
                return False
            
            for task_id in self._tasks:
                _dfs(task_id, [])
            
            return cycles

    def get_task_graph_metrics(self) -> Dict[str, Any]:
        """Get metrics about the task dependency graph."""
        with self._lock:
            total_tasks = len(self._tasks)
            pending_tasks = len(self.get_tasks_by_status(TaskStatus.PENDING))
            in_progress_tasks = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
            completed_tasks = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
            failed_tasks = len(self.get_tasks_by_status(TaskStatus.FAILED))
            
            coordination_groups = len(self._coordination_groups)
            total_dependencies = sum(len(task.dependencies) for task in self._tasks.values())
            
            return {
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "coordination_groups": coordination_groups,
                "total_dependencies": total_dependencies,
                "average_dependencies_per_task": total_dependencies / total_tasks if total_tasks > 0 else 0
            }


class TaskCoordinator:
    """Task coordinator for managing coordinated tasks."""

    def __init__(self):
        self.task_graph = TaskDependencyGraph()
        self._lock = Lock()

    def create_task(self, name: str, description: str, payload: Dict[str, Any],
                   priority: MessagePriority = MessagePriority.MEDIUM,
                   coordination_group: Optional[str] = None,
                   resource_requirements: Optional[List[str]] = None) -> str:
        """Create a new coordinated task."""
        task_id = str(uuid.uuid4())
        
        task = CoordinatedTask(
            task_id=task_id,
            name=name,
            description=description,
            status=TaskStatus.PENDING,
            assigned_agent=None,
            created_at=time.time(),
            updated_at=time.time(),
            priority=priority,
            payload=payload,
            dependencies=[],
            dependents=[],
            coordination_group=coordination_group,
            resource_requirements=resource_requirements or [],
            metadata={}
        )
        
        self.task_graph.add_task(task)
        return task_id

    def add_dependency(self, task_id: str, dependency_task_id: str,
                      dependency_type: TaskDependencyType = TaskDependencyType.HARD,
                      description: str = "") -> bool:
        """Add a dependency between tasks."""
        with self._lock:
            task = self.task_graph.get_task(task_id)
            dependency_task = self.task_graph.get_task(dependency_task_id)
            
            if task and dependency_task:
                dependency = TaskDependency(
                    task_id=dependency_task_id,
                    dependency_type=dependency_type,
                    description=description
                )
                
                task.add_dependency(dependency)
                dependency_task.add_dependent(task_id)
                return True
            
            return False

    def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to a specific agent."""
        return self.task_graph.assign_task(task_id, agent_id)

    def start_task_execution(self, task_id: str) -> bool:
        """Start execution of a task."""
        return self.task_graph.start_task(task_id)

    def complete_task_execution(self, task_id: str) -> bool:
        """Complete execution of a task."""
        return self.task_graph.complete_task(task_id)

    def get_next_available_task(self, agent_id: str) -> Optional[CoordinatedTask]:
        """Get the next available task for an agent."""
        with self._lock:
            # Get ready tasks
            ready_tasks = self.task_graph.get_ready_tasks()
            
            # Filter by agent capabilities and resource availability
            available_tasks = []
            for task in ready_tasks:
                if self._can_agent_execute_task(agent_id, task):
                    available_tasks.append(task)
            
            # Sort by priority and creation time
            available_tasks.sort(key=lambda task: (
                -self._priority_to_value(task.priority), 
                task.created_at
            ))
            
            return available_tasks[0] if available_tasks else None

    def _can_agent_execute_task(self, agent_id: str, task: CoordinatedTask) -> bool:
        """Check if an agent can execute a specific task."""
        # Check if the agent already has too many tasks
        agent_tasks = self.task_graph.get_tasks_for_agent(agent_id)
        in_progress_count = sum(1 for t in agent_tasks if t.status == TaskStatus.IN_PROGRESS)
        
        # Limit to 3 in-progress tasks per agent
        if in_progress_count >= 3:
            return False
        
        # Check resource availability
        for resource in task.resource_requirements:
            resource_tasks = self.task_graph.get_tasks_using_resource(resource)
            
            # Check if any other task is currently using this resource
            for rt in resource_tasks:
                if (rt.status == TaskStatus.IN_PROGRESS and 
                    rt.task_id != task.task_id and
                    rt.assigned_agent != agent_id):
                    # Resource is being used by another agent
                    return False
        
        return True

    def _priority_to_value(self, priority: MessagePriority) -> int:
        """Convert priority to numerical value for sorting."""
        priority_values = {
            MessagePriority.CRITICAL: 4,
            MessagePriority.HIGH: 3,
            MessagePriority.MEDIUM: 2,
            MessagePriority.LOW: 1
        }
        return priority_values.get(priority, 2)

    def coordinate_related_tasks(self, task_id: str) -> List[str]:
        """Coordinate tasks that are related to the given task."""
        with self._lock:
            task = self.task_graph.get_task(task_id)
            if not task:
                return []
            
            # Find all tasks in the same coordination group
            if task.coordination_group:
                group_tasks = self.task_graph.get_coordination_group(task.coordination_group)
                
                # Notify all agents in the group about the coordination
                coordinated_task_ids = []
                for group_task in group_tasks:
                    if group_task.task_id != task_id and group_task.assigned_agent:
                        coordination_payload = {
                            "coordination_type": "group_coordination",
                            "coordination_group": task.coordination_group,
                            "triggering_task_id": task_id,
                            "triggering_task_name": task.name,
                            "related_task_id": group_task.task_id,
                            "related_task_name": group_task.name,
                            "message": f"Task '{task.name}' has been updated, please coordinate your work"
                        }
                        
                        communication_protocol.send_message(
                            sender_id="task_coordinator",
                            recipient_id=group_task.assigned_agent,
                            message_type=MessageType.NOTIFICATION,
                            payload=coordination_payload,
                            priority=MessagePriority.MEDIUM
                        )
                        
                        coordinated_task_ids.append(group_task.task_id)
                
                return coordinated_task_ids
            
            return []

    def resolve_task_conflicts(self, task_id: str) -> Dict[str, Any]:
        """Resolve conflicts for a task."""
        with self._lock:
            task = self.task_graph.get_task(task_id)
            if not task:
                return {"status": "error", "message": "Task not found"}
            
            # Check for resource conflicts
            resource_conflicts = []
            for resource in task.resource_requirements:
                resource_tasks = self.task_graph.get_tasks_using_resource(resource)
                
                for rt in resource_tasks:
                    if (rt.task_id != task_id and 
                        rt.status == TaskStatus.IN_PROGRESS and
                        rt.assigned_agent != task.assigned_agent):
                        
                        resource_conflicts.append({
                            "resource_id": resource,
                            "conflicting_task_id": rt.task_id,
                            "conflicting_agent": rt.assigned_agent,
                            "conflicting_task_name": rt.name
                        })
            
            if resource_conflicts:
                # Try to resolve conflicts by priority
                resolution_results = []
                for conflict in resource_conflicts:
                    conflicting_task = self.task_graph.get_task(conflict["conflicting_task_id"])
                    if conflicting_task:
                        # Compare priorities
                        if self._priority_to_value(task.priority) > self._priority_to_value(conflicting_task.priority):
                            # This task has higher priority, request the other agent to yield
                            resolution_payload = {
                                "conflict_type": "resource_conflict",
                                "resource_id": conflict["resource_id"],
                                "requesting_task_id": task_id,
                                "requesting_task_name": task.name,
                                "requesting_task_priority": task.priority,
                                "conflicting_task_id": conflicting_task.task_id,
                                "conflicting_task_name": conflicting_task.name,
                                "conflicting_task_priority": conflicting_task.priority,
                                "message": f"Higher priority task '{task.name}' requests access to resource '{conflict['resource_id']}'"
                            }
                            
                            communication_protocol.send_message(
                                sender_id="task_coordinator",
                                recipient_id=conflicting_task.assigned_agent,
                                message_type=MessageType.COORDINATION_REQUEST,
                                payload=resolution_payload,
                                priority=MessagePriority.HIGH
                            )
                            
                            resolution_results.append({
                                "resource_id": conflict["resource_id"],
                                "status": "resolution_requested",
                                "action": "sent_coordination_request"
                            })
                        else:
                            # Other task has higher or equal priority, this task should wait
                            resolution_results.append({
                                "resource_id": conflict["resource_id"],
                                "status": "wait_required",
                                "action": "task_should_wait"
                            })
            
            return {
                "status": "conflicts_resolved" if resource_conflicts else "no_conflicts",
                "resource_conflicts": resource_conflicts,
                "resolution_results": resolution_results,
                "task_id": task_id
            }

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get the current coordination status."""
        # Don't use lock here to avoid deadlock - the individual methods handle their own locking
        return {
            "task_graph_metrics": self.task_graph.get_task_graph_metrics(),
            "communication_metrics": communication_protocol.get_queue_metrics(),
            "coordination_groups": list(self.task_graph._coordination_groups.keys())
        }


# Global task coordinator instance
task_coordinator = TaskCoordinator()