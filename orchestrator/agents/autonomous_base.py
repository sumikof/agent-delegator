"""Autonomous agent base class with enhanced decision-making capabilities.

This class extends the basic Agent class with autonomous decision-making,
context understanding, and dynamic priority management capabilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import hashlib

from .base import Agent


class AutonomousAgent(Agent):
    """Autonomous agent base class with enhanced capabilities.
    
    This agent can make autonomous decisions based on context understanding,
    dynamic priority management, and learning from past experiences.
    """

    def __init__(self, agent_id: str, name: str | None = None) -> None:
        super().__init__(agent_id, name)
        self.context_memory = []  # Memory of past contexts and decisions
        self.learning_data = {}   # Data for learning and adaptation
        self.priority_strategy = "default"  # Current priority strategy
        self.decision_log = []    # Log of decisions made

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's logic with autonomous decision-making.
        
        Args:
            context: Arbitrary data passed from previous agents or the orchestrator.
            
        Returns:
            A dictionary matching the common response schema with enhanced autonomy.
        """
        # Store context in memory for learning
        self._store_context(context)
        
        # Analyze context and make autonomous decisions
        decisions = self._make_autonomous_decisions(context)
        
        # Apply dynamic priority management
        updated_context = self._apply_dynamic_priority(context)
        
        # Generate response with autonomy information
        response = {
            "status": "OK",
            "summary": f"{self.name} executed autonomously",
            "findings": [],
            "artifacts": [],
            "next_actions": [],
            "context": updated_context,
            "trace_id": self._generate_trace_id(context),
            "execution_time_ms": 0,
            "autonomy_info": {
                "decisions_made": decisions,
                "priority_strategy": self.priority_strategy,
                "learning_data_used": len(self.learning_data),
                "context_understanding": self._analyze_context_complexity(context)
            }
        }
        
        return response

    def _store_context(self, context: Dict[str, Any]) -> None:
        """Store context information for future learning and decision-making."""
        context_hash = self._generate_context_hash(context)
        
        context_record = {
            "timestamp": datetime.now().isoformat(),
            "context_hash": context_hash,
            "context_data": context,
            "context_type": self._determine_context_type(context)
        }
        
        self.context_memory.append(context_record)
        
        # Keep memory size manageable
        if len(self.context_memory) > 100:
            self.context_memory = self.context_memory[-100:]

    def _make_autonomous_decisions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Make autonomous decisions based on context analysis."""
        decisions = []
        
        # Analyze context complexity
        complexity = self._analyze_context_complexity(context)
        
        # Make decisions based on context
        if complexity > 0.7:  # High complexity
            decisions.append({
                "decision_type": "context_analysis",
                "decision": "high_complexity_detected",
                "reason": f"Context complexity score: {complexity:.2f}",
                "action": "apply_advanced_analysis"
            })
        
        # Check for resource constraints
        if self._detect_resource_constraints(context):
            decisions.append({
                "decision_type": "resource_management",
                "decision": "resource_constraints_detected",
                "reason": "Potential resource constraints identified",
                "action": "optimize_resource_allocation"
            })
        
        # Add decision to log
        for decision in decisions:
            self.decision_log.append({
                "timestamp": datetime.now().isoformat(),
                "decision": decision,
                "context_hash": self._generate_context_hash(context)
            })
        
        return decisions

    def _apply_dynamic_priority(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply dynamic priority management to the context."""
        updated_context = context.copy()
        
        # Check if priority information exists in context
        if "tasks" in context and isinstance(context["tasks"], list):
            updated_tasks = []
            
            for task in context["tasks"]:
                updated_task = task.copy()
                
                # Apply dynamic priority based on task characteristics
                if "priority" in updated_task:
                    original_priority = updated_task["priority"]
                    adjusted_priority = self._calculate_dynamic_priority(updated_task)
                    
                    if adjusted_priority != original_priority:
                        updated_task["priority"] = adjusted_priority
                        updated_task["priority_adjusted"] = True
                        updated_task["priority_reason"] = "dynamic_adjustment"
                
                updated_tasks.append(updated_task)
            
            updated_context["tasks"] = updated_tasks
        
        return updated_context

    def _calculate_dynamic_priority(self, task: Dict[str, Any]) -> int:
        """Calculate dynamic priority for a task."""
        # Default priority strategy
        if self.priority_strategy == "default":
            # Simple strategy: prioritize tasks with dependencies
            if task.get("dependencies", []):
                return min(10, task.get("priority", 5) + 2)
            else:
                return task.get("priority", 5)
        
        # More advanced strategies could be implemented here
        return task.get("priority", 5)

    def _analyze_context_complexity(self, context: Dict[str, Any]) -> float:
        """Analyze the complexity of the given context with improved error handling."""
        try:
            if not isinstance(context, dict):
                return 0.0
                
            complexity_score = 0.0
            
            # Add score based on number of keys
            try:
                complexity_score += min(1.0, len(context) / 20)
            except Exception:
                complexity_score += 0.1  # Default small score for invalid context
                
            # Add score based on nested structures
            try:
                for key, value in context.items():
                    try:
                        if isinstance(value, dict):
                            complexity_score += min(0.5, len(value) / 10)
                        elif isinstance(value, list):
                            complexity_score += min(0.5, len(value) / 10)
                    except Exception:
                        # Skip invalid nested structures
                        continue
            except Exception:
                # Skip if context iteration fails
                pass
                
            # Add score for complex data types
            try:
                complex_types = 0
                for value in context.values():
                    if isinstance(value, (dict, list)):
                        complex_types += 1
                complexity_score += min(0.3, complex_types / 5)
            except Exception:
                pass
                
            return min(1.0, complexity_score)
            
        except Exception as e:
            # Log error and return default complexity
            self._log_error(f"Error analyzing context complexity: {str(e)}")
            return 0.3  # Default medium complexity

    def _detect_resource_constraints(self, context: Dict[str, Any]) -> bool:
        """Detect potential resource constraints in the context."""
        try:
            # Check for resource-related information
            if "resources" in context:
                resources = context["resources"]
                
                if isinstance(resources, dict):
                    for resource_name, resource_info in resources.items():
                        if isinstance(resource_info, dict):
                            # Check for low availability
                            try:
                                availability = float(resource_info.get("availability", 1.0))
                                if availability < 0.3:
                                    return True
                            except (ValueError, TypeError):
                                # Handle invalid availability values
                                continue
                                
                            # Check for high contention
                            try:
                                contention = float(resource_info.get("contention", 0))
                                if contention > 0.7:
                                    return True
                            except (ValueError, TypeError):
                                # Handle invalid contention values
                                continue
                                
                            # Check for resource limits
                            try:
                                current_usage = int(resource_info.get("current_usage", 0))
                                max_capacity = int(resource_info.get("max_capacity", 100))
                                if max_capacity > 0 and current_usage / max_capacity > 0.8:
                                    return True
                            except (ValueError, TypeError, ZeroDivisionError):
                                # Handle invalid resource capacity values
                                continue
        except Exception as e:
            # Log error but continue execution
            self._log_error(f"Error detecting resource constraints: {str(e)}")
            return False
        
        return False

    def _determine_context_type(self, context: Dict[str, Any]) -> str:
        """Determine the type of context based on its content."""
        if "tasks" in context:
            return "task_management"
        elif "resources" in context:
            return "resource_management"
        elif "workflow" in context:
            return "workflow_coordination"
        else:
            return "general"

    def _generate_context_hash(self, context: Dict[str, Any]) -> str:
        """Generate a hash for the context to use as an identifier."""
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _generate_trace_id(self, context: Dict[str, Any]) -> str:
        """Generate a trace ID for this execution."""
        timestamp = datetime.now().isoformat()
        context_hash = self._generate_context_hash(context)
        return f"{self.id}-{timestamp}-{context_hash[:8]}"

    def _log_error(self, error_message: str) -> None:
        """Log an error message for debugging and monitoring."""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": "autonomy_error",
            "message": error_message,
            "agent_id": self.id,
            "agent_name": self.name
        }
        
        # Add to decision log for tracking
        self.decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "decision_type": "error_handling",
            "error_message": error_message,
            "severity": "warning"
        })

    def learn_from_experience(self, feedback: Dict[str, Any]) -> None:
        """Learn from feedback and past experiences."""
        # Store feedback in learning data
        feedback_id = self._generate_context_hash(feedback)
        self.learning_data[feedback_id] = feedback
        
        # Update priority strategy based on feedback
        if "priority_strategy" in feedback:
            self.priority_strategy = feedback["priority_strategy"]

    def get_autonomy_status(self) -> Dict[str, Any]:
        """Get the current autonomy status of the agent."""
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "priority_strategy": self.priority_strategy,
            "memory_size": len(self.context_memory),
            "learning_data_size": len(self.learning_data),
            "decisions_made": len(self.decision_log),
            "autonomy_level": self._calculate_autonomy_level()
        }

    def _calculate_autonomy_level(self) -> float:
        """Calculate the current autonomy level of the agent."""
        # Simple autonomy level calculation
        autonomy_score = 0.0
        
        # Add score based on memory
        autonomy_score += min(0.3, len(self.context_memory) / 100)
        
        # Add score based on learning data
        autonomy_score += min(0.3, len(self.learning_data) / 50)
        
        # Add score based on decisions made
        autonomy_score += min(0.4, len(self.decision_log) / 20)
        
        return min(1.0, autonomy_score)

    def can_handle_coordination(self) -> bool:
        """Check if this agent can handle coordination requests."""
        # Autonomous agents can handle coordination
        return True

    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages with enhanced autonomous capabilities."""
        message_type = message.get("message_type")
        payload = message.get("payload", {})
        
        if message_type == "coordination_request":
            # Handle coordination requests with autonomous decision-making
            return self._handle_coordination_request(payload)
        elif message_type == "feedback":
            # Handle feedback for learning
            self.learn_from_experience(payload)
            return {
                "status": "processed",
                "message": "Feedback processed for learning"
            }
        elif message_type == "autonomy_query":
            # Handle autonomy status queries
            return {
                "status": "success",
                "autonomy_status": self.get_autonomy_status()
            }
        
        return super().receive_message(message)

    def _handle_coordination_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle coordination requests with autonomous decision-making."""
        conflict_type = payload.get("conflict_type")
        
        if conflict_type == "resource_conflict":
            return self._handle_resource_conflict_autonomous(payload)
        elif conflict_type == "priority_conflict":
            return self._handle_priority_conflict_autonomous(payload)
        elif conflict_type == "task_dependency":
            return self._handle_task_dependency_conflict(payload)
        else:
            # Default autonomous handling
            decision = self._make_autonomous_coordination_decision(payload)
            return {
                "status": "resolved",
                "decision": decision,
                "message": "Coordination request resolved autonomously"
            }

    def _handle_resource_conflict_autonomous(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource conflicts with autonomous decision-making."""
        resource_id = payload.get("resource_id")
        requesting_task = payload.get("requesting_task_id")
        conflicting_task = payload.get("conflicting_task_id")
        
        # Make autonomous decision based on task priorities and resource availability
        decision = "allow_higher_priority"
        
        # Store decision for learning
        self.decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "decision_type": "resource_conflict",
            "resource_id": resource_id,
            "requesting_task": requesting_task,
            "conflicting_task": conflicting_task,
            "decision": decision
        })
        
        return {
            "status": "resolved",
            "decision": decision,
            "resource_id": resource_id,
            "message": f"Resource conflict resolved autonomously for resource {resource_id}",
            "autonomy_info": {
                "decision_reason": "priority_based",
                "confidence": 0.85
            }
        }

    def _handle_priority_conflict_autonomous(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle priority conflicts with autonomous decision-making."""
        involved_tasks = payload.get("involved_tasks", [])
        
        # Make autonomous decision based on task characteristics
        decision = "maintain_current_priorities"
        
        # Analyze tasks to make better decision
        if len(involved_tasks) >= 2:
            # Simple analysis: check if tasks have dependencies
            task_info = []
            for task_id in involved_tasks:
                task_info.append({
                    "task_id": task_id,
                    "has_dependencies": self._task_has_dependencies(task_id)
                })
            
            # If one task has dependencies, prioritize it
            tasks_with_deps = [t for t in task_info if t["has_dependencies"]]
            if tasks_with_deps:
                decision = "prioritize_tasks_with_dependencies"
        
        return {
            "status": "resolved",
            "decision": decision,
            "involved_tasks": involved_tasks,
            "message": f"Priority conflict resolved autonomously for tasks {involved_tasks}",
            "autonomy_info": {
                "decision_reason": "dependency_analysis",
                "confidence": 0.75,
                "task_analysis": task_info
            }
        }

    def _handle_task_dependency_conflict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task dependency conflicts."""
        dependent_task = payload.get("dependent_task")
        dependency_task = payload.get("dependency_task")
        
        # Autonomous decision: ensure dependencies are resolved first
        decision = "resolve_dependency_first"
        
        return {
            "status": "resolved",
            "decision": decision,
            "dependent_task": dependent_task,
            "dependency_task": dependency_task,
            "message": f"Task dependency conflict resolved: {dependency_task} should be completed before {dependent_task}",
            "autonomy_info": {
                "decision_reason": "dependency_resolution",
                "confidence": 0.90
            }
        }

    def _make_autonomous_coordination_decision(self, payload: Dict[str, Any]) -> str:
        """Make autonomous decisions for coordination requests."""
        # Default decision
        return "continue_with_current_plan"

    def _task_has_dependencies(self, task_id: str) -> bool:
        """Check if a task has dependencies with improved error handling."""
        try:
            # Check memory for task information
            for context_record in self.context_memory:
                try:
                    context_data = context_record["context_data"]
                    if "tasks" in context_data and isinstance(context_data["tasks"], list):
                        for task in context_data["tasks"]:
                            try:
                                if task.get("id") == task_id and task.get("dependencies"):
                                    # Check if dependencies is a non-empty list
                                    dependencies = task.get("dependencies", [])
                                    if isinstance(dependencies, list) and len(dependencies) > 0:
                                        return True
                            except Exception:
                                # Skip invalid task entries
                                continue
                except Exception:
                    # Skip invalid context records
                    continue
        except Exception as e:
            # Log error but continue execution
            self._log_error(f"Error checking task dependencies: {str(e)}")
            return False
        
        return False