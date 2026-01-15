"""Feedback Analyzer.

This module provides analysis and insights from collected feedback data.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
from collections import Counter

from .models import FeedbackItem, FeedbackType, FeedbackStatus, FeedbackPriority, FeedbackStatistics
from .feedback_manager import FeedbackManager


class FeedbackAnalyzer:
    """Analyzes feedback data and provides insights."""
    
    def __init__(self, feedback_manager: FeedbackManager):
        self.feedback_manager = feedback_manager
    
    def analyze_feedback_trends(self, time_period: str = "month") -> Dict[str, Any]:
        """Analyze feedback trends over time."""
        all_feedback = self.feedback_manager.get_all_feedback(limit=1000)
        
        # Group by time period
        trends = {}
        
        for item in all_feedback:
            # Convert timestamp to time period key
            if time_period == "day":
                period_key = time.strftime("%Y-%m-%d", time.localtime(item.created_at))
            elif time_period == "week":
                period_key = time.strftime("%Y-W%V", time.localtime(item.created_at))
            elif time_period == "month":
                period_key = time.strftime("%Y-%m", time.localtime(item.created_at))
            else:  # default to day
                period_key = time.strftime("%Y-%m-%d", time.localtime(item.created_at))
            
            if period_key not in trends:
                trends[period_key] = {
                    "total": 0,
                    "by_type": {},
                    "by_priority": {}
                }
            
            trends[period_key]["total"] += 1
            
            # Count by type
            feedback_type_str = str(item.feedback_type)
            trends[period_key]["by_type"][feedback_type_str] = trends[period_key]["by_type"].get(feedback_type_str, 0) + 1
            
            # Count by priority
            priority_str = str(item.priority)
            trends[period_key]["by_priority"][priority_str] = trends[period_key]["by_priority"].get(priority_str, 0) + 1
        
        return trends
    
    def analyze_sentiment(self, feedback_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze sentiment of feedback (simple implementation)."""
        if feedback_id:
            feedback_items = [self.feedback_manager.get_feedback_by_id(feedback_id)]
            if not feedback_items[0]:
                return {"error": "Feedback not found"}
        else:
            feedback_items = self.feedback_manager.get_all_feedback(limit=100)
        
        results = {}
        
        for item in feedback_items:
            if not item:
                continue
                
            text = f"{item.title} {item.description}".lower()
            
            # Simple sentiment analysis
            positive_words = ["good", "great", "excellent", "awesome", "perfect", "love", "happy"]
            negative_words = ["bad", "poor", "terrible", "awful", "hate", "broken", "fail", "error", "crash"]
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            # Calculate sentiment score
            if positive_count + negative_count > 0:
                sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
            else:
                sentiment_score = 0
            
            # Determine sentiment category
            if sentiment_score > 0.3:
                sentiment = "positive"
            elif sentiment_score < -0.3:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            results[item.feedback_id] = {
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "positive_words": positive_count,
                "negative_words": negative_count
            }
        
        return results
    
    def extract_key_topics(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Extract key topics from feedback using simple text analysis."""
        all_feedback = self.feedback_manager.get_all_feedback(limit=100)
        
        # Common words to ignore
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "can", "this",
            "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }
        
        # Extract words from all feedback
        all_words = []
        
        for item in all_feedback:
            text = f"{item.title} {item.description}".lower()
            # Remove punctuation and split into words
            words = re.findall(r'\b[a-z]{3,}\b', text)
            # Filter out stop words
            filtered_words = [word for word in words if word not in stop_words]
            all_words.extend(filtered_words)
        
        # Count word frequencies
        word_counts = Counter(all_words)
        
        # Get most common words
        return word_counts.most_common(limit)
    
    def analyze_feedback_by_agent(self) -> Dict[str, Any]:
        """Analyze feedback by agent."""
        all_feedback = self.feedback_manager.get_all_feedback(limit=1000)
        
        agent_feedback = {}
        
        for item in all_feedback:
            agent_id = item.context.get("agent_id")
            if agent_id:
                if agent_id not in agent_feedback:
                    agent_feedback[agent_id] = {
                        "total": 0,
                        "by_type": {},
                        "by_priority": {},
                        "sentiment_scores": []
                    }
                
                agent_feedback[agent_id]["total"] += 1
                
                # Count by type
                feedback_type_str = str(item.feedback_type)
                agent_feedback[agent_id]["by_type"][feedback_type_str] = agent_feedback[agent_id]["by_type"].get(feedback_type_str, 0) + 1
                
                # Count by priority
                priority_str = str(item.priority)
                agent_feedback[agent_id]["by_priority"][priority_str] = agent_feedback[agent_id]["by_priority"].get(priority_str, 0) + 1
                
                # Simple sentiment analysis
                text = f"{item.title} {item.description}".lower()
                positive_words = ["good", "great", "excellent", "awesome", "perfect"]
                negative_words = ["bad", "poor", "terrible", "awful", "broken", "fail"]
                
                positive_count = sum(1 for word in positive_words if word in text)
                negative_count = sum(1 for word in negative_words if word in text)
                
                if positive_count + negative_count > 0:
                    sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
                else:
                    sentiment_score = 0
                
                agent_feedback[agent_id]["sentiment_scores"].append(sentiment_score)
        
        # Calculate average sentiment for each agent
        for agent_id, data in agent_feedback.items():
            if data["sentiment_scores"]:
                avg_sentiment = sum(data["sentiment_scores"]) / len(data["sentiment_scores"])
                data["average_sentiment"] = avg_sentiment
            else:
                data["average_sentiment"] = 0
        
        return agent_feedback
    
    def analyze_feedback_by_workflow(self) -> Dict[str, Any]:
        """Analyze feedback by workflow."""
        all_feedback = self.feedback_manager.get_all_feedback(limit=1000)
        
        workflow_feedback = {}
        
        for item in all_feedback:
            workflow_id = item.context.get("workflow_id")
            if workflow_id:
                if workflow_id not in workflow_feedback:
                    workflow_feedback[workflow_id] = {
                        "total": 0,
                        "by_type": {},
                        "by_status": {},
                        "satisfaction_scores": []
                    }
                
                workflow_feedback[workflow_id]["total"] += 1
                
                # Count by type
                feedback_type_str = str(item.feedback_type)
                workflow_feedback[workflow_id]["by_type"][feedback_type_str] = workflow_feedback[workflow_id]["by_type"].get(feedback_type_str, 0) + 1
                
                # Count by status
                status_str = str(item.status)
                workflow_feedback[workflow_id]["by_status"][status_str] = workflow_feedback[workflow_id]["by_status"].get(status_str, 0) + 1
                
                # Extract satisfaction score if available
                satisfaction_score = item.metadata.get("satisfaction_score")
                if satisfaction_score is not None:
                    workflow_feedback[workflow_id]["satisfaction_scores"].append(satisfaction_score)
        
        # Calculate average satisfaction for each workflow
        for workflow_id, data in workflow_feedback.items():
            if data["satisfaction_scores"]:
                avg_satisfaction = sum(data["satisfaction_scores"]) / len(data["satisfaction_scores"])
                data["average_satisfaction"] = avg_satisfaction
            else:
                data["average_satisfaction"] = None
        
        return workflow_feedback
    
    def generate_feedback_report(self) -> Dict[str, Any]:
        """Generate a comprehensive feedback report."""
        stats = self.feedback_manager.get_feedback_statistics()
        trends = self.analyze_feedback_trends()
        topics = self.extract_key_topics(5)
        agent_analysis = self.analyze_feedback_by_agent()
        workflow_analysis = self.analyze_feedback_by_workflow()
        
        return {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            "statistics": stats,
            "trends": trends,
            "key_topics": topics,
            "agent_analysis": agent_analysis,
            "workflow_analysis": workflow_analysis,
            "recommendations": self._generate_recommendations(stats, topics, agent_analysis)
        }
    
    def _generate_recommendations(self, stats: FeedbackStatistics, topics: List[Tuple[str, int]], 
                                  agent_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feedback analysis."""
        recommendations = []
        
        # Check for high priority feedback
        high_priority_count = stats["feedback_by_priority"].get(FeedbackPriority.HIGH, 0) + stats["feedback_by_priority"].get(FeedbackPriority.CRITICAL, 0)
        
        if high_priority_count > stats["total_feedback"] * 0.2:  # More than 20% high priority
            recommendations.append(
                f"High priority feedback represents {high_priority_count}/{stats['total_feedback']} "
                f"({high_priority_count/stats['total_feedback']*100:.1f}%) of total feedback. "
                "Immediate attention required."
            )
        
        # Check satisfaction score
        if stats["satisfaction_score"] is not None and stats["satisfaction_score"] < 3.5:
            recommendations.append(
                f"User satisfaction score is low ({stats['satisfaction_score']:.2f}/5). "
                "Investigate user experience issues."
            )
        
        # Check for unresolved feedback
        open_feedback = stats["feedback_by_status"].get(FeedbackStatus.NEW, 0) + stats["feedback_by_status"].get(FeedbackStatus.REVIEWED, 0) + stats["feedback_by_status"].get(FeedbackStatus.IN_PROGRESS, 0)
        
        if open_feedback > stats["total_feedback"] * 0.3:  # More than 30% open
            recommendations.append(
                f"Large backlog of open feedback ({open_feedback}/{stats['total_feedback']} "
                f"({open_feedback/stats['total_feedback']*100:.1f}%)). "
                "Consider allocating more resources to feedback processing."
            )
        
        # Check resolution time
        if stats["average_resolution_time"] and stats["average_resolution_time"] > 86400:  # > 1 day
            days = stats["average_resolution_time"] / 86400
            recommendations.append(
                f"Average resolution time is high ({days:.1f} days). "
                "Consider improving feedback processing workflow."
            )
        
        # Analyze key topics
        if topics:
            top_topic = topics[0][0]
            recommendations.append(
                f"Most frequent topic: '{top_topic}'. Consider addressing this area "
                "or providing more documentation/training."
            )
        
        # Check agent performance
        for agent_id, data in agent_analysis.items():
            if data.get("average_sentiment", 0) < -0.2:  # Negative sentiment
                recommendations.append(
                    f"Agent {agent_id} has negative user sentiment (avg: {data['average_sentiment']:.2f}). "
                    "Review agent performance and user interactions."
                )
        
        if not recommendations:
            recommendations.append("Feedback analysis shows healthy system performance. Continue monitoring.")
        
        return recommendations
    
    def analyze_feedback_quality(self) -> Dict[str, Any]:
        """Analyze the quality and usefulness of feedback."""
        all_feedback = self.feedback_manager.get_all_feedback(limit=100)
        
        quality_metrics = {
            "total_feedback": len(all_feedback),
            "detailed_feedback": 0,  # Feedback with > 50 characters in description
            "actionable_feedback": 0,  # Feedback containing specific actionable items
            "low_quality_feedback": 0,  # Very short or unclear feedback
            "average_description_length": 0,
            "feedback_with_context": 0
        }
        
        if not all_feedback:
            return quality_metrics
        
        description_lengths = []
        
        for item in all_feedback:
            desc_length = len(item.description)
            description_lengths.append(desc_length)
            
            # Count detailed feedback
            if desc_length > 50:
                quality_metrics["detailed_feedback"] += 1
            
            # Count actionable feedback (contains specific action words)
            action_words = ["should", "need", "require", "fix", "improve", "add", "remove", "change"]
            if any(word in item.description.lower() for word in action_words):
                quality_metrics["actionable_feedback"] += 1
            
            # Count low quality feedback
            if desc_length < 10:
                quality_metrics["low_quality_feedback"] += 1
            
            # Count feedback with context
            if item.context and any(item.context.values()):
                quality_metrics["feedback_with_context"] += 1
        
        quality_metrics["average_description_length"] = sum(description_lengths) / len(description_lengths)
        
        # Calculate percentages
        quality_metrics["detailed_percentage"] = quality_metrics["detailed_feedback"] / quality_metrics["total_feedback"]
        quality_metrics["actionable_percentage"] = quality_metrics["actionable_feedback"] / quality_metrics["total_feedback"]
        quality_metrics["low_quality_percentage"] = quality_metrics["low_quality_feedback"] / quality_metrics["total_feedback"]
        quality_metrics["context_percentage"] = quality_metrics["feedback_with_context"] / quality_metrics["total_feedback"]
        
        return quality_metrics
