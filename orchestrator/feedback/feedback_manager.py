"""Feedback Manager.

This module manages the storage, retrieval, and lifecycle of user feedback items.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import os

from .models import FeedbackItem, FeedbackType, FeedbackStatus, FeedbackPriority, FeedbackStatistics


class FeedbackManager:
    """Manages user feedback collection and storage."""
    
    def __init__(self, storage_file: str = "feedback_store.json"):
        self._feedback_items: List[FeedbackItem] = []
        self._lock = threading.Lock()
        self._storage_file = storage_file
        self._load_feedback()
    
    def _load_feedback(self) -> None:
        """Load feedback from storage file."""
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, 'r') as f:
                    data = json.load(f)
                    for item_data in data:
                        try:
                            feedback_item = FeedbackItem(
                                feedback_type=FeedbackType(item_data["feedback_type"]),
                                title=item_data["title"],
                                description=item_data["description"],
                                user_info=item_data.get("user_info", {}),
                                context=item_data.get("context", {}),
                                priority=FeedbackPriority(item_data["priority"]),
                                status=FeedbackStatus(item_data["status"])
                            )
                            feedback_item.feedback_id = item_data["feedback_id"]
                            feedback_item.created_at = item_data["created_at"]
                            feedback_item.updated_at = item_data.get("updated_at")
                            feedback_item.resolved_at = item_data.get("resolved_at")
                            feedback_item.metadata = item_data.get("metadata", {})
                            self._feedback_items.append(feedback_item)
                        except Exception as e:
                            print(f"Error loading feedback item: {e}")
            except Exception as e:
                print(f"Error loading feedback store: {e}")
    
    def _save_feedback(self) -> None:
        """Save feedback to storage file."""
        try:
            data = [item.to_dict() for item in self._feedback_items]
            with open(self._storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback store: {e}")
    
    def add_feedback(self, feedback_item: FeedbackItem) -> FeedbackItem:
        """Add a new feedback item."""
        with self._lock:
            self._feedback_items.append(feedback_item)
            self._save_feedback()
        return feedback_item
    
    def get_feedback_by_id(self, feedback_id: str) -> Optional[FeedbackItem]:
        """Get feedback item by ID."""
        with self._lock:
            for item in self._feedback_items:
                if item.feedback_id == feedback_id:
                    return item
            return None
    
    def get_all_feedback(
        self,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        priority: Optional[FeedbackPriority] = None,
        limit: int = 100
    ) -> List[FeedbackItem]:
        """Get all feedback items with optional filtering."""
        with self._lock:
            items = self._feedback_items.copy()
            
            # Filter by type
            if feedback_type:
                items = [item for item in items if item.feedback_type == feedback_type]
            
            # Filter by status
            if status:
                items = [item for item in items if item.status == status]
            
            # Filter by priority
            if priority:
                items = [item for item in items if item.priority == priority]
            
            # Sort by created_at (newest first)
            items.sort(key=lambda x: x.created_at, reverse=True)
            
            # Limit results
            return items[:limit]
    
    def update_feedback_status(self, feedback_id: str, new_status: FeedbackStatus) -> bool:
        """Update the status of a feedback item."""
        with self._lock:
            for item in self._feedback_items:
                if item.feedback_id == feedback_id:
                    item.update_status(new_status)
                    self._save_feedback()
                    return True
            return False
    
    def update_feedback_priority(self, feedback_id: str, new_priority: FeedbackPriority) -> bool:
        """Update the priority of a feedback item."""
        with self._lock:
            for item in self._feedback_items:
                if item.feedback_id == feedback_id:
                    item.update_priority(new_priority)
                    self._save_feedback()
                    return True
            return False
    
    def add_feedback_metadata(self, feedback_id: str, key: str, value: Any) -> bool:
        """Add metadata to a feedback item."""
        with self._lock:
            for item in self._feedback_items:
                if item.feedback_id == feedback_id:
                    item.add_metadata(key, value)
                    self._save_feedback()
                    return True
            return False
    
    def get_feedback_statistics(self) -> FeedbackStatistics:
        """Get statistics about feedback items."""
        with self._lock:
            total_feedback = len(self._feedback_items)
            
            # Count by type
            feedback_by_type = {}
            for feedback_type in FeedbackType:
                count = sum(1 for item in self._feedback_items if item.feedback_type == feedback_type)
                feedback_by_type[feedback_type] = count
            
            # Count by status
            feedback_by_status = {}
            for status in FeedbackStatus:
                count = sum(1 for item in self._feedback_items if item.status == status)
                feedback_by_status[status] = count
            
            # Count by priority
            feedback_by_priority = {}
            for priority in FeedbackPriority:
                count = sum(1 for item in self._feedback_items if item.priority == priority)
                feedback_by_priority[priority] = count
            
            # Calculate average resolution time
            resolved_items = [item for item in self._feedback_items 
                            if item.resolved_at and item.created_at]
            if resolved_items:
                avg_resolution_time = sum(
                    item.resolved_at - item.created_at for item in resolved_items
                ) / len(resolved_items)
            else:
                avg_resolution_time = None
            
            # Calculate satisfaction score (if available)
            satisfaction_scores = [
                item.metadata.get("satisfaction_score") 
                for item in self._feedback_items 
                if item.metadata.get("satisfaction_score") is not None
            ]
            satisfaction_score = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
            
            return {
                "total_feedback": total_feedback,
                "feedback_by_type": feedback_by_type,
                "feedback_by_status": feedback_by_status,
                "feedback_by_priority": feedback_by_priority,
                "average_resolution_time": avg_resolution_time,
                "satisfaction_score": satisfaction_score
            }
    
    def get_open_feedback_count(self) -> int:
        """Get count of open feedback items."""
        with self._lock:
            open_statuses = [FeedbackStatus.NEW, FeedbackStatus.REVIEWED, FeedbackStatus.IN_PROGRESS]
            return sum(1 for item in self._feedback_items if item.status in open_statuses)
    
    def get_high_priority_feedback(self, limit: int = 10) -> List[FeedbackItem]:
        """Get high priority feedback items."""
        with self._lock:
            high_priority_items = [
                item for item in self._feedback_items 
                if item.priority in [FeedbackPriority.CRITICAL, FeedbackPriority.HIGH]
                and item.status in [FeedbackStatus.NEW, FeedbackStatus.REVIEWED]
            ]
            high_priority_items.sort(key=lambda x: (x.priority.value, x.created_at))
            return high_priority_items[:limit]
    
    def search_feedback(self, query: str, limit: int = 20) -> List[FeedbackItem]:
        """Search feedback items by query."""
        with self._lock:
            query = query.lower()
            results = []
            
            for item in self._feedback_items:
                # Search in title and description
                if (query in item.title.lower() or 
                    query in item.description.lower()):
                    results.append(item)
            
            results.sort(key=lambda x: x.created_at, reverse=True)
            return results[:limit]
    
    def clear_resolved_feedback(self) -> int:
        """Clear resolved feedback items."""
        with self._lock:
            resolved_statuses = [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED, FeedbackStatus.REJECTED]
            original_count = len(self._feedback_items)
            self._feedback_items = [
                item for item in self._feedback_items 
                if item.status not in resolved_statuses
            ]
            self._save_feedback()
            return original_count - len(self._feedback_items)
