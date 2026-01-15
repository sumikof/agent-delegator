"""Notifier base class and notification types.

This module defines the core notification system with different notification
types and priority levels for the orchestrator's feedback loop workflow.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import time
import uuid


class NotificationType(str, Enum):
    """Types of notifications supported by the system."""
    STATUS_CHANGE = "status_change"  # Task status changed
    FEEDBACK_REQUEST = "feedback_request"  # Feedback requested on a task
    APPROVAL_COMPLETED = "approval_completed"  # Task approved and completed
    FIX_REQUEST = "fix_request"  # Fix requested on a task
    ERROR = "error"  # Error occurred
    WARNING = "warning"  # Warning notification
    INFO = "info"  # Informational notification


class NotificationPriority(int, Enum):
    """Priority levels for notifications."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Notification:
    """Representation of a notification."""
    notification_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    context: Dict[str, Any]
    created_at: float
    read: bool = False
    read_at: Optional[float] = None
    
    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.read = True
        self.read_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            "notification_id": self.notification_id,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "title": self.title,
            "message": self.message,
            "context": self.context,
            "created_at": self.created_at,
            "read": self.read,
            "read_at": self.read_at
        }


class Notifier:
    """Base notifier class for sending notifications."""
    
    def __init__(self, name: str = "default"):
        self.name = name
    
    def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM
    ) -> Notification:
        """Send a notification."""
        notification_id = str(uuid.uuid4())
        context = context or {}
        
        notification = Notification(
            notification_id=notification_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            context=context,
            created_at=time.time()
        )
        
        self._deliver_notification(notification)
        return notification
    
    def _deliver_notification(self, notification: Notification) -> None:
        """Deliver notification (to be implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement _deliver_notification")
    
    def send_status_change_notification(
        self,
        task_id: str,
        old_status: str,
        new_status: str,
        reason: str = ""
    ) -> Notification:
        """Send a status change notification."""
        return self.send_notification(
            notification_type=NotificationType.STATUS_CHANGE,
            title=f"Task Status Changed: {task_id}",
            message=f"Task {task_id} status changed from {old_status} to {new_status}",
            context={
                "task_id": task_id,
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason
            },
            priority=NotificationPriority.MEDIUM
        )
    
    def send_feedback_request_notification(
        self,
        task_id: str,
        feedback_details: Dict[str, Any]
    ) -> Notification:
        """Send a feedback request notification."""
        return self.send_notification(
            notification_type=NotificationType.FEEDBACK_REQUEST,
            title=f"Feedback Requested: {task_id}",
            message=f"Feedback requested for task {task_id}",
            context={
                "task_id": task_id,
                "feedback_details": feedback_details
            },
            priority=NotificationPriority.HIGH
        )
    
    def send_approval_completed_notification(
        self,
        task_id: str,
        approval_details: Dict[str, Any]
    ) -> Notification:
        """Send an approval completed notification."""
        return self.send_notification(
            notification_type=NotificationType.APPROVAL_COMPLETED,
            title=f"Task Approved: {task_id}",
            message=f"Task {task_id} has been approved and completed",
            context={
                "task_id": task_id,
                "approval_details": approval_details
            },
            priority=NotificationPriority.MEDIUM
        )
    
    def send_fix_request_notification(
        self,
        task_id: str,
        fix_details: Dict[str, Any]
    ) -> Notification:
        """Send a fix request notification."""
        return self.send_notification(
            notification_type=NotificationType.FIX_REQUEST,
            title=f"Fix Requested: {task_id}",
            message=f"Fix requested for task {task_id}",
            context={
                "task_id": task_id,
                "fix_details": fix_details
            },
            priority=NotificationPriority.HIGH
        )
    
    def send_error_notification(
        self,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Send an error notification."""
        return self.send_notification(
            notification_type=NotificationType.ERROR,
            title="Error Occurred",
            message=error_message,
            context=context or {},
            priority=NotificationPriority.CRITICAL
        )