"""Negotiation system for autonomous agents.

This module provides advanced negotiation capabilities for autonomous
agents to resolve conflicts and reach agreements.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import math
from collections import defaultdict


class NegotiationSystem:
    """Advanced negotiation system for autonomous agents."""

    def __init__(self) -> None:
        self.negotiation_protocols = {
            "resource_allocation": ResourceAllocationProtocol(),
            "task_prioritization": TaskPrioritizationProtocol(),
            "workflow_coordination": WorkflowCoordinationProtocol(),
            "conflict_resolution": ConflictResolutionProtocol()
        }
        self.negotiation_history = []
        self.error_log = []
        self.negotiation_metrics = {
            "total_negotiations": 0,
            "successful_negotiations": 0,
            "failed_negotiations": 0,
            "average_negotiation_time": 0,
            "negotiation_types": defaultdict(int)
        }

    def _log_error(self, error_message: str, negotiation_type: str = "unknown") -> None:
        """Log an error message for debugging and monitoring."""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": "negotiation_error",
            "message": error_message,
            "negotiation_type": negotiation_type
        }
        
        self.error_log.append(error_record)
        self.negotiation_metrics["failed_negotiations"] += 1
        
        # Keep error log size manageable
        if len(self.error_log) > 20:
            self.error_log = self.error_log[-20:]

    def initiate_negotiation(self, negotiation_type: str, participants: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a negotiation process with improved error handling."""
        try:
            # Validate inputs
            if not isinstance(participants, list) or not participants:
                raise ValueError("Invalid participants: must be a non-empty list")
            
            if not isinstance(context, dict):
                raise ValueError("Invalid context: must be a dictionary")
            
            if negotiation_type not in self.negotiation_protocols:
                self._log_error(f"Unknown negotiation type: {negotiation_type}", negotiation_type)
                return {
                    "status": "error",
                    "message": f"Unknown negotiation type: {negotiation_type}"
                }
            
            # Prepare negotiation context
            negotiation_context = {
                "negotiation_id": self._generate_negotiation_id(negotiation_type, participants, context),
                "negotiation_type": negotiation_type,
                "participants": participants,
                "context": context,
                "start_time": datetime.now().isoformat(),
                "status": "initiated"
            }
            
            # Execute negotiation protocol
            protocol = self.negotiation_protocols[negotiation_type]
            result = protocol.execute(negotiation_context)
            
            # Validate result
            if not isinstance(result, dict):
                raise ValueError("Negotiation protocol returned invalid result")
            
            # Log negotiation result
            self._log_negotiation_result(negotiation_context, result)
            
            return result
            
        except Exception as e:
            # Log error and return error response
            self._log_error(f"Negotiation initiation failed: {str(e)}", negotiation_type)
            return {
                "status": "error",
                "message": f"Negotiation failed: {str(e)}",
                "error_type": "negotiation_failure",
                "negotiation_type": negotiation_type,
                "participants": participants
            }

    def get_negotiation_status(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a negotiation."""
        for negotiation in self.negotiation_history:
            if negotiation["negotiation_id"] == negotiation_id:
                return negotiation
        return None

    def get_negotiation_metrics(self) -> Dict[str, Any]:
        """Get negotiation system metrics."""
        return {
            "negotiation_metrics": dict(self.negotiation_metrics),
            "negotiation_type_distribution": dict(self.negotiation_metrics["negotiation_types"]),
            "success_rate": self._calculate_success_rate(),
            "recent_negotiations": self.negotiation_history[-5:] if self.negotiation_history else []
        }

    def _log_negotiation_result(self, context: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log a negotiation result."""
        negotiation_id = context["negotiation_id"]
        
        log_entry = {
            "negotiation_id": negotiation_id,
            "negotiation_type": context["negotiation_type"],
            "participants": context["participants"],
            "start_time": context["start_time"],
            "end_time": datetime.now().isoformat(),
            "status": result.get("status", "unknown"),
            "outcome": result.get("decision", result.get("message", "unknown"))
        }
        
        self.negotiation_history.append(log_entry)
        self.negotiation_metrics["total_negotiations"] += 1
        self.negotiation_metrics["negotiation_types"][context["negotiation_type"]] += 1
        
        if result.get("status") == "success":
            self.negotiation_metrics["successful_negotiations"] += 1
        
        # Calculate average negotiation time
        try:
            start_time = datetime.fromisoformat(context["start_time"])
            end_time = datetime.fromisoformat(log_entry["end_time"])
            negotiation_time = (end_time - start_time).total_seconds()
            
            total_negotiations = self.negotiation_metrics["total_negotiations"]
            current_avg = self.negotiation_metrics["average_negotiation_time"]
            new_avg = ((current_avg * (total_negotiations - 1)) + negotiation_time) / total_negotiations
            self.negotiation_metrics["average_negotiation_time"] = new_avg
        except (ValueError, TypeError):
            pass
        
        # Keep history size manageable
        if len(self.negotiation_history) > 50:
            self.negotiation_history = self.negotiation_history[-50:]

    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of negotiations."""
        total = self.negotiation_metrics["total_negotiations"]
        successful = self.negotiation_metrics["successful_negotiations"]
        
        if total > 0:
            return min(1.0, successful / total)
        return 0.0

    def _generate_negotiation_id(self, negotiation_type: str, participants: List[str], context: Dict[str, Any]) -> str:
        """Generate a unique ID for a negotiation."""
        import hashlib
        
        # Create a unique string from negotiation parameters
        participants_sorted = sorted(participants)
        context_str = json.dumps({
            "type": negotiation_type,
            "participants": participants_sorted,
            "timestamp": datetime.now().isoformat()
        }, sort_keys=True)
        
        return hashlib.md5(context_str.encode()).hexdigest()

    def get_negotiation_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for improving negotiation effectiveness."""
        recommendations = []
        
        # Recommendations based on negotiation patterns
        negotiation_types = self.negotiation_metrics["negotiation_types"]
        
        if negotiation_types.get("resource_allocation", 0) > negotiation_types.get("task_prioritization", 0):
            recommendations.append({
                "type": "resource_management",
                "priority": "high",
                "message": "Frequent resource allocation negotiations - consider resource optimization",
                "action": "review_resource_allocation_strategies"
            })
        
        if negotiation_types.get("conflict_resolution", 0) > 3:
            recommendations.append({
                "type": "conflict_management",
                "priority": "medium",
                "message": "Frequent conflict resolution negotiations - review conflict prevention strategies",
                "action": "improve_conflict_prevention"
            })
        
        # Recommendations based on success rate
        success_rate = self._calculate_success_rate()
        if success_rate < 0.8:
            recommendations.append({
                "type": "negotiation_improvement",
                "priority": "high",
                "message": f"Moderate negotiation success rate ({success_rate:.1%}) - review negotiation strategies",
                "action": "improve_negotiation_algorithms"
            })
        
        return recommendations


class NegotiationProtocol:
    """Base class for negotiation protocols."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the negotiation protocol."""
        raise NotImplementedError("Subclasses must implement the execute method")

    def _log_negotiation_step(self, context: Dict[str, Any], step: str, details: Dict[str, Any]) -> None:
        """Log a negotiation step."""
        # This would be implemented in a real system
        pass


class ResourceAllocationProtocol(NegotiationProtocol):
    """Resource allocation negotiation protocol."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute resource allocation negotiation."""
        participants = context.get("participants", [])
        # Handle nested context structure
        actual_context = context.get("context", context)
        resources = actual_context.get("resources", {})
        
        if not participants or not resources:
            return {
                "status": "error",
                "message": f"Insufficient information for resource allocation negotiation: participants={participants}, resources={resources}"
            }
        
        # Gather agent requirements and priorities
        agent_requirements = {}
        for agent_id in participants:
            agent_requirements[agent_id] = {
                "priority": actual_context.get(f"{agent_id}_priority", 5),
                "required_resources": actual_context.get(f"{agent_id}_required_resources", []),
                "flexibility": actual_context.get(f"{agent_id}_flexibility", 0.5)
            }
        
        # Calculate fair allocation
        allocation_plan = self._calculate_fair_allocation(agent_requirements, resources)
        
        return {
            "status": "success",
            "negotiation_type": "resource_allocation",
            "allocation_plan": allocation_plan,
            "participants": participants,
            "resources": list(resources.keys()),
            "allocation_strategy": "fair_sharing_with_priority",
            "message": "Resource allocation negotiation completed successfully"
        }

    def _calculate_fair_allocation(self, agent_requirements: Dict[str, Any], resources: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate fair resource allocation."""
        allocation_plan = {}
        
        for agent_id, requirements in agent_requirements.items():
            agent_allocation = {
                "priority": requirements["priority"],
                "allocated_resources": [],
                "allocation_score": 0.0,
                "satisfaction": 0.0
            }
            
            # Allocate required resources based on priority and availability
            for resource_id in requirements["required_resources"]:
                if resource_id in resources:
                    resource_info = resources[resource_id]
                    availability = resource_info.get("availability", 1.0)
                    
                    # Calculate allocation score based on priority and availability
                    allocation_score = (requirements["priority"] / 10.0) * availability
                    
                    if allocation_score > 0.3:  # Threshold for allocation
                        agent_allocation["allocated_resources"].append(resource_id)
                        agent_allocation["allocation_score"] += allocation_score
            
            # Calculate satisfaction score
            if requirements["required_resources"]:
                satisfaction = len(agent_allocation["allocated_resources"]) / len(requirements["required_resources"])
                agent_allocation["satisfaction"] = satisfaction
            
            allocation_plan[agent_id] = agent_allocation
        
        return allocation_plan


class TaskPrioritizationProtocol(NegotiationProtocol):
    """Task prioritization negotiation protocol."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task prioritization negotiation."""
        participants = context.get("participants", [])
        # Handle nested context structure
        actual_context = context.get("context", context)
        tasks = actual_context.get("tasks", [])
        
        if not participants or not tasks:
            return {
                "status": "error",
                "message": "Insufficient information for task prioritization negotiation"
            }
        
        # Gather agent priorities for each task
        task_priorities = defaultdict(list)
        for agent_id in participants:
            for task_id in tasks:
                agent_priority = actual_context.get(f"{agent_id}_{task_id}_priority", 5)
                task_priorities[task_id].append(agent_priority)
        
        # Calculate consensus priorities
        consensus_priorities = {}
        for task_id, priorities in task_priorities.items():
            # Use weighted average based on agent priorities
            agent_priorities = actual_context.get("agent_priorities", {})
            weights = [agent_priorities.get(agent_id, 5) for agent_id in participants]
            
            if weights and len(weights) == len(priorities):
                # Weighted average
                weighted_sum = sum(p * w for p, w in zip(priorities, weights))
                weight_sum = sum(weights)
                consensus_priority = weighted_sum / weight_sum if weight_sum > 0 else sum(priorities) / len(priorities)
            else:
                # Simple average
                consensus_priority = sum(priorities) / len(priorities)
            
            consensus_priorities[task_id] = round(consensus_priority)
        
        return {
            "status": "success",
            "negotiation_type": "task_prioritization",
            "consensus_priorities": consensus_priorities,
            "participants": participants,
            "tasks": tasks,
            "prioritization_strategy": "weighted_consensus",
            "message": "Task prioritization negotiation completed successfully"
        }


class WorkflowCoordinationProtocol(NegotiationProtocol):
    """Workflow coordination negotiation protocol."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow coordination negotiation."""
        participants = context.get("participants", [])
        
        if not participants:
            return {
                "status": "error",
                "message": "Insufficient information for workflow coordination negotiation"
            }
        
        # Establish coordination protocol
        coordination_protocol = {
            "communication_frequency": context.get("communication_frequency", "regular"),
            "synchronization_points": context.get("synchronization_points", ["task_completion", "milestone_reached"]),
            "conflict_resolution": context.get("conflict_resolution", "negotiation_based"),
            "status_reporting": context.get("status_reporting", "continuous"),
            "resource_sharing": context.get("resource_sharing", "cooperative"),
            "decision_making": context.get("decision_making", "consensus_based")
        }
        
        # Calculate coordination efficiency metrics
        efficiency_metrics = self._calculate_coordination_efficiency(participants, context)
        
        return {
            "status": "success",
            "negotiation_type": "workflow_coordination",
            "coordination_protocol": coordination_protocol,
            "participants": participants,
            "efficiency_metrics": efficiency_metrics,
            "message": "Workflow coordination negotiation completed successfully"
        }

    def _calculate_coordination_efficiency(self, participants: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate coordination efficiency metrics."""
        # Simple efficiency calculation based on participant count
        participant_count = len(participants)
        
        # Base efficiency (higher for smaller teams)
        base_efficiency = max(0.5, 1.0 - (participant_count * 0.1))
        
        # Adjust based on communication frequency
        comm_frequency = context.get("communication_frequency", "regular")
        if comm_frequency == "frequent":
            efficiency_adjustment = -0.1
        elif comm_frequency == "infrequent":
            efficiency_adjustment = 0.1
        else:
            efficiency_adjustment = 0.0
        
        coordination_efficiency = max(0.1, min(1.0, base_efficiency + efficiency_adjustment))
        
        return {
            "coordination_efficiency": coordination_efficiency,
            "participant_count": participant_count,
            "communication_frequency": comm_frequency,
            "estimated_overhead": 1.0 - coordination_efficiency
        }


class ConflictResolutionProtocol(NegotiationProtocol):
    """Conflict resolution negotiation protocol."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conflict resolution negotiation."""
        conflict_type = context.get("conflict_type", "general")
        participants = context.get("participants", [])
        
        if not participants:
            return {
                "status": "error",
                "message": "Insufficient information for conflict resolution negotiation"
            }
        
        # Apply conflict resolution strategy based on type
        if conflict_type == "resource_conflict":
            resolution = self._resolve_resource_conflict(context)
        elif conflict_type == "priority_conflict":
            resolution = self._resolve_priority_conflict(context)
        elif conflict_type == "task_dependency":
            resolution = self._resolve_task_dependency(context)
        else:
            resolution = self._resolve_general_conflict(context)
        
        return {
            "status": "success",
            "negotiation_type": "conflict_resolution",
            "conflict_type": conflict_type,
            "resolution": resolution,
            "participants": participants,
            "message": "Conflict resolution negotiation completed successfully"
        }

    def _resolve_resource_conflict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve resource conflicts through negotiation."""
        resource_id = context.get("resource_id")
        participants = context.get("participants", [])
        
        # Gather agent requirements and priorities
        agent_requirements = {}
        for agent_id in participants:
            agent_requirements[agent_id] = {
                "priority": context.get(f"{agent_id}_priority", 5),
                "resource_need": context.get(f"{agent_id}_resource_need", 0.5),
                "flexibility": context.get(f"{agent_id}_flexibility", 0.5)
            }
        
        # Calculate fair allocation
        allocation = self._calculate_resource_allocation(agent_requirements)
        
        return {
            "resolution_type": "resource_allocation",
            "resource_id": resource_id,
            "allocation_plan": allocation,
            "resolution_strategy": "priority_and_flexibility_based"
        }

    def _resolve_priority_conflict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve priority conflicts through negotiation."""
        tasks = context.get("tasks", [])
        participants = context.get("participants", [])
        
        # Gather agent priorities
        task_priorities = {}
        for task_id in tasks:
            priorities = []
            for agent_id in participants:
                priorities.append(context.get(f"{agent_id}_{task_id}_priority", 5))
            task_priorities[task_id] = priorities
        
        # Calculate consensus priorities
        consensus_priorities = {}
        for task_id, priorities in task_priorities.items():
            consensus_priority = sum(priorities) / len(priorities)
            consensus_priorities[task_id] = round(consensus_priority)
        
        return {
            "resolution_type": "priority_consensus",
            "tasks": tasks,
            "consensus_priorities": consensus_priorities,
            "resolution_strategy": "average_priority_consensus"
        }

    def _resolve_task_dependency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve task dependency conflicts through negotiation."""
        dependent_task = context.get("dependent_task")
        dependency_task = context.get("dependency_task")
        
        # Simple resolution: ensure dependency is completed first
        return {
            "resolution_type": "dependency_resolution",
            "dependent_task": dependent_task,
            "dependency_task": dependency_task,
            "resolution": "complete_dependency_first",
            "resolution_strategy": "dependency_aware_scheduling"
        }

    def _resolve_general_conflict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve general conflicts through negotiation."""
        participants = context.get("participants", [])
        
        # Simple resolution: establish communication and cooperation
        return {
            "resolution_type": "general_resolution",
            "resolution": "establish_cooperation_protocol",
            "participants": participants,
            "resolution_strategy": "cooperative_conflict_resolution"
        }

    def _calculate_resource_allocation(self, agent_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource allocation for conflict resolution."""
        allocation = {}
        
        # Calculate total demand and flexibility
        total_demand = sum(req["resource_need"] for req in agent_requirements.values())
        total_flexibility = sum(req["flexibility"] for req in agent_requirements.values())
        
        for agent_id, requirements in agent_requirements.items():
            # Calculate allocation based on priority, need, and flexibility
            priority_weight = requirements["priority"] / 10.0
            need_weight = requirements["resource_need"] / max(1.0, total_demand)
            flexibility_weight = 1.0 - requirements["flexibility"]
            
            allocation_score = (priority_weight * 0.5) + (need_weight * 0.3) + (flexibility_weight * 0.2)
            
            allocation[agent_id] = {
                "allocation_score": allocation_score,
                "allocated_resource": allocation_score > 0.5,  # Simple threshold
                "priority": requirements["priority"],
                "resource_need": requirements["resource_need"],
                "flexibility": requirements["flexibility"]
            }
        
        return allocation


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