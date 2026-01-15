"""Notification manager for the orchestrator.

This module manages notifications and integrates with the workflow engine
to provide status change notifications, feedback requests, and approval notifications.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import time

from .notifier import Notifier, Notification, NotificationType, NotificationPriority


class NotificationManager:
    """Manages notifications and integrates with workflow engine."""
    
    def __init__(self):
        self._notifications: List[Notification] = []
        self._subscribers: Dict[NotificationType, List[Callable]] = {}
        self._lock = threading.Lock()
        
        # Initialize subscribers for all notification types
        for notification_type in NotificationType:
            self._subscribers[notification_type] = []
    
    def add_notification(self, notification: Notification) -> None:
        """Add a notification to the manager."""
        with self._lock:
            self._notifications.append(notification)
            
            # Notify subscribers
            for callback in self._subscribers.get(notification.notification_type, []):
                try:
                    callback(notification)
                except Exception as e:
                    print(f"Error in notification callback: {e}")
    
    def get_notifications(
        self,
        notification_type: Optional[NotificationType] = None,
        limit: int = 100,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications with optional filtering."""
        with self._lock:
            notifications = self._notifications.copy()
            
            # Filter by type if specified
            if notification_type:
                notifications = [n for n in notifications if n.notification_type == notification_type]
            
            # Filter unread only if specified
            if unread_only:
                notifications = [n for n in notifications if not n.read]
            
            # Limit results
            return notifications[-limit:] if limit else notifications
    
    def get_unread_count(self, notification_type: Optional[NotificationType] = None) -> int:
        """Get count of unread notifications."""
        with self._lock:
            if notification_type:
                return sum(1 for n in self._notifications 
                         if n.notification_type == notification_type and not n.read)
            else:
                return sum(1 for n in self._notifications if not n.read)
    
    def mark_notification_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        with self._lock:
            for notification in self._notifications:
                if notification.notification_id == notification_id:
                    notification.mark_as_read()
                    return True
            return False
    
    def mark_all_as_read(self, notification_type: Optional[NotificationType] = None) -> int:
        """Mark all notifications as read."""
        with self._lock:
            count = 0
            for notification in self._notifications:
                if not notification_type or notification.notification_type == notification_type:
                    if not notification.read:
                        notification.mark_as_read()
                        count += 1
            return count
    
    def subscribe(
        self,
        notification_type: NotificationType,
        callback: Callable[[Notification], None]
    ) -> None:
        """Subscribe to notifications of a specific type."""
        with self._lock:
            if notification_type not in self._subscribers:
                self._subscribers[notification_type] = []
            self._subscribers[notification_type].append(callback)
    
    def unsubscribe(
        self,
        notification_type: NotificationType,
        callback: Callable[[Notification], None]
    ) -> bool:
        """Unsubscribe from notifications of a specific type."""
        with self._lock:
            if notification_type in self._subscribers:
                try:
                    self._subscribers[notification_type].remove(callback)
                    return True
                except ValueError:
                    pass
            return False
    
    def clear_notifications(self, notification_type: Optional[NotificationType] = None) -> int:
        """Clear notifications."""
        with self._lock:
            if notification_type:
                original_count = len(self._notifications)
                self._notifications = [n for n in self._notifications 
                                     if n.notification_type != notification_type]
                return original_count - len(self._notifications)
            else:
                count = len(self._notifications)
                self._notifications = []
                return count
    
    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID."""
        with self._lock:
            for notification in self._notifications:
                if notification.notification_id == notification_id:
                    return notification
            return None


class ConsoleNotifier(Notifier):
    """Notifier that outputs to console."""
    
    def __init__(self, manager: NotificationManager):
        super().__init__("console")
        self.manager = manager
    
    def _deliver_notification(self, notification: Notification) -> None:
        """Deliver notification to console."""
        priority_str = {
            NotificationPriority.CRITICAL: "🔴 CRITICAL",
            NotificationPriority.HIGH: "🟡 HIGH",
            NotificationPriority.MEDIUM: "🟢 MEDIUM",
            NotificationPriority.LOW: "🔵 LOW"
        }.get(notification.priority, "🟤 UNKNOWN")
        
        print(f"[{priority_str}] [{notification.notification_type}] {notification.title}")
        print(f"  {notification.message}")
        
        # Add to manager
        self.manager.add_notification(notification)


class FileNotifier(Notifier):
    """Notifier that writes to a file."""
    
    def __init__(self, manager: NotificationManager, log_file: str = "notifications.log"):
        super().__init__("file")
        self.manager = manager
        self.log_file = log_file
    
    def _deliver_notification(self, notification: Notification) -> None:
        """Deliver notification to file."""
        with open(self.log_file, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{notification.notification_type}] {notification.title}\n")
            f.write(f"  {notification.message}\n")
            f.write(f"  Context: {notification.context}\n")
            f.write("-" * 50 + "\n")
        
        # Add to manager
        self.manager.add_notification(notification)