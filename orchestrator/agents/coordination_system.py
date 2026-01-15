"""Coordination system for autonomous agents.

This module provides advanced coordination capabilities for autonomous
agents to work together effectively and resolve conflicts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import math
from collections import defaultdict


class CoordinationSystem:
    """Coordination system for autonomous agents."""

    def __init__(self) -> None:
        self.coordination_history = []  # History of coordination events
        self.conflict_resolution_strategies = {
            "resource_conflict": self._resolve_resource_conflict,
            "priority_conflict": self._resolve_priority_conflict,
            "task_dependency": self._resolve_task_dependency,
            "agent_coordination": self._resolve_agent_coordination
        }
        self.negotiation_protocols = {
            "resource_allocation": self._negotiate_resource_allocation,
            "task_prioritization": self._negotiate_task_prioritization,
            "workflow_coordination": self._negotiate_workflow_coordination
        }
        self.coordination_metrics = {
            "total_coordination_events": 0,
            "successful_resolutions": 0,
            "conflict_types": defaultdict(int)
        }

    def handle_coordination_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a coordination request from an agent."""
        # Log the coordination request
        self._log_coordination_request(request)
        
        # Determine the type of coordination needed
        conflict_type = request.get("conflict_type")
        
        # Use appropriate resolution strategy
        if conflict_type in self.conflict_resolution_strategies:
            resolution = self.conflict_resolution_strategies[conflict_type](request)
            
            # Log successful resolution
            self._log_successful_resolution(request, resolution)
            
            return resolution
        else:
            # Default resolution for unknown conflict types
            return self._default_conflict_resolution(request)

    def initiate_negotiation(self, negotiation_type: str, participants: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a negotiation process between agents."""
        if negotiation_type not in self.negotiation_protocols:
            return {
                "status": "error",
                "message": f"Unknown negotiation type: {negotiation_type}"
            }
        
        # Prepare negotiation context
        negotiation_context = {
            "negotiation_type": negotiation_type,
            "participants": participants,
            "context": context,
            "start_time": datetime.now().isoformat(),
            "status": "initiated"
        }
        
        # Execute negotiation protocol
        result = self.negotiation_protocols[negotiation_type](negotiation_context)
        
        # Log negotiation result
        self._log_negotiation_result(negotiation_context, result)
        
        return result

    def _resolve_resource_conflict(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve resource conflicts between agents."""
        resource_id = request.get("resource_id")
        requesting_agent = request.get("requesting_agent")
        conflicting_agent = request.get("conflicting_agent")
        
        # Get resource information
        resource_info = request.get("resource_info", {})
        
        # Determine resolution strategy based on resource characteristics
        if resource_info.get("availability", 1.0) < 0.3:
            # Low availability: prioritize based on task urgency
            resolution = self._resolve_low_availability_conflict(request)
        elif resource_info.get("contention", 0) > 0.7:
            # High contention: use fair allocation strategy
            resolution = self._resolve_high_contention_conflict(request)
        else:
            # Normal case: prioritize based on task characteristics
            resolution = self._resolve_normal_resource_conflict(request)
        
        return resolution

    def _resolve_low_availability_conflict(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts for resources with low availability."""
        # Prioritize tasks with higher urgency and dependencies
        task1 = request.get("requesting_task", {})
        task2 = request.get("conflicting_task", {})
        
        # Calculate priority scores
        score1 = self._calculate_task_priority_score(task1)
        score2 = self._calculate_task_priority_score(task2)
        
        if score1 > score2:
            decision = "allocate_to_requesting_agent"
            winner = request.get("requesting_agent")
            loser = request.get("conflicting_agent")
        else:
            decision = "allocate_to_conflicting_agent"
            winner = request.get("conflicting_agent")
            loser = request.get("requesting_agent")
        
        return {
            "status": "resolved",
            "conflict_type": "resource_conflict",
            "resource_id": request.get("resource_id"),
            "decision": decision,
            "winner": winner,
            "loser": loser,
            "resolution_strategy": "urgency_based",
            "priority_scores": {
                "requesting_task": score1,
                "conflicting_task": score2
            },
            "message": f"Resource {request.get('resource_id')} allocated based on task urgency"
        }

    def _resolve_high_contention_conflict(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts for resources with high contention."""
        # Use fair allocation with time-sharing
        resource_id = request.get("resource_id")
        
        return {
            "status": "resolved",
            "conflict_type": "resource_conflict",
            "resource_id": resource_id,
            "decision": "time_sharing_allocation",
            "allocation_plan": {
                "requesting_agent": {
                    "allocation": 0.5,
                    "time_slots": ["morning", "evening"]
                },
                "conflicting_agent": {
                    "allocation": 0.5,
                    "time_slots": ["afternoon", "night"]
                }
            },
            "resolution_strategy": "fair_sharing",
            "message": f"Resource {resource_id} allocated using time-sharing for fair access"
        }

    def _resolve_normal_resource_conflict(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve normal resource conflicts."""
        # Simple priority-based resolution
        task1_priority = request.get("requesting_task", {}).get("priority", 5)
        task2_priority = request.get("conflicting_task", {}).get("priority", 5)
        
        if task1_priority > task2_priority:
            decision = "allocate_to_requesting_agent"
        elif task2_priority > task1_priority:
            decision = "allocate_to_conflicting_agent"
        else:
            decision = "share_resource"
        
        return {
            "status": "resolved",
            "conflict_type": "resource_conflict",
            "resource_id": request.get("resource_id"),
            "decision": decision,
            "resolution_strategy": "priority_based",
            "message": f"Resource {request.get('resource_id')} allocated based on task priorities"
        }

    def _resolve_priority_conflict(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve priority conflicts between tasks."""
        involved_tasks = request.get("involved_tasks", [])
        
        if len(involved_tasks) < 2:
            return {
                "status": "resolved",
                "conflict_type": "priority_conflict",
                "decision": "no_conflict",
                "message": "No priority conflict detected"
            }
        
        # Analyze task characteristics
        task_analysis = []
        for task_id in involved_tasks:
            task_info = request.get(f"task_{task_id}", {})
            analysis = {
                "task_id": task_id,
                "priority": task_info.get("priority", 5),
                "dependencies": len(task_info.get("dependencies", [])),
                "has_deadline": "deadline" in task_info,
                "priority_score": self._calculate_task_priority_score(task_info)
            }
            task_analysis.append(analysis)
        
        # Determine resolution based on analysis
        if any(t["has_deadline"] for t in task_analysis):
            # Prioritize tasks with deadlines
            deadline_tasks = [t for t in task_analysis if t["has_deadline"]]
            highest_priority_deadline_task = max(deadline_tasks, key=lambda x: x["priority_score"])
            
            return {
                "status": "resolved",
                "conflict_type": "priority_conflict",
                "decision": "prioritize_deadline_tasks",
                "priority_task": highest_priority_deadline_task["task_id"],
                "task_analysis": task_analysis,
                "resolution_strategy": "deadline_aware",
                "message": "Priority conflict resolved by prioritizing tasks with deadlines"
            }
        else:
            # Use overall priority scores
            highest_priority_task = max(task_analysis, key=lambda x: x["priority_score"])
            
            return {
                "status": "resolved",
                "conflict_type": "priority_conflict",
                "decision": "maintain_priority_order",
                "priority_task": highest_priority_task["task_id"],
                "task_analysis": task_analysis,
                "resolution_strategy": "score_based",
                "message": "Priority conflict resolved by maintaining priority order"
            }

    def _resolve_task_dependency(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve task dependency conflicts."""
        dependent_task = request.get("dependent_task")
        dependency_task = request.get("dependency_task")
        
        # Check if dependency is already completed
        dependency_status = request.get("dependency_status", "pending")
        
        if dependency_status == "completed":
            return {
                "status": "resolved",
                "conflict_type": "task_dependency",
                "decision": "dependency_satisfied",
                "dependent_task": dependent_task,
                "dependency_task": dependency_task,
                "message": f"Dependency {dependency_task} is completed, {dependent_task} can proceed"
            }
        else:
            return {
                "status": "resolved",
                "conflict_type": "task_dependency",
                "decision": "resolve_dependency_first",
                "dependent_task": dependent_task,
                "dependency_task": dependency_task,
                "required_action": "complete_dependency_task",
                "message": f"Task {dependency_task} must be completed before {dependent_task} can proceed"
            }

    def _resolve_agent_coordination(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve agent coordination conflicts."""
        agents_involved = request.get("agents_involved", [])
        coordination_type = request.get("coordination_type", "general")
        
        if coordination_type == "workflow_sync":
            return {
                "status": "resolved",
                "conflict_type": "agent_coordination",
                "decision": "synchronize_workflow",
                "agents": agents_involved,
                "coordination_strategy": "workflow_synchronization",
                "message": f"Agents {agents_involved} will synchronize their workflows"
            }
        elif coordination_type == "resource_sharing":
            return {
                "status": "resolved",
                "conflict_type": "agent_coordination",
                "decision": "establish_resource_sharing",
                "agents": agents_involved,
                "coordination_strategy": "resource_sharing_protocol",
                "message": f"Agents {agents_involved} will establish resource sharing protocol"
            }
        else:
            return {
                "status": "resolved",
                "conflict_type": "agent_coordination",
                "decision": "establish_communication",
                "agents": agents_involved,
                "coordination_strategy": "direct_communication",
                "message": f"Agents {agents_involved} will establish direct communication"
            }

    def _default_conflict_resolution(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Default conflict resolution for unknown conflict types."""
        return {
            "status": "resolved",
            "conflict_type": request.get("conflict_type", "unknown"),
            "decision": "default_resolution",
            "message": "Conflict resolved using default strategy",
            "suggested_action": "review_conflict_manually"
        }

    def _negotiate_resource_allocation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate resource allocation between agents."""
        participants = context.get("participants", [])
        resources = context.get("resources", {})
        
        if not participants or not resources:
            return {
                "status": "error",
                "message": "Insufficient information for resource allocation negotiation"
            }
        
        # Simple negotiation: allocate resources based on agent priorities
        allocation_plan = {}
        
        for agent_id in participants:
            agent_priority = context.get(f"{agent_id}_priority", 5)
            required_resources = context.get(f"{agent_id}_required_resources", [])
            
            allocation_plan[agent_id] = {
                "priority": agent_priority,
                "allocated_resources": required_resources,
                "allocation_score": agent_priority / 10.0
            }
        
        return {
            "status": "success",
            "negotiation_type": "resource_allocation",
            "allocation_plan": allocation_plan,
            "participants": participants,
            "resources": list(resources.keys()),
            "message": "Resource allocation negotiation completed successfully"
        }

    def _negotiate_task_prioritization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate task prioritization between agents."""
        participants = context.get("participants", [])
        tasks = context.get("tasks", [])
        
        if not participants or not tasks:
            return {
                "status": "error",
                "message": "Insufficient information for task prioritization negotiation"
            }
        
        # Calculate consensus priorities
        consensus_priorities = {}
        
        for task_id in tasks:
            priorities = []
            for agent_id in participants:
                agent_priority = context.get(f"{agent_id}_{task_id}_priority", 5)
                priorities.append(agent_priority)
            
            # Use average priority as consensus
            consensus_priority = sum(priorities) / len(priorities)
            consensus_priorities[task_id] = round(consensus_priority)
        
        return {
            "status": "success",
            "negotiation_type": "task_prioritization",
            "consensus_priorities": consensus_priorities,
            "participants": participants,
            "tasks": tasks,
            "message": "Task prioritization negotiation completed successfully"
        }

    def _negotiate_workflow_coordination(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate workflow coordination between agents."""
        participants = context.get("participants", [])
        
        if not participants:
            return {
                "status": "error",
                "message": "Insufficient information for workflow coordination negotiation"
            }
        
        # Establish coordination protocol
        coordination_protocol = {
            "communication_frequency": "regular",
            "synchronization_points": ["task_completion", "milestone_reached"],
            "conflict_resolution": "negotiation_based",
            "status_reporting": "continuous"
        }
        
        return {
            "status": "success",
            "negotiation_type": "workflow_coordination",
            "coordination_protocol": coordination_protocol,
            "participants": participants,
            "message": "Workflow coordination negotiation completed successfully"
        }

    def _calculate_task_priority_score(self, task: Dict[str, Any]) -> float:
        """Calculate a comprehensive priority score for a task."""
        score = 0.0
        
        # Base score from explicit priority
        score += task.get("priority", 5) / 10.0
        
        # Add score for dependencies
        dependencies = task.get("dependencies", [])
        score += min(0.3, len(dependencies) * 0.1)
        
        # Add score for deadline urgency
        if "deadline" in task:
            try:
                deadline = datetime.fromisoformat(task["deadline"])
                current_time = datetime.now()
                time_remaining = (deadline - current_time).total_seconds()
                
                if time_remaining > 0:
                    # Higher urgency for tasks with less time remaining
                    hours_remaining = time_remaining / 3600
                    urgency_score = max(0, 1 - (math.log10(hours_remaining + 1) / 3))
                    score += min(0.4, urgency_score)
            except (ValueError, TypeError):
                pass
        
        # Add score for resource requirements
        if "required_resources" in task:
            required_resources = task.get("required_resources", [])
            score += min(0.2, len(required_resources) * 0.05)
        
        return min(1.0, score)

    def _log_coordination_request(self, request: Dict[str, Any]) -> None:
        """Log a coordination request."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": self._generate_request_id(request),
            "conflict_type": request.get("conflict_type", "unknown"),
            "requesting_agent": request.get("requesting_agent", "unknown"),
            "context": self._get_request_context_summary(request)
        }
        
        self.coordination_history.append(log_entry)
        self.coordination_metrics["total_coordination_events"] += 1
        self.coordination_metrics["conflict_types"][request.get("conflict_type", "unknown")] += 1
        
        # Keep history size manageable
        if len(self.coordination_history) > 100:
            self.coordination_history = self.coordination_history[-100:]

    def _log_successful_resolution(self, request: Dict[str, Any], resolution: Dict[str, Any]) -> None:
        """Log a successful conflict resolution."""
        # Find the corresponding request log
        request_id = self._generate_request_id(request)
        
        for entry in self.coordination_history:
            if entry["request_id"] == request_id:
                entry["resolution"] = {
                    "timestamp": datetime.now().isoformat(),
                    "status": resolution.get("status", "unknown"),
                    "decision": resolution.get("decision", "unknown"),
                    "resolution_strategy": resolution.get("resolution_strategy", "unknown")
                }
                break
        
        self.coordination_metrics["successful_resolutions"] += 1

    def _log_negotiation_result(self, context: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log a negotiation result."""
        negotiation_id = self._generate_negotiation_id(context)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "negotiation_id": negotiation_id,
            "negotiation_type": context.get("negotiation_type"),
            "participants": context.get("participants", []),
            "status": result.get("status"),
            "outcome": result.get("decision", result.get("message", "unknown"))
        }
        
        self.coordination_history.append(log_entry)

    def _get_request_context_summary(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the request context."""
        return {
            "resource_id": request.get("resource_id"),
            "task_count": len(request.get("involved_tasks", [])),
            "agents_involved": len(request.get("agents_involved", [])),
            "context_size": len(request)
        }

    def _generate_request_id(self, request: Dict[str, Any]) -> str:
        """Generate a unique ID for a coordination request."""
        import hashlib
        request_str = json.dumps(request, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()

    def _generate_negotiation_id(self, context: Dict[str, Any]) -> str:
        """Generate a unique ID for a negotiation."""
        import hashlib
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get coordination system metrics."""
        return {
            "coordination_metrics": dict(self.coordination_metrics),
            "conflict_type_distribution": dict(self.coordination_metrics["conflict_types"]),
            "success_rate": self._calculate_success_rate(),
            "recent_coordination_events": self.coordination_history[-5:] if self.coordination_history else []
        }

    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of conflict resolutions."""
        total = self.coordination_metrics["total_coordination_events"]
        successful = self.coordination_metrics["successful_resolutions"]
        
        if total > 0:
            return min(1.0, successful / total)
        return 0.0

    def get_coordination_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for improving coordination."""
        recommendations = []
        
        # Recommendations based on conflict patterns
        conflict_types = self.coordination_metrics["conflict_types"]
        
        if conflict_types.get("resource_conflict", 0) > conflict_types.get("priority_conflict", 0):
            recommendations.append({
                "type": "resource_management",
                "priority": "high",
                "message": "Frequent resource conflicts detected - consider resource optimization",
                "action": "review_resource_allocation_strategies"
            })
        
        if conflict_types.get("task_dependency", 0) > 3:
            recommendations.append({
                "type": "workflow_optimization",
                "priority": "medium",
                "message": "Frequent task dependency conflicts - review workflow design",
                "action": "analyze_workflow_dependencies"
            })
        
        # Recommendations based on success rate
        success_rate = self._calculate_success_rate()
        if success_rate < 0.7:
            recommendations.append({
                "type": "coordination_improvement",
                "priority": "high",
                "message": f"Low coordination success rate ({success_rate:.1%}) - review resolution strategies",
                "action": "improve_conflict_resolution_algorithms"
            })
        
        return recommendations


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