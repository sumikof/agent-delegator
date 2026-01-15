"""Distributed Orchestrator.

This module implements a distributed task processing framework that enables
the orchestrator to distribute work across multiple nodes and coordinate
complex workflows in a distributed environment.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

from orchestrator.agents.registry import AgentRegistry
from orchestrator.coordination.communication_protocol import (
    CommunicationProtocol, MessageType, MessagePriority
)
from orchestrator.parallel.task_queue import TaskPriority

logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    """Status of distributed nodes."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"


class TaskDistributionStrategy(str, Enum):
    """Strategies for distributing tasks across nodes."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    PRIORITY_BASED = "priority_based"
    RESOURCE_BASED = "resource_based"
    LOCATION_BASED = "location_based"


@dataclass
class DistributedNode:
    """Represents a node in the distributed system."""
    node_id: str
    hostname: str
    port: int
    status: NodeStatus
    capabilities: List[str]
    current_load: float
    max_capacity: float
    last_heartbeat: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert node information to dictionary."""
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "port": self.port,
            "status": self.status,
            "capabilities": self.capabilities,
            "current_load": self.current_load,
            "max_capacity": self.max_capacity,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata
        }

    def update_heartbeat(self) -> None:
        """Update the heartbeat timestamp."""
        self.last_heartbeat = time.time()

    def is_available(self) -> bool:
        """Check if the node is available for tasks."""
        return (
            self.status == NodeStatus.ONLINE and
            self.current_load < self.max_capacity
        )

    def can_handle_task(self, task_requirements: Dict[str, Any]) -> bool:
        """Check if this node can handle a specific task."""
        # Check if node has required capabilities
        required_capabilities = task_requirements.get("capabilities", [])
        if required_capabilities and not all(cap in self.capabilities 
                                           for cap in required_capabilities):
            return False

        # Check if node has enough capacity
        if self.current_load >= self.max_capacity:
            return False

        return True


@dataclass
class DistributedTask:
    """Represents a task in the distributed system."""
    task_id: str
    agent_type: str
    payload: Dict[str, Any]
    priority: TaskPriority
    status: str
    assigned_node: Optional[str]
    created_at: float
    updated_at: float
    dependencies: List[str]
    requirements: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert task information to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "payload": self.payload,
            "priority": self.priority,
            "status": self.status,
            "assigned_node": self.assigned_node,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "dependencies": self.dependencies,
            "requirements": self.requirements,
            "result": self.result,
            "error": self.error
        }


class DistributedTaskManager:
    """Manages distributed tasks across multiple nodes."""

    def __init__(self):
        self._tasks: Dict[str, DistributedTask] = {}
        self._task_dependencies: Dict[str, List[str]] = {}
        self._lock = threading.Lock()

    def add_task(self, agent_type: str, payload: Dict[str, Any], 
                priority: TaskPriority = TaskPriority.MEDIUM,
                dependencies: Optional[List[str]] = None,
                requirements: Optional[Dict[str, Any]] = None) -> str:
        """Add a new distributed task."""
        task_id = str(uuid.uuid4())
        
        task = DistributedTask(
            task_id=task_id,
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            status="pending",
            assigned_node=None,
            created_at=time.time(),
            updated_at=time.time(),
            dependencies=dependencies or [],
            requirements=requirements or {},
            result=None,
            error=None
        )
        
        with self._lock:
            self._tasks[task_id] = task
            
            # Track dependencies
            for dep in task.dependencies:
                if dep not in self._task_dependencies:
                    self._task_dependencies[dep] = []
                self._task_dependencies[dep].append(task_id)
        
        return task_id

    def get_task(self, task_id: str) -> Optional[DistributedTask]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def update_task_status(self, task_id: str, status: str, 
                          assigned_node: Optional[str] = None) -> bool:
        """Update the status of a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = status
                task.assigned_node = assigned_node
                task.updated_at = time.time()
                return True
            return False

    def update_task_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Update the result of a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.result = result
                task.status = "completed"
                task.updated_at = time.time()
                return True
            return False

    def update_task_error(self, task_id: str, error: str) -> bool:
        """Update the error status of a task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.error = error
                task.status = "failed"
                task.updated_at = time.time()
                return True
            return False

    def get_ready_tasks(self) -> List[DistributedTask]:
        """Get tasks that are ready to be executed."""
        with self._lock:
            ready_tasks = []
            
            for task in self._tasks.values():
                if task.status == "pending":
                    # Check if all dependencies are completed
                    all_deps_completed = all(
                        self._tasks.get(dep).status == "completed" 
                        if self._tasks.get(dep) else False
                        for dep in task.dependencies
                    )
                    
                    if all_deps_completed:
                        ready_tasks.append(task)
            
            return ready_tasks

    def get_tasks_by_status(self, status: str) -> List[DistributedTask]:
        """Get tasks by status."""
        with self._lock:
            return [task for task in self._tasks.values() if task.status == status]

    def get_tasks_for_node(self, node_id: str) -> List[DistributedTask]:
        """Get tasks assigned to a specific node."""
        with self._lock:
            return [task for task in self._tasks.values() 
                   if task.assigned_node == node_id]


class NodeRegistry:
    """Registry for managing distributed nodes."""

    def __init__(self):
        self._nodes: Dict[str, DistributedNode] = {}
        self._lock = threading.Lock()

    def register_node(self, node_id: str, hostname: str, port: int,
                     capabilities: List[str], max_capacity: float = 1.0,
                     metadata: Optional[Dict[str, Any]] = None) -> DistributedNode:
        """Register a new node."""
        node = DistributedNode(
            node_id=node_id,
            hostname=hostname,
            port=port,
            status=NodeStatus.ONLINE,
            capabilities=capabilities,
            current_load=0.0,
            max_capacity=max_capacity,
            last_heartbeat=time.time(),
            metadata=metadata or {}
        )
        
        with self._lock:
            self._nodes[node_id] = node
        
        return node

    def unregister_node(self, node_id: str) -> bool:
        """Unregister a node."""
        with self._lock:
            if node_id in self._nodes:
                del self._nodes[node_id]
                return True
            return False

    def get_node(self, node_id: str) -> Optional[DistributedNode]:
        """Get a node by ID."""
        with self._lock:
            return self._nodes.get(node_id)

    def get_available_nodes(self) -> List[DistributedNode]:
        """Get all available nodes."""
        with self._lock:
            return [node for node in self._nodes.values() if node.is_available()]

    def get_nodes_by_capability(self, capability: str) -> List[DistributedNode]:
        """Get nodes with a specific capability."""
        with self._lock:
            return [node for node in self._nodes.values() 
                   if capability in node.capabilities and node.is_available()]

    def update_node_heartbeat(self, node_id: str) -> bool:
        """Update heartbeat for a node."""
        with self._lock:
            node = self._nodes.get(node_id)
            if node:
                node.update_heartbeat()
                return True
            return False

    def update_node_load(self, node_id: str, load_change: float) -> bool:
        """Update the load for a node."""
        with self._lock:
            node = self._nodes.get(node_id)
            if node:
                node.current_load = max(0.0, min(node.max_capacity, 
                                               node.current_load + load_change))
                return True
            return False

    def get_all_nodes(self) -> List[DistributedNode]:
        """Get all registered nodes."""
        with self._lock:
            return list(self._nodes.values())


class DistributedOrchestrator:
    """Main distributed orchestrator that coordinates work across multiple nodes."""

    def __init__(self, agent_registry: AgentRegistry, 
                 communication_protocol: Optional[CommunicationProtocol] = None):
        self.agent_registry = agent_registry
        self.communication_protocol = communication_protocol or CommunicationProtocol()
        
        # Initialize components
        self.task_manager = DistributedTaskManager()
        self.node_registry = NodeRegistry()
        
        # Configuration
        self.distribution_strategy = TaskDistributionStrategy.LEAST_LOADED
        self.heartbeat_interval = 30.0  # seconds
        self.heartbeat_timeout = 60.0  # seconds
        
        # Start heartbeat monitoring
        self.heartbeat_thread = threading.Thread(
            target=self._monitor_heartbeats, daemon=True
        )
        self.running = True
        self.heartbeat_thread.start()

    def submit_task(self, agent_type: str, payload: Dict[str, Any],
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   dependencies: Optional[List[str]] = None,
                   requirements: Optional[Dict[str, Any]] = None) -> str:
        """Submit a new task to the distributed system."""
        return self.task_manager.add_task(
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            dependencies=dependencies,
            requirements=requirements
        )

    def register_node(self, node_id: str, hostname: str, port: int,
                     capabilities: List[str], max_capacity: float = 1.0,
                     metadata: Optional[Dict[str, Any]] = None) -> DistributedNode:
        """Register a new node in the distributed system."""
        return self.node_registry.register_node(
            node_id=node_id,
            hostname=hostname,
            port=port,
            capabilities=capabilities,
            max_capacity=max_capacity,
            metadata=metadata
        )

    def distribute_tasks(self) -> None:
        """Distribute ready tasks to available nodes."""
        ready_tasks = self.task_manager.get_ready_tasks()
        available_nodes = self.node_registry.get_available_nodes()
        
        if not ready_tasks or not available_nodes:
            return
        
        for task in ready_tasks:
            # Find the best node for this task
            best_node = self._select_best_node(task, available_nodes)
            
            if best_node:
                # Assign task to node
                self.task_manager.update_task_status(
                    task.task_id, "assigned", best_node.node_id
                )
                
                # Update node load
                load_increase = self._calculate_load_increase(task)
                self.node_registry.update_node_load(best_node.node_id, load_increase)
                
                # Send task to node (in a real implementation, this would be network communication)
                self._send_task_to_node(task, best_node)
                
                logger.info(f"Assigned task {task.task_id} to node {best_node.node_id}")

    def _select_best_node(self, task: DistributedTask, 
                         available_nodes: List[DistributedNode]) -> Optional[DistributedNode]:
        """Select the best node for a task based on distribution strategy."""
        if not available_nodes:
            return None
        
        # Filter nodes that can handle this task
        capable_nodes = [node for node in available_nodes 
                        if node.can_handle_task(task.requirements)]
        
        if not capable_nodes:
            return None
        
        # Apply distribution strategy
        if self.distribution_strategy == TaskDistributionStrategy.ROUND_ROBIN:
            # Simple round-robin for now
            return capable_nodes[0]
        elif self.distribution_strategy == TaskDistributionStrategy.LEAST_LOADED:
            # Select node with least load
            return min(capable_nodes, key=lambda node: node.current_load)
        elif self.distribution_strategy == TaskDistributionStrategy.PRIORITY_BASED:
            # Select based on task priority and node capabilities
            priority_nodes = [node for node in capable_nodes 
                            if "high_priority" in node.capabilities]
            return priority_nodes[0] if priority_nodes else capable_nodes[0]
        else:
            # Default: select first capable node
            return capable_nodes[0]

    def _calculate_load_increase(self, task: DistributedTask) -> float:
        """Calculate the load increase for a task."""
        # Simple calculation based on task priority
        priority_weights = {
            TaskPriority.CRITICAL: 0.4,
            TaskPriority.HIGH: 0.3,
            TaskPriority.MEDIUM: 0.2,
            TaskPriority.LOW: 0.1
        }
        
        return priority_weights.get(task.priority, 0.2)

    def _send_task_to_node(self, task: DistributedTask, node: DistributedNode) -> None:
        """Send a task to a node for execution."""
        # In a real implementation, this would send the task over the network
        # For now, we simulate it by updating the task status
        
        # Create a message to send to the node
        task_message = {
            "task_id": task.task_id,
            "agent_type": task.agent_type,
            "payload": task.payload,
            "priority": task.priority,
            "requirements": task.requirements
        }
        
        # Simulate network communication
        logger.debug(f"Sending task {task.task_id} to node {node.node_id}: {task_message}")
        
        # In a real system, this would be:
        # self.communication_protocol.send_message(
        #     sender_id="orchestrator",
        #     recipient_id=node.node_id,
        #     message_type=MessageType.REQUEST,
        #     payload={
        #         "action": "execute_task",
        #         "task": task_message
        #     },
        #     priority=MessagePriority.HIGH
        # )

    def _monitor_heartbeats(self) -> None:
        """Monitor node heartbeats and update status."""
        while self.running:
            time.sleep(self.heartbeat_interval)
            
            current_time = time.time()
            
            with self.node_registry._lock:
                for node_id, node in self.node_registry._nodes.items():
                    if (current_time - node.last_heartbeat) > self.heartbeat_timeout:
                        if node.status != NodeStatus.OFFLINE:
                            logger.warning(f"Node {node_id} heartbeat timeout, marking as offline")
                            node.status = NodeStatus.OFFLINE

    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the distributed system."""
        return {
            "nodes": {
                "total": len(self.node_registry.get_all_nodes()),
                "online": len([n for n in self.node_registry.get_all_nodes() 
                              if n.status == NodeStatus.ONLINE]),
                "offline": len([n for n in self.node_registry.get_all_nodes() 
                               if n.status == NodeStatus.OFFLINE]),
                "busy": len([n for n in self.node_registry.get_all_nodes() 
                            if n.status == NodeStatus.BUSY])
            },
            "tasks": {
                "total": len(self.task_manager._tasks),
                "pending": len(self.task_manager.get_tasks_by_status("pending")),
                "assigned": len(self.task_manager.get_tasks_by_status("assigned")),
                "completed": len(self.task_manager.get_tasks_by_status("completed")),
                "failed": len(self.task_manager.get_tasks_by_status("failed"))
            },
            "distribution_strategy": self.distribution_strategy
        }

    def shutdown(self) -> None:
        """Shutdown the distributed orchestrator."""
        self.running = False
        if self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5.0)
        
        logger.info("Distributed orchestrator shutdown complete")


# Global instance for convenience
_distributed_orchestrator = None


def get_distributed_orchestrator(agent_registry: AgentRegistry) -> DistributedOrchestrator:
    """Get or create the global distributed orchestrator instance."""
    global _distributed_orchestrator
    
    if _distributed_orchestrator is None:
        _distributed_orchestrator = DistributedOrchestrator(agent_registry)
    
    return _distributed_orchestrator