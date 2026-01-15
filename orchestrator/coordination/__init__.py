"""Multi-Agent Coordination System.

This module provides components for agent-to-agent communication,
coordinated task management, and conflict resolution.
"""

from .communication_protocol import (
    communication_protocol,
    coordination_protocol,
    MessageType,
    MessagePriority,
    AgentMessage,
    MessageQueue,
    CommunicationProtocol,
    CoordinationProtocol,
    CoordinationRequest
)

from .task_manager import (
    task_coordinator,
    TaskStatus,
    TaskDependencyType,
    TaskDependency,
    CoordinatedTask,
    TaskDependencyGraph,
    TaskCoordinator
)

from .conflict_resolver import (
    conflict_resolution_system,
    ConflictType,
    ConflictResolutionStrategy,
    Conflict,
    ConflictDetector,
    ConflictResolver,
    PriorityManager,
    ConflictResolutionSystem
)