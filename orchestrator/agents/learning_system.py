"""Learning system for autonomous agents.

This module provides learning and adaptation capabilities for autonomous
agents to improve their performance over time.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import math
from collections import defaultdict


class LearningSystem:
    """Learning system for autonomous agents."""

    def __init__(self) -> None:
        self.knowledge_base = {}  # Accumulated knowledge
        self.performance_history = []  # History of agent performance
        self.learning_patterns = {}  # Learned patterns and insights
        self.feedback_history = []  # History of received feedback
        self.learning_metrics = {
            "total_learning_cycles": 0,
            "successful_adaptations": 0,
            "last_learning_time": None
        }

    def process_feedback(self, feedback: Dict[str, Any]) -> None:
        """Process feedback and update learning system."""
        # Store feedback in history
        feedback_record = {
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "feedback_type": feedback.get("type", "general")
        }
        self.feedback_history.append(feedback_record)
        
        # Extract learning from feedback
        self._extract_learning_from_feedback(feedback)
        
        # Keep history size manageable
        if len(self.feedback_history) > 50:
            self.feedback_history = self.feedback_history[-50:]

    def record_performance(self, performance_data: Dict[str, Any]) -> None:
        """Record agent performance for learning."""
        performance_record = {
            "timestamp": datetime.now().isoformat(),
            "performance": performance_data,
            "context_hash": self._generate_context_hash(performance_data.get("context", {}))
        }
        self.performance_history.append(performance_record)
        
        # Keep history size manageable
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    def perform_learning_cycle(self) -> Dict[str, Any]:
        """Perform a learning cycle to improve agent capabilities."""
        learning_results = {
            "learning_cycle_start": datetime.now().isoformat(),
            "new_patterns_learned": 0,
            "knowledge_updated": 0,
            "performance_improvements": []
        }
        
        # Analyze feedback patterns
        feedback_patterns = self._analyze_feedback_patterns()
        if feedback_patterns:
            self.learning_patterns["feedback_patterns"] = feedback_patterns
            learning_results["new_patterns_learned"] += 1
        
        # Analyze performance trends
        performance_trends = self._analyze_performance_trends()
        if performance_trends:
            self.learning_patterns["performance_trends"] = performance_trends
            learning_results["new_patterns_learned"] += 1
        
        # Update knowledge base
        knowledge_updates = self._update_knowledge_base()
        learning_results["knowledge_updated"] = knowledge_updates
        
        # Identify performance improvements
        improvements = self._identify_performance_improvements()
        learning_results["performance_improvements"] = improvements
        
        # Update learning metrics
        self.learning_metrics["total_learning_cycles"] += 1
        self.learning_metrics["last_learning_time"] = datetime.now().isoformat()
        
        learning_results["learning_cycle_end"] = datetime.now().isoformat()
        
        return learning_results

    def get_learning_status(self) -> Dict[str, Any]:
        """Get the current learning status."""
        return {
            "learning_metrics": self.learning_metrics,
            "knowledge_base_size": len(self.knowledge_base),
            "learning_patterns_count": len(self.learning_patterns),
            "feedback_history_size": len(self.feedback_history),
            "performance_history_size": len(self.performance_history),
            "recent_learning_results": self._get_recent_learning_results()
        }

    def get_adaptation_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggestions for adapting to the current context."""
        suggestions = []
        
        # Check for relevant learning patterns
        context_hash = self._generate_context_hash(context)
        
        # Suggestions based on feedback patterns
        if "feedback_patterns" in self.learning_patterns:
            patterns = self.learning_patterns["feedback_patterns"]
            for pattern_type, pattern_info in patterns.items():
                if pattern_type == "resource_management" and "resources" in context:
                    suggestions.append({
                        "type": "resource_optimization",
                        "priority": "high",
                        "message": "Apply learned resource optimization patterns",
                        "action": "optimize_resource_allocation",
                        "confidence": pattern_info.get("confidence", 0.7)
                    })
        
        # Suggestions based on performance trends
        if "performance_trends" in self.learning_patterns:
            trends = self.learning_patterns["performance_trends"]
            if "priority_adjustment" in trends:
                suggestions.append({
                    "type": "priority_management",
                    "priority": "medium",
                    "message": "Apply learned priority adjustment strategies",
                    "action": "adjust_priorities_using_learned_strategies",
                    "confidence": trends["priority_adjustment"].get("confidence", 0.6)
                })
        
        # General suggestions based on context
        if "tasks" in context and len(context["tasks"]) > 3:
            suggestions.append({
                "type": "task_management",
                "priority": "medium",
                "message": "Consider parallel execution for multiple tasks",
                "action": "evaluate_parallel_execution",
                "confidence": 0.5
            })
        
        return suggestions

    def _extract_learning_from_feedback(self, feedback: Dict[str, Any]) -> None:
        """Extract learning from feedback."""
        feedback_type = feedback.get("type", "general")
        
        # Store feedback in knowledge base
        feedback_id = self._generate_feedback_id(feedback)
        self.knowledge_base[feedback_id] = {
            "timestamp": datetime.now().isoformat(),
            "feedback_type": feedback_type,
            "feedback_data": feedback,
            "context": feedback.get("context", {})
        }
        
        # Specific learning based on feedback type
        if feedback_type == "priority_adjustment":
            self._learn_from_priority_feedback(feedback)
        elif feedback_type == "resource_management":
            self._learn_from_resource_feedback(feedback)
        elif feedback_type == "performance":
            self._learn_from_performance_feedback(feedback)

    def _learn_from_priority_feedback(self, feedback: Dict[str, Any]) -> None:
        """Learn from priority adjustment feedback."""
        # Extract priority adjustment patterns
        if "adjustments" in feedback:
            adjustments = feedback["adjustments"]
            
            # Simple pattern: track which adjustment reasons are most effective
            reason_effectiveness = defaultdict(int)
            
            for adjustment in adjustments:
                reason = adjustment.get("reason", "unknown")
                effectiveness = adjustment.get("effectiveness", 0)
                
                # Ensure effectiveness is a number before comparison
                try:
                    effectiveness = float(effectiveness)
                except (ValueError, TypeError):
                    effectiveness = 0.0
                
                if effectiveness > 0.5:  # Considered effective
                    reason_effectiveness[reason] += effectiveness
            
            if reason_effectiveness:
                # Store as learned pattern
                if "priority_adjustment" not in self.learning_patterns:
                    self.learning_patterns["priority_adjustment"] = {}
                
                self.learning_patterns["priority_adjustment"]["effective_reasons"] = dict(reason_effectiveness)

    def _learn_from_resource_feedback(self, feedback: Dict[str, Any]) -> None:
        """Learn from resource management feedback."""
        # Extract resource management patterns
        if "resource_usage" in feedback:
            resource_usage = feedback["resource_usage"]
            
            # Simple pattern: track resource contention patterns
            contention_patterns = {}
            
            for resource_id, usage_info in resource_usage.items():
                if usage_info.get("contention", 0) > 0.6:
                    contention_patterns[resource_id] = usage_info.get("contention", 0)
            
            if contention_patterns:
                # Store as learned pattern
                if "resource_management" not in self.learning_patterns:
                    self.learning_patterns["resource_management"] = {}
                
                self.learning_patterns["resource_management"]["high_contention_resources"] = contention_patterns

    def _learn_from_performance_feedback(self, feedback: Dict[str, Any]) -> None:
        """Learn from performance feedback."""
        # Extract performance patterns
        if "metrics" in feedback:
            metrics = feedback["metrics"]
            
            # Simple pattern: track which strategies perform best
            strategy_performance = {}
            
            for strategy, performance in metrics.get("strategy_performance", {}).items():
                if performance.get("success_rate", 0) > 0.7:
                    strategy_performance[strategy] = performance.get("success_rate", 0)
            
            if strategy_performance:
                # Store as learned pattern
                if "performance" not in self.learning_patterns:
                    self.learning_patterns["performance"] = {}
                
                self.learning_patterns["performance"]["effective_strategies"] = strategy_performance

    def _analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in feedback history."""
        if not self.feedback_history:
            return {}
        
        patterns = {}
        
        # Count feedback types
        feedback_types = defaultdict(int)
        for record in self.feedback_history:
            feedback_types[record["feedback_type"]] += 1
        
        patterns["feedback_type_distribution"] = dict(feedback_types)
        
        # Analyze common feedback themes
        common_themes = self._identify_common_feedback_themes()
        if common_themes:
            patterns["common_themes"] = common_themes
        
        return patterns

    def _identify_common_feedback_themes(self) -> List[Dict[str, Any]]:
        """Identify common themes in feedback."""
        themes = defaultdict(int)
        
        for record in self.feedback_history:
            feedback = record["feedback"]
            
            # Simple theme identification
            if "priority" in feedback.get("message", "").lower():
                themes["priority_management"] += 1
            elif "resource" in feedback.get("message", "").lower():
                themes["resource_management"] += 1
            elif "performance" in feedback.get("message", "").lower():
                themes["performance_optimization"] += 1
        
        # Convert to list with confidence scores
        theme_list = []
        total_feedback = len(self.feedback_history)
        
        for theme, count in themes.items():
            confidence = min(1.0, count / max(1, total_feedback))
            theme_list.append({
                "theme": theme,
                "count": count,
                "confidence": confidence
            })
        
        # Sort by confidence
        theme_list.sort(key=lambda x: x["confidence"], reverse=True)
        
        return theme_list

    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze trends in performance history."""
        if not self.performance_history:
            return {}
        
        trends = {}
        
        # Analyze priority adjustment trends
        priority_trends = self._analyze_priority_trends()
        if priority_trends:
            trends["priority_adjustment"] = priority_trends
        
        # Analyze resource usage trends
        resource_trends = self._analyze_resource_trends()
        if resource_trends:
            trends["resource_usage"] = resource_trends
        
        return trends

    def _analyze_priority_trends(self) -> Dict[str, Any]:
        """Analyze trends in priority adjustments."""
        priority_adjustments = []
        
        for record in self.performance_history:
            performance = record["performance"]
            if "priority_adjustments" in performance:
                priority_adjustments.extend(performance["priority_adjustments"])
        
        if not priority_adjustments:
            return {}
        
        # Count adjustment reasons
        reason_counts = defaultdict(int)
        for adjustment in priority_adjustments:
            reason = adjustment.get("reason", "unknown")
            reason_counts[reason] += 1
        
        # Calculate confidence for each reason
        total_adjustments = len(priority_adjustments)
        reason_confidence = {}
        
        for reason, count in reason_counts.items():
            confidence = min(1.0, count / max(1, total_adjustments))
            reason_confidence[reason] = confidence
        
        return {
            "common_reasons": dict(reason_counts),
            "reason_confidence": reason_confidence,
            "total_adjustments": total_adjustments
        }

    def _analyze_resource_trends(self) -> Dict[str, Any]:
        """Analyze trends in resource usage."""
        resource_usage_data = []
        
        for record in self.performance_history:
            performance = record["performance"]
            if "resource_usage" in performance:
                resource_usage_data.append(performance["resource_usage"])
        
        if not resource_usage_data:
            return {}
        
        # Analyze resource contention patterns
        contention_patterns = defaultdict(list)
        
        for usage_data in resource_usage_data:
            for resource_id, usage_info in usage_data.items():
                if "contention" in usage_info:
                    contention_patterns[resource_id].append(usage_info["contention"])
        
        # Calculate average contention for each resource
        resource_contention = {}
        for resource_id, contention_values in contention_patterns.items():
            avg_contention = sum(contention_values) / len(contention_values)
            resource_contention[resource_id] = avg_contention
        
        return {
            "resource_contention": resource_contention,
            "high_contention_resources": [rid for rid, cont in resource_contention.items() if cont > 0.6]
        }

    def _update_knowledge_base(self) -> int:
        """Update the knowledge base with new insights."""
        updates = 0
        
        # Update with recent performance data
        if self.performance_history:
            recent_performance = self.performance_history[-1]["performance"]
            performance_id = self._generate_performance_id(recent_performance)
            
            if performance_id not in self.knowledge_base:
                self.knowledge_base[performance_id] = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "performance",
                    "data": recent_performance
                }
                updates += 1
        
        # Update with recent feedback
        if self.feedback_history:
            recent_feedback = self.feedback_history[-1]["feedback"]
            feedback_id = self._generate_feedback_id(recent_feedback)
            
            if feedback_id not in self.knowledge_base:
                self.knowledge_base[feedback_id] = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "feedback",
                    "data": recent_feedback
                }
                updates += 1
        
        return updates

    def _identify_performance_improvements(self) -> List[Dict[str, Any]]:
        """Identify areas where performance has improved."""
        improvements = []
        
        # Check if we have enough history for comparison
        if len(self.performance_history) >= 2:
            recent = self.performance_history[-1]["performance"]
            previous = self.performance_history[-2]["performance"]
            
            # Compare priority adjustment effectiveness
            if "priority_adjustments" in recent and "priority_adjustments" in previous:
                recent_count = len(recent["priority_adjustments"])
                previous_count = len(previous["priority_adjustments"])
                
                if recent_count > previous_count:
                    improvements.append({
                        "area": "priority_management",
                        "improvement": "increased_adjustments",
                        "value": recent_count - previous_count,
                        "confidence": 0.6
                    })
            
            # Compare resource usage efficiency
            if "resource_usage" in recent and "resource_usage" in previous:
                recent_efficiency = self._calculate_resource_efficiency(recent["resource_usage"])
                previous_efficiency = self._calculate_resource_efficiency(previous["resource_usage"])
                
                if recent_efficiency > previous_efficiency:
                    improvements.append({
                        "area": "resource_management",
                        "improvement": "improved_efficiency",
                        "value": recent_efficiency - previous_efficiency,
                        "confidence": 0.7
                    })
        
        return improvements

    def _calculate_resource_efficiency(self, resource_usage: Dict[str, Any]) -> float:
        """Calculate resource usage efficiency score."""
        if not resource_usage:
            return 0.0
        
        total_resources = len(resource_usage)
        efficiency_score = 0.0
        
        for usage_info in resource_usage.values():
            if isinstance(usage_info, dict):
                # Simple efficiency calculation
                availability = usage_info.get("availability", 1.0)
                contention = usage_info.get("contention", 0)
                
                # Higher efficiency for high availability and low contention
                resource_efficiency = (availability * (1 - contention))
                efficiency_score += resource_efficiency
        
        return efficiency_score / max(1, total_resources)

    def _generate_context_hash(self, context: Dict[str, Any]) -> str:
        """Generate a hash for context data."""
        import hashlib
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _generate_feedback_id(self, feedback: Dict[str, Any]) -> str:
        """Generate a unique ID for feedback."""
        import hashlib
        try:
            # Convert feedback to a JSON-serializable format
            serializable_feedback = self._make_feedback_serializable(feedback)
            feedback_str = json.dumps(serializable_feedback, sort_keys=True)
            return hashlib.md5(feedback_str.encode()).hexdigest()
        except Exception as e:
            # Fallback hash if serialization fails
            self._log_error(f"Failed to generate feedback ID: {str(e)}")
            return hashlib.md5(str(feedback).encode()).hexdigest()

    def _make_feedback_serializable(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Convert feedback to a JSON-serializable format."""
        if feedback is None:
            return {}
        
        serializable_feedback = {}
        for key, value in feedback.items():
            try:
                if isinstance(value, (str, int, float, bool)) or value is None:
                    serializable_feedback[key] = value
                elif isinstance(value, (list, tuple)):
                    serializable_feedback[key] = [self._make_value_serializable(item) for item in value]
                elif isinstance(value, dict):
                    serializable_feedback[key] = self._make_feedback_serializable(value)
                else:
                    # Convert other objects to string representation
                    serializable_feedback[key] = str(value)
            except Exception:
                # If conversion fails, store as string
                serializable_feedback[key] = str(value)
        
        return serializable_feedback

    def _make_value_serializable(self, value: Any) -> Any:
        """Convert a single value to a JSON-serializable format."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        elif isinstance(value, (list, tuple)):
            return [self._make_value_serializable(item) for item in value]
        elif isinstance(value, dict):
            return self._make_feedback_serializable(value)
        else:
            return str(value)

    def _generate_performance_id(self, performance: Dict[str, Any]) -> str:
        """Generate a unique ID for performance data."""
        import hashlib
        performance_str = json.dumps(performance, sort_keys=True)
        return hashlib.md5(performance_str.encode()).hexdigest()

    def _get_recent_learning_results(self) -> Optional[Dict[str, Any]]:
        """Get recent learning results if available."""
        # In a real implementation, this would return actual learning results
        # For now, return a placeholder
        return {
            "last_learning_cycle": self.learning_metrics.get("last_learning_time"),
            "patterns_learned": len(self.learning_patterns),
            "knowledge_gained": len(self.knowledge_base)
        }


class defaultdict:
    """Simple defaultdict implementation for compatibility."""
    
    def __init__(self, default_type=None):
        self.default_type = default_type
        self.data = {}
    
    def __getitem__(self, key):
        if key not in self.data:
            if self.default_type == int:
                self.data[key] = 0
            elif self.default_type == list:
                self.data[key] = []
            elif self.default_type == dict:
                self.data[key] = {}
            else:
                self.data[key] = self.default_type() if self.default_type else None
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def items(self):
        return self.data.items()
    
    def keys(self):
        return self.data.keys()
    
    def values(self):
        return self.data.values()