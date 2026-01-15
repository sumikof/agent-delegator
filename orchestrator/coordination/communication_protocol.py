"""Agent Communication Protocol.

This module implements a communication protocol for direct agent-to-agent communication,
enabling multi-agent coordination and collaboration.
"""

from __future__ import annotations

import json
import uuid
import time
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from threading import Lock


class MessageType(str, Enum):
    """Message types for agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentMessage:
    """Message structure for agent communication."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: MessagePriority
    timestamp: float
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentMessage:
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data["priority"]),
            timestamp=data["timestamp"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to")
        )


class MessageQueue:
    """Thread-safe message queue for agent communication."""

    def __init__(self):
        self._queue: List[AgentMessage] = []
        self._lock = Lock()
        self._message_store: Dict[str, AgentMessage] = {}

    def enqueue(self, message: AgentMessage) -> None:
        """Add a message to the queue."""
        with self._lock:
            self._queue.append(message)
            self._message_store[message.message_id] = message

    def dequeue(self, recipient_id: str) -> Optional[AgentMessage]:
        """Get the next message for a specific recipient."""
        with self._lock:
            # Find the highest priority message for this recipient
            recipient_messages = [msg for msg in self._queue if msg.recipient_id == recipient_id]
            
            if not recipient_messages:
                return None
            
            # Sort by priority (critical > high > medium > low)
            priority_order = {
                MessagePriority.CRITICAL: 4,
                MessagePriority.HIGH: 3,
                MessagePriority.MEDIUM: 2,
                MessagePriority.LOW: 1
            }
            
            # Sort by priority, then by timestamp (older first)
            recipient_messages.sort(key=lambda msg: (-priority_order[msg.priority], msg.timestamp))
            
            # Remove from queue and return
            message = recipient_messages[0]
            self._queue.remove(message)
            return message

    def get_message(self, message_id: str) -> Optional[AgentMessage]:
        """Get a specific message by ID."""
        with self._lock:
            return self._message_store.get(message_id)

    def has_messages(self, recipient_id: str) -> bool:
        """Check if there are messages for a specific recipient."""
        with self._lock:
            return any(msg.recipient_id == recipient_id for msg in self._queue)

    def get_queue_size(self) -> int:
        """Get the total number of messages in the queue."""
        with self._lock:
            return len(self._queue)


class CommunicationProtocol:
    """Agent communication protocol implementation."""

    def __init__(self):
        self.message_queue = MessageQueue()
        self._message_history: List[AgentMessage] = []
        self._pending_requests: Dict[str, AgentMessage] = {}
        self._lock = Lock()

    def send_message(self, sender_id: str, recipient_id: str, 
                    message_type: MessageType, payload: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.MEDIUM,
                    correlation_id: Optional[str] = None,
                    reply_to: Optional[str] = None) -> str:
        """Send a message from one agent to another."""
        message_id = str(uuid.uuid4())
        timestamp = time.time()
        
        message = AgentMessage(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            timestamp=timestamp,
            payload=payload,
            correlation_id=correlation_id,
            reply_to=reply_to
        )
        
        with self._lock:
            self.message_queue.enqueue(message)
            self._message_history.append(message)
            
            # If this is a request, track it
            if message_type == MessageType.REQUEST:
                self._pending_requests[message_id] = message
        
        return message_id

    def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """Receive a message for a specific agent."""
        start_time = time.time()
        
        while True:
            if self.message_queue.has_messages(agent_id):
                message = self.message_queue.dequeue(agent_id)
                return message
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return None
            
            # Small sleep to prevent busy waiting
            time.sleep(0.01)

    def send_response(self, original_message: AgentMessage, response_payload: Dict[str, Any]) -> str:
        """Send a response to a received message."""
        return self.send_message(
            sender_id=original_message.recipient_id,
            recipient_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=response_payload,
            priority=original_message.priority,
            correlation_id=original_message.message_id,
            reply_to=original_message.message_id
        )

    def send_error(self, original_message: AgentMessage, error_message: str, error_details: Dict[str, Any]) -> str:
        """Send an error response to a received message."""
        error_payload = {
            "error": error_message,
            "details": error_details,
            "original_message_id": original_message.message_id,
            "original_payload": original_message.payload
        }
        
        return self.send_message(
            sender_id=original_message.recipient_id,
            recipient_id=original_message.sender_id,
            message_type=MessageType.ERROR,
            payload=error_payload,
            priority=MessagePriority.HIGH,
            correlation_id=original_message.message_id,
            reply_to=original_message.message_id
        )

    def get_message_history(self, agent_id: Optional[str] = None) -> List[AgentMessage]:
        """Get message history for an agent or all agents."""
        with self._lock:
            if agent_id:
                return [msg for msg in self._message_history 
                       if msg.sender_id == agent_id or msg.recipient_id == agent_id]
            return self._message_history.copy()

    def get_pending_requests(self, agent_id: str) -> List[AgentMessage]:
        """Get pending requests for an agent."""
        with self._lock:
            return [msg for msg in self._pending_requests.values() 
                   if msg.recipient_id == agent_id]

    def clear_pending_request(self, message_id: str) -> None:
        """Clear a pending request from tracking."""
        with self._lock:
            self._pending_requests.pop(message_id, None)

    def get_queue_metrics(self) -> Dict[str, Any]:
        """Get metrics about the message queue."""
        with self._lock:
            return {
                "total_messages": self.message_queue.get_queue_size(),
                "pending_requests": len(self._pending_requests),
                "total_messages_processed": len(self._message_history)
            }


class CoordinationRequest:
    """Specialized coordination request message."""

    def __init__(self, request_type: str, resource_id: str, 
                 requesting_agent: str, priority: MessagePriority = MessagePriority.MEDIUM):
        self.request_type = request_type
        self.resource_id = resource_id
        self.requesting_agent = requesting_agent
        self.priority = priority
        self.timestamp = time.time()
        self.status = "pending"
        self.response: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert coordination request to dictionary."""
        return {
            "request_type": self.request_type,
            "resource_id": self.resource_id,
            "requesting_agent": self.requesting_agent,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "status": self.status,
            "response": self.response
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CoordinationRequest:
        """Create coordination request from dictionary."""
        request = cls(
            request_type=data["request_type"],
            resource_id=data["resource_id"],
            requesting_agent=data["requesting_agent"],
            priority=MessagePriority(data["priority"])
        )
        request.timestamp = data["timestamp"]
        request.status = data["status"]
        request.response = data.get("response")
        return request


class CoordinationProtocol:
    """Specialized protocol for agent coordination."""

    def __init__(self, communication_protocol: CommunicationProtocol):
        self.communication_protocol = communication_protocol
        self._resource_lock: Dict[str, str] = {}  # resource_id -> agent_id
        self._lock = Lock()

    def request_resource_access(self, requesting_agent: str, resource_id: str, 
                               access_type: str, priority: MessagePriority = MessagePriority.MEDIUM) -> Tuple[bool, Optional[str]]:
        """Request access to a shared resource."""
        with self._lock:
            # Check if resource is already locked
            if resource_id in self._resource_lock:
                current_owner = self._resource_lock[resource_id]
                
                # If the current owner is the same agent, grant access
                if current_owner == requesting_agent:
                    return True, None
                
                # If different agent owns the resource, send coordination request
                coordination_payload = {
                    "request_type": "resource_access",
                    "resource_id": resource_id,
                    "access_type": access_type,
                    "requesting_agent": requesting_agent,
                    "priority": priority
                }
                
                message_id = self.communication_protocol.send_message(
                    sender_id=requesting_agent,
                    recipient_id=current_owner,
                    message_type=MessageType.COORDINATION_REQUEST,
                    payload=coordination_payload,
                    priority=priority
                )
                
                return False, message_id
            else:
                # Resource is available, grant access
                self._resource_lock[resource_id] = requesting_agent
                return True, None

    def release_resource(self, agent_id: str, resource_id: str) -> None:
        """Release a previously acquired resource."""
        with self._lock:
            if resource_id in self._resource_lock and self._resource_lock[resource_id] == agent_id:
                del self._resource_lock[resource_id]

    def handle_coordination_request(self, message: AgentMessage) -> AgentMessage:
        """Handle an incoming coordination request."""
        payload = message.payload
        request_type = payload.get("request_type")
        resource_id = payload.get("resource_id")
        requesting_agent = payload.get("requesting_agent")
        
        if request_type == "resource_access":
            # Check if we can release the resource
            if resource_id in self._resource_lock and self._resource_lock[resource_id] == message.recipient_id:
                # Decide whether to grant access based on priority
                current_priority = self._get_current_resource_priority(resource_id)
                requested_priority = MessagePriority(payload.get("priority", "medium"))
                
                if self._should_grant_access(current_priority, requested_priority):
                    # Release resource and grant access
                    self.release_resource(message.recipient_id, resource_id)
                    
                    response_payload = {
                        "status": "granted",
                        "resource_id": resource_id,
                        "message": "Resource access granted"
                    }
                    
                    return self.communication_protocol.send_response(message, response_payload)
                else:
                    # Deny access
                    response_payload = {
                        "status": "denied",
                        "resource_id": resource_id,
                        "message": "Resource access denied due to priority",
                        "current_priority": current_priority,
                        "requested_priority": requested_priority
                    }
                    
                    return self.communication_protocol.send_response(message, response_payload)
            else:
                # Resource not owned by this agent
                error_payload = {
                    "error": "Resource not owned by this agent",
                    "resource_id": resource_id
                }
                return self.communication_protocol.send_error(message, "Resource not owned", error_payload)
        
        # Unknown request type
        error_payload = {
            "error": "Unknown coordination request type",
            "request_type": request_type
        }
        return self.communication_protocol.send_error(message, "Unknown request type", error_payload)

    def _get_current_resource_priority(self, resource_id: str) -> MessagePriority:
        """Get the current priority of a resource (simplified for this example)."""
        # In a real implementation, this would track the priority of the current owner
        return MessagePriority.MEDIUM

    def _should_grant_access(self, current_priority: MessagePriority, requested_priority: MessagePriority) -> bool:
        """Determine if access should be granted based on priorities."""
        priority_order = {
            MessagePriority.CRITICAL: 4,
            MessagePriority.HIGH: 3,
            MessagePriority.MEDIUM: 2,
            MessagePriority.LOW: 1
        }
        
        return priority_order[requested_priority] > priority_order[current_priority]


# Global communication protocol instance
communication_protocol = CommunicationProtocol()
coordination_protocol = CoordinationProtocol(communication_protocol)