"""Conflict Resolution and Priority Management System.

This module implements algorithms for resolving conflicts between agents
and managing task priorities in a multi-agent system.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from threading import Lock
from collections import defaultdict

from orchestrator.coordination.communication_protocol import (
    MessageType, MessagePriority, communication_protocol
)
from orchestrator.coordination.task_manager import (
    task_coordinator, TaskStatus
)


class ConflictType(str, Enum):
    """Types of conflicts that can occur."""
    RESOURCE_CONFLICT = "resource_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    TASK_CONFLICT = "task_conflict"


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving conflicts."""
    PRIORITY_BASED = "priority_based"
    TIME_BASED = "time_based"
    NEGOTIATION = "negotiation"
    ESCALATION = "escalation"


@dataclass
class Conflict:
    """Conflict information."""
    conflict_id: str
    conflict_type: ConflictType
    involved_agents: List[str]
    involved_tasks: List[str]
    resource_id: Optional[str]
    detected_at: float
    status: str
    resolution_strategy: Optional[ConflictResolutionStrategy]
    resolution_result: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type,
            "involved_agents": self.involved_agents,
            "involved_tasks": self.involved_tasks,
            "resource_id": self.resource_id,
            "detected_at": self.detected_at,
            "status": self.status,
            "resolution_strategy": self.resolution_strategy,
            "resolution_result": self.resolution_result
        }


class ConflictDetector:
    """Conflict detection system."""

    def __init__(self):
        self._lock = Lock()
        self._conflict_history: List[Conflict] = []

    def detect_conflicts(self) -> List[Conflict]:
        """Detect conflicts in the system."""
        conflicts = []
        
        # Detect resource conflicts
        resource_conflicts = self._detect_resource_conflicts()
        conflicts.extend(resource_conflicts)
        
        # Detect priority conflicts
        priority_conflicts = self._detect_priority_conflicts()
        conflicts.extend(priority_conflicts)
        
        # Detect dependency conflicts
        dependency_conflicts = self._detect_dependency_conflicts()
        conflicts.extend(dependency_conflicts)
        
        # Detect task conflicts
        task_conflicts = self._detect_task_conflicts()
        conflicts.extend(task_conflicts)
        
        # Store detected conflicts
        with self._lock:
            self._conflict_history.extend(conflicts)
        
        return conflicts

    def _detect_resource_conflicts(self) -> List[Conflict]:
        """Detect resource conflicts."""
        conflicts = []
        
        # Get all tasks that are currently in progress
        in_progress_tasks = task_coordinator.task_graph.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        
        # Group tasks by resource usage
        resource_usage = defaultdict(list)
        for task in in_progress_tasks:
            for resource in task.resource_requirements:
                resource_usage[resource].append(task)
        
        # Find resources with multiple tasks
        for resource, tasks in resource_usage.items():
            if len(tasks) > 1:
                # Multiple tasks using the same resource
                involved_agents = list(set(task.assigned_agent for task in tasks if task.assigned_agent))
                involved_tasks = [task.task_id for task in tasks]
                
                if len(involved_agents) > 1:
                    # Different agents using the same resource
                    conflict_id = f"resource_{resource}_{time.time()}"
                    
                    conflict = Conflict(
                        conflict_id=conflict_id,
                        conflict_type=ConflictType.RESOURCE_CONFLICT,
                        involved_agents=involved_agents,
                        involved_tasks=involved_tasks,
                        resource_id=resource,
                        detected_at=time.time(),
                        status="detected",
                        resolution_strategy=None,
                        resolution_result=None
                    )
                    
                    conflicts.append(conflict)
        
        return conflicts

    def _detect_priority_conflicts(self) -> List[Conflict]:
        """Detect priority conflicts."""
        conflicts = []
        
        # Get all tasks that are ready to start
        ready_tasks = task_coordinator.task_graph.get_ready_tasks()
        
        # Check if there are high priority tasks waiting while lower priority tasks are running
        in_progress_tasks = task_coordinator.task_graph.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        
        for ready_task in ready_tasks:
            if ready_task.priority in [MessagePriority.HIGH, MessagePriority.CRITICAL]:
                # Check if there are lower priority tasks running
                for in_progress_task in in_progress_tasks:
                    if (in_progress_task.priority in [MessagePriority.LOW, MessagePriority.MEDIUM] and
                        in_progress_task.assigned_agent != ready_task.assigned_agent):
                        
                        # Potential priority conflict
                        involved_agents = list(set(filter(None, [ready_task.assigned_agent, in_progress_task.assigned_agent])))
                        involved_tasks = [ready_task.task_id, in_progress_task.task_id]
                        
                        conflict_id = f"priority_{ready_task.task_id}_{in_progress_task.task_id}_{time.time()}"
                        
                        conflict = Conflict(
                            conflict_id=conflict_id,
                            conflict_type=ConflictType.PRIORITY_CONFLICT,
                            involved_agents=involved_agents,
                            involved_tasks=involved_tasks,
                            resource_id=None,
                            detected_at=time.time(),
                            status="detected",
                            resolution_strategy=None,
                            resolution_result=None
                        )
                        
                        conflicts.append(conflict)
                        break  # Only report one conflict per ready task
        
        return conflicts

    def _detect_dependency_conflicts(self) -> List[Conflict]:
        """Detect dependency conflicts (circular dependencies)."""
        conflicts = []
        
        # Check for circular dependencies
        circular_dependencies = task_coordinator.task_graph.detect_circular_dependencies()
        
        for cycle in circular_dependencies:
            if len(cycle) > 1:  # Need at least 2 tasks to form a cycle
                involved_tasks = cycle
                
                # Get agents assigned to these tasks
                involved_agents = []
                for task_id in involved_tasks:
                    task = task_coordinator.task_graph.get_task(task_id)
                    if task and task.assigned_agent:
                        involved_agents.append(task.assigned_agent)
                
                involved_agents = list(set(involved_agents))
                
                conflict_id = f"dependency_cycle_{'_'.join(cycle)}_{time.time()}"
                
                conflict = Conflict(
                    conflict_id=conflict_id,
                    conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                    involved_agents=involved_agents,
                    involved_tasks=involved_tasks,
                    resource_id=None,
                    detected_at=time.time(),
                    status="detected",
                    resolution_strategy=None,
                    resolution_result=None
                )
                
                conflicts.append(conflict)
        
        return conflicts

    def _detect_task_conflicts(self) -> List[Conflict]:
        """Detect task conflicts (tasks working on the same artifacts)."""
        conflicts = []
        
        # This is a simplified detection - in a real system, this would analyze
        # the actual artifacts being worked on by different tasks
        in_progress_tasks = task_coordinator.task_graph.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        
        # Group tasks by coordination group (tasks in same group might conflict)
        coordination_groups = defaultdict(list)
        for task in in_progress_tasks:
            if task.coordination_group:
                coordination_groups[task.coordination_group].append(task)
        
        for group_id, tasks in coordination_groups.items():
            if len(tasks) > 1:
                # Multiple tasks in the same coordination group
                involved_agents = list(set(task.assigned_agent for task in tasks if task.assigned_agent))
                involved_tasks = [task.task_id for task in tasks]
                
                if len(involved_agents) > 1:
                    # Different agents working on related tasks
                    conflict_id = f"task_coordination_{group_id}_{time.time()}"
                    
                    conflict = Conflict(
                        conflict_id=conflict_id,
                        conflict_type=ConflictType.TASK_CONFLICT,
                        involved_agents=involved_agents,
                        involved_tasks=involved_tasks,
                        resource_id=None,
                        detected_at=time.time(),
                        status="detected",
                        resolution_strategy=None,
                        resolution_result=None
                    )
                    
                    conflicts.append(conflict)
        
        return conflicts

    def get_conflict_history(self) -> List[Conflict]:
        """Get the history of detected conflicts."""
        with self._lock:
            return self._conflict_history.copy()


class ConflictResolver:
    """Conflict resolution system."""

    def __init__(self):
        self._lock = Lock()
        self._resolution_history: List[Conflict] = []

    def resolve_conflict(self, conflict: Conflict) -> Conflict:
        """Resolve a conflict using the appropriate strategy."""
        # Determine the best resolution strategy
        strategy = self._determine_resolution_strategy(conflict)
        
        # Apply the resolution strategy
        resolution_result = self._apply_resolution_strategy(conflict, strategy)
        
        # Update conflict status
        conflict.status = "resolved"
        conflict.resolution_strategy = strategy
        conflict.resolution_result = resolution_result
        
        # Store resolved conflict
        with self._lock:
            self._resolution_history.append(conflict)
        
        return conflict

    def _determine_resolution_strategy(self, conflict: Conflict) -> ConflictResolutionStrategy:
        """Determine the best resolution strategy for a conflict."""
        if conflict.conflict_type == ConflictType.RESOURCE_CONFLICT:
            return ConflictResolutionStrategy.PRIORITY_BASED
        elif conflict.conflict_type == ConflictType.PRIORITY_CONFLICT:
            return ConflictResolutionStrategy.PRIORITY_BASED
        elif conflict.conflict_type == ConflictType.DEPENDENCY_CONFLICT:
            return ConflictResolutionStrategy.NEGOTIATION
        elif conflict.conflict_type == ConflictType.TASK_CONFLICT:
            return ConflictResolutionStrategy.NEGOTIATION
        else:
            return ConflictResolutionStrategy.PRIORITY_BASED

    def _apply_resolution_strategy(self, conflict: Conflict, strategy: ConflictResolutionStrategy) -> Dict[str, Any]:
        """Apply a resolution strategy to a conflict."""
        if strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            return self._resolve_with_priority(conflict)
        elif strategy == ConflictResolutionStrategy.TIME_BASED:
            return self._resolve_with_time(conflict)
        elif strategy == ConflictResolutionStrategy.NEGOTIATION:
            return self._resolve_with_negotiation(conflict)
        elif strategy == ConflictResolutionStrategy.ESCALATION:
            return self._resolve_with_escalation(conflict)
        else:
            return {"status": "error", "message": "Unknown resolution strategy"}

    def _resolve_with_priority(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict based on task priorities."""
        resolution_actions = []
        
        # Get all tasks involved in the conflict
        tasks = []
        for task_id in conflict.involved_tasks:
            task = task_coordinator.task_graph.get_task(task_id)
            if task:
                tasks.append(task)
        
        # Sort tasks by priority (highest first)
        priority_order = {
            MessagePriority.CRITICAL: 4,
            MessagePriority.HIGH: 3,
            MessagePriority.MEDIUM: 2,
            MessagePriority.LOW: 1
        }
        
        tasks.sort(key=lambda task: -priority_order[task.priority])
        
        # Higher priority tasks get to continue, lower priority tasks get blocked
        for i, task in enumerate(tasks):
            if i == 0:
                # Highest priority task continues
                if task.status != TaskStatus.IN_PROGRESS:
                    task_coordinator.task_graph.update_task_status(task.task_id, TaskStatus.IN_PROGRESS)
                
                resolution_actions.append({
                    "task_id": task.task_id,
                    "action": "continue",
                    "reason": "highest_priority"
                })
            else:
                # Lower priority tasks get blocked
                if task.status == TaskStatus.IN_PROGRESS:
                    task_coordinator.task_graph.update_task_status(task.task_id, TaskStatus.BLOCKED)
                
                resolution_actions.append({
                    "task_id": task.task_id,
                    "action": "block",
                    "reason": "lower_priority"
                })
                
                # Notify the agent that their task is blocked
                if task.assigned_agent:
                    notification_payload = {
                        "event": "task_blocked",
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "reason": "lower_priority_conflict",
                        "conflict_id": conflict.conflict_id,
                        "higher_priority_task": tasks[0].task_id,
                        "message": f"Your task has been blocked due to priority conflict with task '{tasks[0].name}'"
                    }
                    
                    communication_protocol.send_message(
                        sender_id="conflict_resolver",
                        recipient_id=task.assigned_agent,
                        message_type=MessageType.NOTIFICATION,
                        payload=notification_payload,
                        priority=MessagePriority.HIGH
                    )
        
        return {
            "strategy": "priority_based",
            "resolution_actions": resolution_actions,
            "conflict_type": conflict.conflict_type
        }

    def _resolve_with_time(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict based on task creation time (FIFO)."""
        resolution_actions = []
        
        # Get all tasks involved in the conflict
        tasks = []
        for task_id in conflict.involved_tasks:
            task = task_coordinator.task_graph.get_task(task_id)
            if task:
                tasks.append(task)
        
        # Sort tasks by creation time (oldest first)
        tasks.sort(key=lambda task: task.created_at)
        
        # Older tasks get to continue, newer tasks get blocked
        for i, task in enumerate(tasks):
            if i == 0:
                # Oldest task continues
                if task.status != TaskStatus.IN_PROGRESS:
                    task_coordinator.task_graph.update_task_status(task.task_id, TaskStatus.IN_PROGRESS)
                
                resolution_actions.append({
                    "task_id": task.task_id,
                    "action": "continue",
                    "reason": "oldest_task"
                })
            else:
                # Newer tasks get blocked
                if task.status == TaskStatus.IN_PROGRESS:
                    task_coordinator.task_graph.update_task_status(task.task_id, TaskStatus.BLOCKED)
                
                resolution_actions.append({
                    "task_id": task.task_id,
                    "action": "block",
                    "reason": "newer_task"
                })
                
                # Notify the agent that their task is blocked
                if task.assigned_agent:
                    notification_payload = {
                        "event": "task_blocked",
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "reason": "time_based_conflict",
                        "conflict_id": conflict.conflict_id,
                        "older_task": tasks[0].task_id,
                        "message": f"Your task has been blocked due to time-based conflict with task '{tasks[0].name}'"
                    }
                    
                    communication_protocol.send_message(
                        sender_id="conflict_resolver",
                        recipient_id=task.assigned_agent,
                        message_type=MessageType.NOTIFICATION,
                        payload=notification_payload,
                        priority=MessagePriority.HIGH
                    )
        
        return {
            "strategy": "time_based",
            "resolution_actions": resolution_actions,
            "conflict_type": conflict.conflict_type
        }

    def _resolve_with_negotiation(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict through negotiation between agents."""
        resolution_actions = []
        
        # For negotiation, we send coordination requests to all involved agents
        # and let them negotiate the resolution
        for agent_id in conflict.involved_agents:
            negotiation_payload = {
                "conflict_id": conflict.conflict_id,
                "conflict_type": conflict.conflict_type,
                "involved_tasks": conflict.involved_tasks,
                "involved_agents": conflict.involved_agents,
                "resource_id": conflict.resource_id,
                "message": "Please negotiate resolution for this conflict"
            }
            
            message_id = communication_protocol.send_message(
                sender_id="conflict_resolver",
                recipient_id=agent_id,
                message_type=MessageType.COORDINATION_REQUEST,
                payload=negotiation_payload,
                priority=MessagePriority.HIGH
            )
            
            resolution_actions.append({
                "agent_id": agent_id,
                "action": "negotiation_request_sent",
                "message_id": message_id
            })
        
        return {
            "strategy": "negotiation",
            "resolution_actions": resolution_actions,
            "conflict_type": conflict.conflict_type,
            "status": "negotiation_in_progress"
        }

    def _resolve_with_escalation(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve conflict by escalating to a higher authority."""
        # In this implementation, we escalate to the orchestrator agent
        escalation_payload = {
            "conflict_id": conflict.conflict_id,
            "conflict_type": conflict.conflict_type,
            "involved_tasks": conflict.involved_tasks,
            "involved_agents": conflict.involved_agents,
            "resource_id": conflict.resource_id,
            "message": "Conflict requires escalation for resolution"
        }
        
        message_id = communication_protocol.send_message(
            sender_id="conflict_resolver",
            recipient_id="orchestrator",
            message_type=MessageType.COORDINATION_REQUEST,
            payload=escalation_payload,
            priority=MessagePriority.CRITICAL
        )
        
        return {
            "strategy": "escalation",
            "escalation_target": "orchestrator",
            "message_id": message_id,
            "conflict_type": conflict.conflict_type,
            "status": "escalated"
        }

    def get_resolution_history(self) -> List[Conflict]:
        """Get the history of resolved conflicts."""
        with self._lock:
            return self._resolution_history.copy()


class PriorityManager:
    """Priority management system."""

    def __init__(self):
        self._lock = Lock()
        self._priority_adjustments: Dict[str, MessagePriority] = {}  # task_id -> adjusted_priority

    def adjust_task_priority(self, task_id: str, new_priority: MessagePriority) -> bool:
        """Adjust the priority of a task."""
        with self._lock:
            task = task_coordinator.task_graph.get_task(task_id)
            if task:
                self._priority_adjustments[task_id] = new_priority
                return True
            return False

    def get_effective_priority(self, task_id: str) -> MessagePriority:
        """Get the effective priority of a task (original or adjusted)."""
        with self._lock:
            if task_id in self._priority_adjustments:
                return self._priority_adjustments[task_id]
            
            task = task_coordinator.task_graph.get_task(task_id)
            if task:
                return task.priority
            
            return MessagePriority.MEDIUM

    def reset_task_priority(self, task_id: str) -> bool:
        """Reset a task's priority to its original value."""
        with self._lock:
            if task_id in self._priority_adjustments:
                del self._priority_adjustments[task_id]
                return True
            return False

    def adjust_priority_based_on_dependencies(self, task_id: str) -> bool:
        """Adjust a task's priority based on its dependencies."""
        task = task_coordinator.task_graph.get_task(task_id)
        if not task:
            return False
        
        # Check if this task is blocking higher priority tasks
        dependents = []
        for dependent_id in task.dependents:
            dependent_task = task_coordinator.task_graph.get_task(dependent_id)
            if dependent_task:
                dependents.append(dependent_task)
        
        # If any dependent has higher priority, increase this task's priority
        current_priority = self.get_effective_priority(task_id)
        priority_order = {
            MessagePriority.CRITICAL: 4,
            MessagePriority.HIGH: 3,
            MessagePriority.MEDIUM: 2,
            MessagePriority.LOW: 1
        }
        
        for dependent in dependents:
            dependent_priority = self.get_effective_priority(dependent.task_id)
            if priority_order[dependent_priority] > priority_order[current_priority]:
                # Dependent has higher priority, increase this task's priority
                if current_priority == MessagePriority.LOW:
                    new_priority = MessagePriority.MEDIUM
                elif current_priority == MessagePriority.MEDIUM:
                    new_priority = MessagePriority.HIGH
                else:
                    new_priority = MessagePriority.CRITICAL
                
                return self.adjust_task_priority(task_id, new_priority)
        
        return False

    def get_priority_analysis(self) -> Dict[str, Any]:
        """Get analysis of current priority distribution."""
        priority_counts = {
            MessagePriority.CRITICAL: 0,
            MessagePriority.HIGH: 0,
            MessagePriority.MEDIUM: 0,
            MessagePriority.LOW: 0
        }
        
        all_tasks = task_coordinator.task_graph._tasks.values()
        for task in all_tasks:
            effective_priority = self.get_effective_priority(task.task_id)
            priority_counts[effective_priority] += 1
        
        return {
            "priority_distribution": priority_counts,
            "total_tasks": len(all_tasks),
            "adjusted_priorities": len(self._priority_adjustments)
        }


class ConflictResolutionSystem:
    """Complete conflict resolution system."""

    def __init__(self):
        self.conflict_detector = ConflictDetector()
        self.conflict_resolver = ConflictResolver()
        self.priority_manager = PriorityManager()
        self._lock = Lock()
        self._running = False
        self._monitor_thread = None

    def start_monitoring(self, interval: float = 5.0) -> None:
        """Start continuous conflict monitoring."""
        import threading
        
        with self._lock:
            if self._running:
                return
            
            self._running = True
            
            def _monitor_loop():
                while self._running:
                    try:
                        self.monitor_and_resolve_conflicts()
                    except Exception as e:
                        print(f"Conflict monitoring error: {e}")
                    
                    # Sleep for the interval
                    for _ in range(int(interval * 10)):  # Sleep in 0.1s increments for responsiveness
                        if not self._running:
                            break
                        time.sleep(0.1)
            
            self._monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
            self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop continuous conflict monitoring."""
        with self._lock:
            self._running = False
            if self._monitor_thread:
                self._monitor_thread.join()
                self._monitor_thread = None

    def monitor_and_resolve_conflicts(self) -> Dict[str, Any]:
        """Monitor for conflicts and resolve them."""
        start_time = time.time()
        
        # Detect conflicts
        conflicts = self.conflict_detector.detect_conflicts()
        
        # Resolve conflicts
        resolved_conflicts = []
        for conflict in conflicts:
            resolved_conflict = self.conflict_resolver.resolve_conflict(conflict)
            resolved_conflicts.append(resolved_conflict)
        
        # Adjust priorities based on conflicts
        for conflict in resolved_conflicts:
            for task_id in conflict.involved_tasks:
                self.priority_manager.adjust_priority_based_on_dependencies(task_id)
        
        execution_time = time.time() - start_time
        
        return {
            "detected_conflicts": len(conflicts),
            "resolved_conflicts": len(resolved_conflicts),
            "conflict_types": self._get_conflict_type_summary(conflicts),
            "execution_time_ms": int(execution_time * 1000),
            "timestamp": time.time()
        }

    def _get_conflict_type_summary(self, conflicts: List[Conflict]) -> Dict[str, int]:
        """Get summary of conflict types."""
        type_counts = defaultdict(int)
        for conflict in conflicts:
            type_counts[conflict.conflict_type] += 1
        return dict(type_counts)

    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the conflict resolution system."""
        # Don't use lock here to avoid deadlock - individual methods handle their own locking
        return {
            "conflict_detection": {
                "total_detected": len(self.conflict_detector.get_conflict_history()),
                "monitoring_active": self._running
            },
            "conflict_resolution": {
                "total_resolved": len(self.conflict_resolver.get_resolution_history())
            },
            "priority_management": self.priority_manager.get_priority_analysis(),
            "task_graph_metrics": task_coordinator.task_graph.get_task_graph_metrics()
        }


# Global conflict resolution system instance
conflict_resolution_system = ConflictResolutionSystem()