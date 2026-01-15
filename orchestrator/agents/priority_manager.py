"""Dynamic priority management module for autonomous agents.

This module provides advanced priority management capabilities for autonomous
agents to dynamically adjust task priorities based on various factors.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import math


class PriorityManager:
    """Dynamic priority management engine."""

    def __init__(self) -> None:
        self.priority_strategies = {
            "default": self._default_priority_strategy,
            "dependency_aware": self._dependency_aware_strategy,
            "resource_aware": self._resource_aware_strategy,
            "deadline_aware": self._deadline_aware_strategy,
            "balanced": self._balanced_strategy
        }
        self.current_strategy = "default"
        self.priority_history = []  # History of priority adjustments
        self.learning_data = {}     # Data for learning priority patterns

    def calculate_priorities(self, tasks: List[Dict[str, Any]], context: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """Calculate dynamic priorities for tasks."""
        if not tasks:
            return []
        
        # Use the current strategy
        strategy = self.priority_strategies.get(self.current_strategy, self._default_priority_strategy)
        
        # Calculate priorities using the selected strategy
        prioritized_tasks = strategy(tasks, context or {})
        
        # Log the priority adjustments
        self._log_priority_adjustments(tasks, prioritized_tasks, context or {})
        
        return prioritized_tasks

    def set_strategy(self, strategy_name: str) -> bool:
        """Set the current priority strategy."""
        if strategy_name in self.priority_strategies:
            self.current_strategy = strategy_name
            return True
        return False

    def get_available_strategies(self) -> List[str]:
        """Get the list of available priority strategies."""
        return list(self.priority_strategies.keys())

    def _default_priority_strategy(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Default priority strategy - simple priority adjustment."""
        prioritized_tasks = []
        
        for task in tasks:
            prioritized_task = task.copy()
            
            # Simple adjustment: increase priority for tasks with dependencies
            if "dependencies" in prioritized_task and prioritized_task["dependencies"]:
                original_priority = prioritized_task.get("priority", 5)
                prioritized_task["priority"] = min(10, original_priority + 1)
                prioritized_task["priority_adjusted"] = True
                prioritized_task["priority_reason"] = "has_dependencies"
            
            prioritized_tasks.append(prioritized_task)
        
        return prioritized_tasks

    def _dependency_aware_strategy(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Dependency-aware priority strategy."""
        prioritized_tasks = []
        task_map = {task["id"]: task.copy() for task in tasks}
        
        # First pass: calculate dependency scores
        for task_id, task in task_map.items():
            dependency_score = self._calculate_dependency_score(task, task_map)
            task["dependency_score"] = dependency_score
        
        # Second pass: adjust priorities based on dependency scores
        for task_id, task in task_map.items():
            original_priority = task.get("priority", 5)
            dependency_score = task.get("dependency_score", 0)
            
            # Adjust priority based on dependency score
            priority_adjustment = math.ceil(dependency_score * 2)
            new_priority = min(10, max(1, original_priority + priority_adjustment))
            
            task["priority"] = new_priority
            task["priority_adjusted"] = priority_adjustment != 0
            task["priority_reason"] = f"dependency_score_{dependency_score:.1f}"
            
            prioritized_tasks.append(task)
        
        return prioritized_tasks

    def _resource_aware_strategy(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Resource-aware priority strategy."""
        prioritized_tasks = []
        
        # Get resource information from context
        resources = context.get("resources", {})
        
        for task in tasks:
            prioritized_task = task.copy()
            
            # Check if task requires resources
            if "required_resources" in prioritized_task:
                resource_score = 0
                required_resources = prioritized_task["required_resources"]
                
                for resource_id in required_resources:
                    if resource_id in resources:
                        resource_info = resources[resource_id]
                        availability = resource_info.get("availability", 1.0)
                        contention = resource_info.get("contention", 0)
                        
                        # Higher priority for tasks requiring scarce resources
                        if availability < 0.5:
                            resource_score += (0.5 - availability) * 2
                        
                        # Higher priority for tasks requiring high-contention resources
                        if contention > 0.5:
                            resource_score += (contention - 0.5) * 2
                
                # Adjust priority based on resource score
                if resource_score > 0:
                    original_priority = prioritized_task.get("priority", 5)
                    priority_adjustment = math.floor(resource_score * 3)
                    new_priority = min(10, original_priority + priority_adjustment)
                    
                    prioritized_task["priority"] = new_priority
                    prioritized_task["priority_adjusted"] = True
                    prioritized_task["priority_reason"] = f"resource_score_{resource_score:.1f}"
            
            prioritized_tasks.append(prioritized_task)
        
        return prioritized_tasks

    def _deadline_aware_strategy(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Deadline-aware priority strategy."""
        prioritized_tasks = []
        current_time = datetime.now()
        
        for task in tasks:
            prioritized_task = task.copy()
            
            # Check if task has a deadline
            if "deadline" in prioritized_task:
                try:
                    deadline = datetime.fromisoformat(prioritized_task["deadline"])
                    time_remaining = (deadline - current_time).total_seconds()
                    
                    if time_remaining > 0:
                        # Calculate urgency score (higher urgency = higher priority)
                        urgency_score = max(0, 1 - (time_remaining / (24 * 3600 * 7)))  # 1 week reference
                        
                        # Adjust priority based on urgency
                        original_priority = prioritized_task.get("priority", 5)
                        priority_adjustment = math.floor(urgency_score * 4)
                        new_priority = min(10, original_priority + priority_adjustment)
                        
                        prioritized_task["priority"] = new_priority
                        prioritized_task["priority_adjusted"] = priority_adjustment != 0
                        prioritized_task["priority_reason"] = f"urgency_score_{urgency_score:.1f}"
                        prioritized_task["time_remaining_hours"] = time_remaining / 3600
                except (ValueError, TypeError):
                    # Invalid deadline format, skip adjustment
                    pass
            
            prioritized_tasks.append(prioritized_task)
        
        return prioritized_tasks

    def _balanced_strategy(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Balanced priority strategy combining multiple factors."""
        prioritized_tasks = []
        task_map = {task["id"]: task.copy() for task in tasks}
        
        # Calculate multiple scores for each task
        for task_id, task in task_map.items():
            # Calculate individual scores
            dependency_score = self._calculate_dependency_score(task, task_map)
            resource_score = self._calculate_resource_score(task, context)
            urgency_score = self._calculate_urgency_score(task)
            
            # Combine scores with weights
            combined_score = (
                dependency_score * 0.4 +
                resource_score * 0.3 +
                urgency_score * 0.3
            )
            
            task["priority_scores"] = {
                "dependency": dependency_score,
                "resource": resource_score,
                "urgency": urgency_score,
                "combined": combined_score
            }
            
            # Adjust priority based on combined score
            original_priority = task.get("priority", 5)
            priority_adjustment = math.floor(combined_score * 3)
            new_priority = min(10, max(1, original_priority + priority_adjustment))
            
            task["priority"] = new_priority
            task["priority_adjusted"] = priority_adjustment != 0
            task["priority_reason"] = f"balanced_score_{combined_score:.1f}"
        
        # Convert back to list
        prioritized_tasks = list(task_map.values())
        
        return prioritized_tasks

    def _calculate_dependency_score(self, task: Dict[str, Any], task_map: Dict[str, Dict[str, Any]]) -> float:
        """Calculate dependency score for a task."""
        score = 0.0
        
        # Score based on number of dependencies
        dependencies = task.get("dependencies", [])
        score += min(0.5, len(dependencies) * 0.2)
        
        # Score based on dependency complexity
        for dep_id in dependencies:
            if dep_id in task_map:
                dep_task = task_map[dep_id]
                # Tasks depending on high-priority tasks get higher score
                dep_priority = dep_task.get("priority", 5)
                score += min(0.3, (dep_priority / 10) * 0.3)
        
        # Score based on being a dependency for other tasks
        dependent_tasks = []
        for other_task_id, other_task in task_map.items():
            if task["id"] in other_task.get("dependencies", []):
                dependent_tasks.append(other_task_id)
        
        score += min(0.4, len(dependent_tasks) * 0.2)
        
        return min(1.0, score)

    def _calculate_resource_score(self, task: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate resource score for a task."""
        score = 0.0
        
        # Check if task requires resources
        if "required_resources" in task:
            resources = context.get("resources", {})
            required_resources = task["required_resources"]
            
            for resource_id in required_resources:
                if resource_id in resources:
                    resource_info = resources[resource_id]
                    availability = resource_info.get("availability", 1.0)
                    contention = resource_info.get("contention", 0)
                    
                    # Higher score for scarce resources
                    if availability < 0.7:
                        score += min(0.4, (0.7 - availability) * 1.5)
                    
                    # Higher score for high-contention resources
                    if contention > 0.5:
                        score += min(0.3, (contention - 0.5) * 1.2)
        
        return min(1.0, score)

    def _calculate_urgency_score(self, task: Dict[str, Any]) -> float:
        """Calculate urgency score for a task."""
        score = 0.0
        
        # Check if task has a deadline
        if "deadline" in task:
            try:
                deadline = datetime.fromisoformat(task["deadline"])
                current_time = datetime.now()
                time_remaining = (deadline - current_time).total_seconds()
                
                if time_remaining > 0:
                    # Higher urgency for tasks with less time remaining
                    # Use logarithmic scale to avoid extreme values
                    hours_remaining = time_remaining / 3600
                    urgency_factor = max(0, 1 - (math.log10(hours_remaining + 1) / 3))  # Normalize
                    score = min(1.0, urgency_factor)
            except (ValueError, TypeError):
                # Invalid deadline format
                pass
        
        return score

    def _log_priority_adjustments(self, original_tasks: List[Dict[str, Any]], adjusted_tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
        """Log priority adjustments for learning and analysis."""
        adjustments = []
        
        for orig_task, adj_task in zip(original_tasks, adjusted_tasks):
            if orig_task.get("priority") != adj_task.get("priority"):
                adjustment = {
                    "timestamp": datetime.now().isoformat(),
                    "task_id": adj_task.get("id"),
                    "original_priority": orig_task.get("priority"),
                    "new_priority": adj_task.get("priority"),
                    "adjustment_reason": adj_task.get("priority_reason", "unknown"),
                    "strategy": self.current_strategy,
                    "context_info": self._get_context_summary(context)
                }
                adjustments.append(adjustment)
        
        if adjustments:
            self.priority_history.extend(adjustments)
            
            # Keep history size manageable
            if len(self.priority_history) > 100:
                self.priority_history = self.priority_history[-100:]

    def _get_context_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the context for logging."""
        return {
            "context_size": len(context),
            "has_resources": "resources" in context,
            "has_workflow": "workflow" in context,
            "task_count": len(context.get("tasks", []))
        }

    def learn_from_adjustments(self) -> None:
        """Learn from past priority adjustments to improve future decisions."""
        if not self.priority_history:
            return
        
        # Analyze adjustment patterns
        strategy_effectiveness = {}
        reason_distribution = Counter()
        
        for adjustment in self.priority_history:
            strategy = adjustment["strategy"]
            reason = adjustment["adjustment_reason"]
            
            # Track strategy effectiveness (simple metric: number of adjustments)
            strategy_effectiveness[strategy] = strategy_effectiveness.get(strategy, 0) + 1
            
            # Track reason distribution
            reason_distribution[reason] += 1
        
        # Store learning data
        self.learning_data["strategy_effectiveness"] = strategy_effectiveness
        self.learning_data["reason_distribution"] = dict(reason_distribution)
        self.learning_data["last_learning_time"] = datetime.now().isoformat()

    def get_priority_insights(self) -> Dict[str, Any]:
        """Get insights about priority management."""
        insights = {
            "current_strategy": self.current_strategy,
            "available_strategies": self.get_available_strategies(),
            "adjustment_history": len(self.priority_history),
            "learning_data": self.learning_data.copy()
        }
        
        if self.priority_history:
            insights["recent_adjustments"] = self.priority_history[-5:]
        
        return insights

    def suggest_strategy(self, context: Dict[str, Any]) -> str:
        """Suggest an appropriate priority strategy based on context."""
        # Default strategy
        suggested_strategy = "default"
        
        # Analyze context to suggest strategy
        if "resources" in context and len(context["resources"]) > 3:
            suggested_strategy = "resource_aware"
        elif "tasks" in context:
            tasks = context["tasks"]
            if any("dependencies" in task and task["dependencies"] for task in tasks):
                suggested_strategy = "dependency_aware"
            elif any("deadline" in task for task in tasks):
                suggested_strategy = "deadline_aware"
            elif len(tasks) > 5:
                suggested_strategy = "balanced"
        
        return suggested_strategy

    def get_strategy_description(self, strategy_name: str) -> str:
        """Get description of a priority strategy."""
        descriptions = {
            "default": "Simple priority adjustment based on basic task characteristics",
            "dependency_aware": "Priority adjustment considering task dependencies and relationships",
            "resource_aware": "Priority adjustment based on resource availability and contention",
            "deadline_aware": "Priority adjustment focusing on task deadlines and urgency",
            "balanced": "Comprehensive priority adjustment considering multiple factors"
        }
        
        return descriptions.get(strategy_name, "Unknown strategy")


class Counter:
    """Simple counter class for compatibility."""
    
    def __init__(self) -> None:
        self.counter = {}
    
    def __getitem__(self, key):
        return self.counter.get(key, 0)
    
    def __setitem__(self, key, value):
        self.counter[key] = value
    
    def get(self, key, default=0):
        return self.counter.get(key, default)
    
    def update(self, other):
        if isinstance(other, dict):
            for key, value in other.items():
                self.counter[key] = self.counter.get(key, 0) + value
        elif isinstance(other, Counter):
            for key, value in other.counter.items():
                self.counter[key] = self.counter.get(key, 0) + value
    
    def most_common(self, n=None):
        items = list(self.counter.items())
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:n] if n is not None else items