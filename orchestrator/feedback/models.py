"""Feedback data models and schemas.

This module defines the data structures for user feedback collection and processing.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass
import time
import uuid


class FeedbackType(str, Enum):
    """Types of feedback that can be collected."""
    BUG_REPORT = "bug_report"  # Bug or issue report
    FEATURE_REQUEST = "feature_request"  # Feature request or enhancement
    USABILITY = "usability"  # Usability feedback
    PERFORMANCE = "performance"  # Performance feedback
    GENERAL = "general"  # General feedback or comments
    SATISFACTION = "satisfaction"  # User satisfaction survey


class FeedbackPriority(int, Enum):
    """Priority levels for feedback items."""
    CRITICAL = 1  # Critical issue requiring immediate attention
    HIGH = 2  # High priority feedback
    MEDIUM = 3  # Medium priority feedback
    LOW = 4  # Low priority feedback


class FeedbackStatus(str, Enum):
    """Status of feedback items."""
    NEW = "new"  # Newly submitted feedback
    REVIEWED = "reviewed"  # Feedback has been reviewed
    IN_PROGRESS = "in_progress"  # Feedback is being addressed
    RESOLVED = "resolved"  # Feedback has been resolved
    CLOSED = "closed"  # Feedback has been closed
    REJECTED = "rejected"  # Feedback has been rejected


class UserInfo(TypedDict):
    """User information associated with feedback."""
    user_id: Optional[str]
    user_name: Optional[str]
    user_email: Optional[str]
    user_role: Optional[str]
    session_id: Optional[str]


class FeedbackContext(TypedDict):
    """Context information for feedback."""
    workflow_id: Optional[str]
    task_id: Optional[str]
    agent_id: Optional[str]
    timestamp: Optional[str]
    system_version: Optional[str]
    environment: Optional[str]


@dataclass
class FeedbackItem:
    """Representation of a user feedback item."""
    feedback_id: str
    feedback_type: FeedbackType
    title: str
    description: str
    user_info: UserInfo
    context: FeedbackContext
    priority: FeedbackPriority
    status: FeedbackStatus
    created_at: float
    updated_at: Optional[float]
    resolved_at: Optional[float]
    metadata: Dict[str, Any]
    
    def __init__(
        self,
        feedback_type: FeedbackType,
        title: str,
        description: str,
        user_info: Optional[UserInfo] = None,
        context: Optional[FeedbackContext] = None,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        status: FeedbackStatus = FeedbackStatus.NEW,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.feedback_id = str(uuid.uuid4())
        self.feedback_type = feedback_type
        self.title = title
        self.description = description
        self.user_info = user_info or {}
        self.context = context or {}
        self.priority = priority
        self.status = status
        self.created_at = time.time()
        self.updated_at = None
        self.resolved_at = None
        self.metadata = metadata or {}
    
    def update_status(self, new_status: FeedbackStatus) -> None:
        """Update the status of the feedback."""
        self.status = new_status
        self.updated_at = time.time()
        
        if new_status in [FeedbackStatus.RESOLVED, FeedbackStatus.CLOSED, FeedbackStatus.REJECTED]:
            self.resolved_at = time.time()
    
    def update_priority(self, new_priority: FeedbackPriority) -> None:
        """Update the priority of the feedback."""
        self.priority = new_priority
        self.updated_at = time.time()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the feedback."""
        self.metadata[key] = value
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback item to dictionary."""
        return {
            "feedback_id": self.feedback_id,
            "feedback_type": self.feedback_type,
            "title": self.title,
            "description": self.description,
            "user_info": self.user_info,
            "context": self.context,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "metadata": self.metadata
        }


class FeedbackSurvey(TypedDict):
    """Structure for user satisfaction surveys."""
    survey_id: str
    user_id: Optional[str]
    workflow_id: Optional[str]
    timestamp: float
    responses: Dict[str, Any]  # Question ID -> Response
    overall_satisfaction: int  # 1-5 scale
    comments: Optional[str]


class FeedbackStatistics(TypedDict):
    """Statistics for feedback analysis."""
    total_feedback: int
    feedback_by_type: Dict[FeedbackType, int]
    feedback_by_status: Dict[FeedbackStatus, int]
    feedback_by_priority: Dict[FeedbackPriority, int]
    average_resolution_time: Optional[float]
    satisfaction_score: Optional[float]
