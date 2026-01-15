"""Feedback Processor.

This module processes incoming feedback and integrates with the workflow system.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .models import FeedbackItem, FeedbackType, FeedbackPriority, FeedbackStatus, UserInfo, FeedbackContext
from .feedback_manager import FeedbackManager


class FeedbackProcessor:
    """Processes incoming feedback and manages feedback workflow."""
    
    def __init__(self, feedback_manager: FeedbackManager):
        self.feedback_manager = feedback_manager
    
    def process_feedback(
        self,
        feedback_type: FeedbackType,
        title: str,
        description: str,
        user_info: Optional[UserInfo] = None,
        context: Optional[FeedbackContext] = None,
        priority: Optional[FeedbackPriority] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FeedbackItem:
        """Process a new feedback item."""
        # Determine priority if not specified
        if priority is None:
            priority = self._determine_priority(feedback_type, description)
        
        # Create feedback item
        feedback_item = FeedbackItem(
            feedback_type=feedback_type,
            title=title,
            description=description,
            user_info=user_info,
            context=context,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Add timestamp to metadata
        feedback_item.add_metadata("processed_at", time.time())
        
        # Store feedback
        self.feedback_manager.add_feedback(feedback_item)
        
        return feedback_item
    
    def _determine_priority(self, feedback_type: FeedbackType, description: str) -> FeedbackPriority:
        """Determine priority based on feedback type and content."""
        # Keywords that indicate high priority
        critical_keywords = ["crash", "hang", "freeze", "data loss", "security", "urgent"]
        high_keywords = ["error", "bug", "broken", "fail", "problem", "issue"]
        
        description_lower = description.lower()
        
        # Check for critical keywords
        if any(keyword in description_lower for keyword in critical_keywords):
            return FeedbackPriority.CRITICAL
        
        # Check for high priority keywords
        if any(keyword in description_lower for keyword in high_keywords):
            return FeedbackPriority.HIGH
        
        # Default priority based on feedback type
        if feedback_type == FeedbackType.BUG_REPORT:
            return FeedbackPriority.HIGH
        elif feedback_type == FeedbackType.FEATURE_REQUEST:
            return FeedbackPriority.MEDIUM
        elif feedback_type == FeedbackType.PERFORMANCE:
            return FeedbackPriority.HIGH
        else:
            return FeedbackPriority.MEDIUM
    
    def process_bug_report(
        self,
        title: str,
        description: str,
        steps_to_reproduce: str,
        user_info: Optional[UserInfo] = None,
        context: Optional[FeedbackContext] = None,
        severity: str = "medium"
    ) -> FeedbackItem:
        """Process a bug report."""
        metadata = {
            "steps_to_reproduce": steps_to_reproduce,
            "severity": severity
        }
        
        # Determine priority based on severity
        severity_priority = {
            "critical": FeedbackPriority.CRITICAL,
            "high": FeedbackPriority.HIGH,
            "medium": FeedbackPriority.MEDIUM,
            "low": FeedbackPriority.LOW
        }
        
        priority = severity_priority.get(severity.lower(), FeedbackPriority.MEDIUM)
        
        return self.process_feedback(
            feedback_type=FeedbackType.BUG_REPORT,
            title=title,
            description=description,
            user_info=user_info,
            context=context,
            priority=priority,
            metadata=metadata
        )
    
    def process_feature_request(
        self,
        title: str,
        description: str,
        use_case: str,
        user_info: Optional[UserInfo] = None,
        context: Optional[FeedbackContext] = None,
        priority_hint: str = "medium"
    ) -> FeedbackItem:
        """Process a feature request."""
        metadata = {
            "use_case": use_case,
            "priority_hint": priority_hint
        }
        
        # Determine priority based on hint
        priority_map = {
            "critical": FeedbackPriority.HIGH,
            "high": FeedbackPriority.HIGH,
            "medium": FeedbackPriority.MEDIUM,
            "low": FeedbackPriority.LOW
        }
        
        priority = priority_map.get(priority_hint.lower(), FeedbackPriority.MEDIUM)
        
        return self.process_feedback(
            feedback_type=FeedbackType.FEATURE_REQUEST,
            title=title,
            description=description,
            user_info=user_info,
            context=context,
            priority=priority,
            metadata=metadata
        )
    
    def process_satisfaction_survey(
        self,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        overall_satisfaction: int = 3,
        comments: Optional[str] = None,
        specific_feedback: Optional[Dict[str, Any]] = None
    ) -> FeedbackItem:
        """Process a user satisfaction survey."""
        title = f"User Satisfaction Survey (Score: {overall_satisfaction}/5)"
        description = comments or "User satisfaction survey submission"
        
        user_info = {"user_id": user_id} if user_id else {}
        context = {"workflow_id": workflow_id} if workflow_id else {}
        
        metadata = {
            "survey_type": "satisfaction",
            "overall_satisfaction": overall_satisfaction,
            "specific_feedback": specific_feedback or {}
        }
        
        # Determine priority based on satisfaction score
        if overall_satisfaction <= 2:
            priority = FeedbackPriority.HIGH  # Low satisfaction needs attention
        elif overall_satisfaction == 3:
            priority = FeedbackPriority.MEDIUM
        else:
            priority = FeedbackPriority.LOW
        
        return self.process_feedback(
            feedback_type=FeedbackType.SATISFACTION,
            title=title,
            description=description,
            user_info=user_info,
            context=context,
            priority=priority,
            metadata=metadata
        )
    
    def process_usability_feedback(
        self,
        title: str,
        description: str,
        user_info: Optional[UserInfo] = None,
        context: Optional[FeedbackContext] = None,
        severity: str = "medium"
    ) -> FeedbackItem:
        """Process usability feedback."""
        metadata = {
            "feedback_category": "usability",
            "severity": severity
        }
        
        # Determine priority based on severity
        severity_priority = {
            "critical": FeedbackPriority.HIGH,
            "high": FeedbackPriority.HIGH,
            "medium": FeedbackPriority.MEDIUM,
            "low": FeedbackPriority.LOW
        }
        
        priority = severity_priority.get(severity.lower(), FeedbackPriority.MEDIUM)
        
        return self.process_feedback(
            feedback_type=FeedbackType.USABILITY,
            title=title,
            description=description,
            user_info=user_info,
            context=context,
            priority=priority,
            metadata=metadata
        )
    
    def process_performance_feedback(
        self,
        title: str,
        description: str,
        performance_metrics: Dict[str, Any],
        user_info: Optional[UserInfo] = None,
        context: Optional[FeedbackContext] = None
    ) -> FeedbackItem:
        """Process performance feedback."""
        metadata = {
            "feedback_category": "performance",
            "performance_metrics": performance_metrics
        }
        
        # Determine priority based on performance metrics
        priority = FeedbackPriority.MEDIUM
        
        # Check if performance metrics indicate issues
        if any(
            metric.get("value", 0) < metric.get("threshold", 0) 
            for metric in performance_metrics.values()
            if isinstance(metric, dict)
        ):
            priority = FeedbackPriority.HIGH
        
        return self.process_feedback(
            feedback_type=FeedbackType.PERFORMANCE,
            title=title,
            description=description,
            user_info=user_info,
            context=context,
            priority=priority,
            metadata=metadata
        )
    
    def escalate_feedback(self, feedback_id: str, reason: str) -> bool:
        """Escalate feedback priority."""
        feedback_item = self.feedback_manager.get_feedback_by_id(feedback_id)
        if feedback_item:
            # Increase priority by one level (but not above CRITICAL)
            if feedback_item.priority.value > FeedbackPriority.CRITICAL.value:
                new_priority = FeedbackPriority(feedback_item.priority.value - 1)
                self.feedback_manager.update_feedback_priority(feedback_id, new_priority)
                
                # Add escalation reason to metadata
                self.feedback_manager.add_feedback_metadata(feedback_id, "escalation_reason", reason)
                self.feedback_manager.add_feedback_metadata(feedback_id, "escalated_at", time.time())
                
                return True
        return False
    
    def resolve_feedback(self, feedback_id: str, resolution_notes: str) -> bool:
        """Mark feedback as resolved."""
        feedback_item = self.feedback_manager.get_feedback_by_id(feedback_id)
        if feedback_item:
            self.feedback_manager.update_feedback_status(feedback_id, FeedbackStatus.RESOLVED)
            self.feedback_manager.add_feedback_metadata(feedback_id, "resolution_notes", resolution_notes)
            self.feedback_manager.add_feedback_metadata(feedback_id, "resolved_by", "system")
            return True
        return False
    
    def reject_feedback(self, feedback_id: str, rejection_reason: str) -> bool:
        """Mark feedback as rejected."""
        feedback_item = self.feedback_manager.get_feedback_by_id(feedback_id)
        if feedback_item:
            self.feedback_manager.update_feedback_status(feedback_id, FeedbackStatus.REJECTED)
            self.feedback_manager.add_feedback_metadata(feedback_id, "rejection_reason", rejection_reason)
            self.feedback_manager.add_feedback_metadata(feedback_id, "rejected_by", "system")
            return True
        return False
