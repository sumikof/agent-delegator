"""Feedback Collection Agent.

This agent integrates with the workflow system to collect and process user feedback.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..agents.base import Agent as BaseAgent
from ..agents.registry import registry as agent_registry
from .models import FeedbackItem, FeedbackType, FeedbackPriority, FeedbackStatus, UserInfo, FeedbackContext
from .feedback_manager import FeedbackManager
from .feedback_processor import FeedbackProcessor
from .feedback_analyzer import FeedbackAnalyzer


class FeedbackCollectionAgent(BaseAgent):
    """Agent for collecting and processing user feedback."""
    
    def __init__(self, agent_id: str = "feedback_collector"):
        super().__init__(agent_id, "Feedback Collection Agent", "feedback_collection")
        
        # Initialize feedback components
        self.feedback_manager = FeedbackManager()
        self.feedback_processor = FeedbackProcessor(self.feedback_manager)
        self.feedback_analyzer = FeedbackAnalyzer(self.feedback_manager)
        
        # Agent capabilities
        self.capabilities = [
            "feedback_collection",
            "feedback_processing", 
            "feedback_analysis",
            "user_satisfaction_surveys"
        ]
    
    def execute(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute feedback collection task."""
        action = task.get("action", "collect_feedback")
        
        if action == "collect_feedback":
            return self.collect_feedback(task, context)
        elif action == "process_feedback":
            return self.process_feedback(task, context)
        elif action == "analyze_feedback":
            return self.analyze_feedback(task, context)
        elif action == "generate_report":
            return self.generate_report(task, context)
        elif action == "get_statistics":
            return self.get_statistics(task, context)
        else:
            return self._create_error_response(f"Unknown action: {action}")
    
    def collect_feedback(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collect user feedback."""
        try:
            feedback_data = task.get("feedback_data", {})
            feedback_type = feedback_data.get("type", "general")
            
            # Extract user info from context
            user_info: UserInfo = {
                "user_id": context.get("user_id") if context else None,
                "user_name": context.get("user_name") if context else None,
                "user_email": context.get("user_email") if context else None,
                "user_role": context.get("user_role") if context else None,
                "session_id": context.get("session_id") if context else None
            }
            
            # Extract workflow context
            workflow_context: FeedbackContext = {
                "workflow_id": context.get("workflow_id") if context else None,
                "task_id": context.get("task_id") if context else None,
                "agent_id": context.get("agent_id") if context else None,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                "system_version": context.get("system_version", "1.0.0") if context else "1.0.0",
                "environment": context.get("environment", "production") if context else "production"
            }
            
            # Process different types of feedback
            if feedback_type == "bug_report":
                feedback_item = self.feedback_processor.process_bug_report(
                    title=feedback_data.get("title", "Bug Report"),
                    description=feedback_data.get("description", ""),
                    steps_to_reproduce=feedback_data.get("steps_to_reproduce", ""),
                    user_info=user_info,
                    context=workflow_context,
                    severity=feedback_data.get("severity", "medium")
                )
            elif feedback_type == "feature_request":
                feedback_item = self.feedback_processor.process_feature_request(
                    title=feedback_data.get("title", "Feature Request"),
                    description=feedback_data.get("description", ""),
                    use_case=feedback_data.get("use_case", ""),
                    user_info=user_info,
                    context=workflow_context,
                    priority_hint=feedback_data.get("priority_hint", "medium")
                )
            elif feedback_type == "satisfaction_survey":
                feedback_item = self.feedback_processor.process_satisfaction_survey(
                    user_id=user_info.get("user_id"),
                    workflow_id=workflow_context.get("workflow_id"),
                    overall_satisfaction=feedback_data.get("overall_satisfaction", 3),
                    comments=feedback_data.get("comments", ""),
                    specific_feedback=feedback_data.get("specific_feedback", {})
                )
            elif feedback_type == "usability":
                feedback_item = self.feedback_processor.process_usability_feedback(
                    title=feedback_data.get("title", "Usability Feedback"),
                    description=feedback_data.get("description", ""),
                    user_info=user_info,
                    context=workflow_context,
                    severity=feedback_data.get("severity", "medium")
                )
            elif feedback_type == "performance":
                feedback_item = self.feedback_processor.process_performance_feedback(
                    title=feedback_data.get("title", "Performance Feedback"),
                    description=feedback_data.get("description", ""),
                    performance_metrics=feedback_data.get("performance_metrics", {}),
                    user_info=user_info,
                    context=workflow_context
                )
            else:  # general feedback
                feedback_item = self.feedback_processor.process_feedback(
                    feedback_type=FeedbackType(feedback_type),
                    title=feedback_data.get("title", "User Feedback"),
                    description=feedback_data.get("description", ""),
                    user_info=user_info,
                    context=workflow_context,
                    priority=FeedbackPriority(feedback_data.get("priority", "medium"))
                )
            
            return self._create_success_response(
                "Feedback collected successfully",
                {
                    "feedback_id": feedback_item.feedback_id,
                    "feedback_type": str(feedback_item.feedback_type),
                    "title": feedback_item.title,
                    "status": str(feedback_item.status),
                    "priority": str(feedback_item.priority),
                    "created_at": feedback_item.created_at
                }
            )
            
        except Exception as e:
            return self._create_error_response(f"Error collecting feedback: {str(e)}")
    
    def process_feedback(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process existing feedback."""
        try:
            action = task.get("action_type", "review")
            feedback_id = task.get("feedback_id")
            
            if not feedback_id:
                return self._create_error_response("Feedback ID is required")
            
            feedback_item = self.feedback_manager.get_feedback_by_id(feedback_id)
            if not feedback_item:
                return self._create_error_response("Feedback not found")
            
            if action == "escalate":
                reason = task.get("reason", "Manual escalation")
                success = self.feedback_processor.escalate_feedback(feedback_id, reason)
                if success:
                    return self._create_success_response(
                        "Feedback escalated successfully",
                        {"feedback_id": feedback_id, "new_priority": str(feedback_item.priority)}
                    )
                else:
                    return self._create_error_response("Failed to escalate feedback")
            
            elif action == "resolve":
                resolution_notes = task.get("resolution_notes", "Feedback resolved")
                success = self.feedback_processor.resolve_feedback(feedback_id, resolution_notes)
                if success:
                    return self._create_success_response(
                        "Feedback resolved successfully",
                        {"feedback_id": feedback_id, "status": "RESOLVED"}
                    )
                else:
                    return self._create_error_response("Failed to resolve feedback")
            
            elif action == "reject":
                rejection_reason = task.get("rejection_reason", "Feedback rejected")
                success = self.feedback_processor.reject_feedback(feedback_id, rejection_reason)
                if success:
                    return self._create_success_response(
                        "Feedback rejected successfully",
                        {"feedback_id": feedback_id, "status": "REJECTED"}
                    )
                else:
                    return self._create_error_response("Failed to reject feedback")
            
            elif action == "update_status":
                new_status = task.get("new_status")
                if new_status:
                    success = self.feedback_manager.update_feedback_status(feedback_id, FeedbackStatus(new_status))
                    if success:
                        return self._create_success_response(
                            "Feedback status updated successfully",
                            {"feedback_id": feedback_id, "status": new_status}
                        )
                    else:
                        return self._create_error_response("Failed to update feedback status")
                else:
                    return self._create_error_response("New status is required")
            
            else:
                return self._create_error_response(f"Unknown action type: {action}")
                
        except Exception as e:
            return self._create_error_response(f"Error processing feedback: {str(e)}")
    
    def analyze_feedback(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze feedback data."""
        try:
            analysis_type = task.get("analysis_type", "trends")
            
            if analysis_type == "trends":
                time_period = task.get("time_period", "month")
                trends = self.feedback_analyzer.analyze_feedback_trends(time_period)
                return self._create_success_response("Feedback trends analyzed", {"trends": trends})
            
            elif analysis_type == "sentiment":
                feedback_id = task.get("feedback_id")
                sentiment = self.feedback_analyzer.analyze_sentiment(feedback_id)
                return self._create_success_response("Feedback sentiment analyzed", {"sentiment": sentiment})
            
            elif analysis_type == "topics":
                limit = task.get("limit", 10)
                topics = self.feedback_analyzer.extract_key_topics(limit)
                return self._create_success_response("Key topics extracted", {"topics": topics})
            
            elif analysis_type == "by_agent":
                agent_analysis = self.feedback_analyzer.analyze_feedback_by_agent()
                return self._create_success_response("Feedback by agent analyzed", {"agent_analysis": agent_analysis})
            
            elif analysis_type == "by_workflow":
                workflow_analysis = self.feedback_analyzer.analyze_feedback_by_workflow()
                return self._create_success_response("Feedback by workflow analyzed", {"workflow_analysis": workflow_analysis})
            
            elif analysis_type == "quality":
                quality_analysis = self.feedback_analyzer.analyze_feedback_quality()
                return self._create_success_response("Feedback quality analyzed", {"quality_analysis": quality_analysis})
            
            else:
                return self._create_error_response(f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            return self._create_error_response(f"Error analyzing feedback: {str(e)}")
    
    def generate_report(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive feedback report."""
        try:
            report = self.feedback_analyzer.generate_feedback_report()
            return self._create_success_response("Feedback report generated", {"report": report})
        except Exception as e:
            return self._create_error_response(f"Error generating report: {str(e)}")
    
    def get_statistics(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get feedback statistics."""
        try:
            stats = self.feedback_manager.get_feedback_statistics()
            open_count = self.feedback_manager.get_open_feedback_count()
            high_priority = self.feedback_manager.get_high_priority_feedback()
            
            return self._create_success_response(
                "Feedback statistics retrieved",
                {
                    "statistics": stats,
                    "open_feedback_count": open_count,
                    "high_priority_feedback": [
                        {
                            "feedback_id": item.feedback_id,
                            "title": item.title,
                            "type": str(item.feedback_type),
                            "priority": str(item.priority),
                            "status": str(item.status)
                        } for item in high_priority
                    ]
                }
            )
        except Exception as e:
            return self._create_error_response(f"Error getting statistics: {str(e)}")
    
    def _create_success_response(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a success response."""
        response = {
            "status": "SUCCESS",
            "message": message,
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "data": data or {}
        }
        return response
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response."""
        response = {
            "status": "ERROR",
            "message": error_message,
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "data": {}
        }
        return response


# Register the feedback collection agent
def register_feedback_agents():
    """Register feedback collection agents."""
    feedback_agent = FeedbackCollectionAgent()
    agent_registry.register_agent(feedback_agent)
    print(f"Registered feedback collection agent: {feedback_agent.agent_id}")