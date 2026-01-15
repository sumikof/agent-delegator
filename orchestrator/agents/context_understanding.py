"""Context understanding module for autonomous agents.

This module provides advanced context analysis capabilities for autonomous
agents to better understand their environment and make informed decisions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import re
from collections import Counter


class ContextAnalyzer:
    """Context analysis engine for autonomous agents."""

    def __init__(self) -> None:
        self.knowledge_base = {}  # Knowledge accumulated from past contexts
        self.pattern_cache = {}  # Cache for compiled regex patterns

    def analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given context and extract meaningful information."""
        analysis_result = {
            "context_type": self._determine_context_type(context),
            "complexity_score": self._calculate_complexity_score(context),
            "key_entities": self._extract_key_entities(context),
            "relationships": self._identify_relationships(context),
            "potential_issues": self._detect_potential_issues(context),
            "opportunities": self._identify_opportunities(context)
        }
        
        # Update knowledge base with new context
        self._update_knowledge_base(context, analysis_result)
        
        return analysis_result

    def _determine_context_type(self, context: Dict[str, Any]) -> str:
        """Determine the type of context based on its content."""
        context_types = []
        
        if "tasks" in context:
            context_types.append("task_management")
        if "resources" in context:
            context_types.append("resource_management")
        if "workflow" in context:
            context_types.append("workflow_coordination")
        if "agents" in context:
            context_types.append("agent_coordination")
        if "feedback" in context:
            context_types.append("feedback_processing")
        
        return ", ".join(context_types) if context_types else "general"

    def _calculate_complexity_score(self, context: Dict[str, Any]) -> float:
        """Calculate a complexity score for the context."""
        score = 0.0
        
        # Base score based on size
        score += min(0.5, len(context) / 10)
        
        # Add score for nested structures
        for key, value in context.items():
            if isinstance(value, dict):
                score += min(0.3, len(value) / 5)
            elif isinstance(value, list):
                score += min(0.3, len(value) / 5)
                # Check list item complexity
                if value and isinstance(value[0], dict):
                    score += min(0.2, len(value[0]) / 3)
        
        # Add score for special patterns
        if self._contains_complex_patterns(context):
            score += 0.2
        
        return min(1.0, score)

    def _extract_key_entities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key entities from the context."""
        entities = []
        
        # Extract tasks
        if "tasks" in context and isinstance(context["tasks"], list):
            for task in context["tasks"]:
                if isinstance(task, dict) and "id" in task:
                    entities.append({
                        "type": "task",
                        "id": task["id"],
                        "name": task.get("name", ""),
                        "priority": task.get("priority", 0),
                        "status": task.get("status", "unknown")
                    })
        
        # Extract resources
        if "resources" in context and isinstance(context["resources"], dict):
            for resource_id, resource_info in context["resources"].items():
                if isinstance(resource_info, dict):
                    entities.append({
                        "type": "resource",
                        "id": resource_id,
                        "name": resource_info.get("name", resource_id),
                        "availability": resource_info.get("availability", 1.0),
                        "status": resource_info.get("status", "available")
                    })
        
        # Extract agents
        if "agents" in context and isinstance(context["agents"], list):
            for agent in context["agents"]:
                if isinstance(agent, dict) and "agent_id" in agent:
                    entities.append({
                        "type": "agent",
                        "id": agent["agent_id"],
                        "name": agent.get("name", ""),
                        "status": agent.get("status", "active")
                    })
        
        return entities

    def _identify_relationships(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify relationships between entities in the context."""
        relationships = []
        entities = self._extract_key_entities(context)
        
        # Identify task dependencies
        if "tasks" in context and isinstance(context["tasks"], list):
            for task in context["tasks"]:
                if isinstance(task, dict) and "dependencies" in task:
                    task_id = task.get("id")
                    dependencies = task.get("dependencies", [])
                    
                    for dep_task_id in dependencies:
                        relationships.append({
                            "type": "dependency",
                            "source": dep_task_id,
                            "target": task_id,
                            "relationship": "must_complete_before"
                        })
        
        # Identify resource assignments
        if "tasks" in context and isinstance(context["tasks"], list):
            for task in context["tasks"]:
                if isinstance(task, dict) and "required_resources" in task:
                    task_id = task.get("id")
                    resources = task.get("required_resources", [])
                    
                    for resource_id in resources:
                        relationships.append({
                            "type": "resource_assignment",
                            "source": resource_id,
                            "target": task_id,
                            "relationship": "requires_resource"
                        })
        
        return relationships

    def _detect_potential_issues(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential issues in the context."""
        issues = []
        
        # Check for resource constraints
        if "resources" in context and isinstance(context["resources"], dict):
            for resource_id, resource_info in context["resources"].items():
                if isinstance(resource_info, dict):
                    availability = resource_info.get("availability", 1.0)
                    contention = resource_info.get("contention", 0)
                    
                    if availability < 0.3:
                        issues.append({
                            "type": "resource_constraint",
                            "severity": "high" if availability < 0.1 else "medium",
                            "resource_id": resource_id,
                            "message": f"Low resource availability: {availability:.1%}",
                            "suggested_action": "optimize_resource_usage"
                        })
                    
                    if contention > 0.7:
                        issues.append({
                            "type": "resource_contention",
                            "severity": "high" if contention > 0.9 else "medium",
                            "resource_id": resource_id,
                            "message": f"High resource contention: {contention:.1%}",
                            "suggested_action": "balance_resource_allocation"
                        })
        
        # Check for task dependencies issues
        if "tasks" in context and isinstance(context["tasks"], list):
            task_ids = [task.get("id") for task in context["tasks"] if isinstance(task, dict) and "id" in task]
            
            for task in context["tasks"]:
                if isinstance(task, dict) and "dependencies" in task:
                    dependencies = task.get("dependencies", [])
                    missing_deps = [dep for dep in dependencies if dep not in task_ids]
                    
                    if missing_deps:
                        issues.append({
                            "type": "missing_dependency",
                            "severity": "high",
                            "task_id": task.get("id"),
                            "missing_dependencies": missing_deps,
                            "message": f"Task {task.get('id')} has missing dependencies: {missing_deps}",
                            "suggested_action": "resolve_dependencies"
                        })
        
        # Check for potential bottlenecks
        if "workflow" in context and isinstance(context["workflow"], dict):
            workflow = context["workflow"]
            if "bottlenecks" in workflow:
                for bottleneck in workflow["bottlenecks"]:
                    issues.append({
                        "type": "workflow_bottleneck",
                        "severity": "medium",
                        "location": bottleneck.get("location", "unknown"),
                        "message": f"Potential bottleneck detected at {bottleneck.get('location', 'unknown')}",
                        "suggested_action": "optimize_workflow"
                    })
        
        return issues

    def _identify_opportunities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for optimization in the context."""
        opportunities = []
        
        # Check for parallelization opportunities
        if "tasks" in context and isinstance(context["tasks"], list):
            independent_tasks = []
            
            for task in context["tasks"]:
                if isinstance(task, dict):
                    has_deps = "dependencies" in task and task["dependencies"]
                    if not has_deps:
                        independent_tasks.append(task.get("id"))
            
            if len(independent_tasks) >= 2:
                opportunities.append({
                    "type": "parallelization",
                    "potential": "high" if len(independent_tasks) >= 3 else "medium",
                    "tasks": independent_tasks,
                    "message": f"{len(independent_tasks)} independent tasks could be parallelized",
                    "suggested_action": "execute_tasks_in_parallel"
                })
        
        # Check for resource optimization opportunities
        if "resources" in context and isinstance(context["resources"], dict):
            underutilized_resources = []
            
            for resource_id, resource_info in context["resources"].items():
                if isinstance(resource_info, dict):
                    availability = resource_info.get("availability", 1.0)
                    if availability > 0.8:  # High availability
                        underutilized_resources.append(resource_id)
            
            if underutilized_resources:
                opportunities.append({
                    "type": "resource_optimization",
                    "potential": "medium",
                    "resources": underutilized_resources,
                    "message": f"Underutilized resources could be optimized: {underutilized_resources}",
                    "suggested_action": "consolidate_resource_usage"
                })
        
        # Check for workflow optimization opportunities
        if "workflow" in context and isinstance(context["workflow"], dict):
            workflow = context["workflow"]
            
            # Check for redundant steps
            if "steps" in workflow and len(workflow["steps"]) > 5:
                opportunities.append({
                    "type": "workflow_optimization",
                    "potential": "medium",
                    "message": "Workflow with many steps could potentially be optimized",
                    "suggested_action": "review_workflow_steps"
                })
        
        return opportunities

    def _update_knowledge_base(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Update the knowledge base with information from the context."""
        context_id = self._generate_context_id(context)
        
        knowledge_entry = {
            "context_id": context_id,
            "timestamp": self._get_current_timestamp(),
            "context_type": analysis["context_type"],
            "complexity": analysis["complexity_score"],
            "entities": analysis["key_entities"],
            "relationships": analysis["relationships"],
            "issues": analysis["potential_issues"],
            "opportunities": analysis["opportunities"]
        }
        
        self.knowledge_base[context_id] = knowledge_entry
        
        # Keep knowledge base size manageable
        if len(self.knowledge_base) > 200:
            # Remove oldest entries
            sorted_entries = sorted(self.knowledge_base.items(), key=lambda x: x[1]["timestamp"])
            self.knowledge_base = dict(sorted_entries[-200:])

    def _contains_complex_patterns(self, context: Dict[str, Any]) -> bool:
        """Check if context contains complex patterns."""
        context_str = json.dumps(context)
        
        # Check for complex patterns using regex
        complex_patterns = [
            r"\b(dependency|depends_on|requires)\b",
            r"\b(priority|urgent|critical)\b",
            r"\b(conflict|contention|bottleneck)\b",
            r"\b(parallel|concurrent|async)\b"
        ]
        
        for pattern in complex_patterns:
            if pattern not in self.pattern_cache:
                self.pattern_cache[pattern] = re.compile(pattern, re.IGNORECASE)
            
            if self.pattern_cache[pattern].search(context_str):
                return True
        
        return False

    def _generate_context_id(self, context: Dict[str, Any]) -> str:
        """Generate a unique ID for the context."""
        import hashlib
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_context_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights about the context based on accumulated knowledge."""
        analysis = self.analyze_context(context)
        context_id = self._generate_context_id(context)
        
        insights = {
            "context_analysis": analysis,
            "historical_context": self._get_historical_context(context_id),
            "recommendations": self._generate_recommendations(analysis)
        }
        
        return insights

    def _get_historical_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get historical context information."""
        return self.knowledge_base.get(context_id)

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on context analysis."""
        recommendations = []
        
        # Recommendations based on issues
        for issue in analysis["potential_issues"]:
            recommendations.append({
                "type": "issue_resolution",
                "priority": "high" if issue["severity"] == "high" else "medium",
                "issue_type": issue["type"],
                "message": f"Resolve {issue['type']}: {issue['message']}",
                "action": issue["suggested_action"]
            })
        
        # Recommendations based on opportunities
        for opportunity in analysis["opportunities"]:
            recommendations.append({
                "type": "optimization",
                "priority": "high" if opportunity["potential"] == "high" else "medium",
                "opportunity_type": opportunity["type"],
                "message": f"Optimize {opportunity['type']}: {opportunity['message']}",
                "action": opportunity["suggested_action"]
            })
        
        # General recommendations based on context type
        context_type = analysis["context_type"]
        if "task_management" in context_type:
            recommendations.append({
                "type": "task_management",
                "priority": "medium",
                "message": "Review task priorities and dependencies",
                "action": "review_task_management"
            })
        
        if "resource_management" in context_type:
            recommendations.append({
                "type": "resource_management",
                "priority": "medium",
                "message": "Optimize resource allocation",
                "action": "optimize_resources"
            })
        
        return recommendations

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of the accumulated knowledge."""
        return {
            "knowledge_entries": len(self.knowledge_base),
            "context_types": self._get_context_type_statistics(),
            "common_issues": self._get_common_issues(),
            "common_opportunities": self._get_common_opportunities()
        }

    def _get_context_type_statistics(self) -> Dict[str, int]:
        """Get statistics about context types."""
        context_types = Counter()
        
        for entry in self.knowledge_base.values():
            for ctx_type in entry["context_type"].split(", "):
                context_types[ctx_type] += 1
        
        return dict(context_types)

    def _get_common_issues(self) -> List[Dict[str, Any]]:
        """Get common issues from the knowledge base."""
        issue_types = Counter()
        
        for entry in self.knowledge_base.values():
            for issue in entry["issues"]:
                issue_types[issue["type"]] += 1
        
        common_issues = []
        for issue_type, count in issue_types.most_common(3):
            common_issues.append({
                "type": issue_type,
                "count": count
            })
        
        return common_issues

    def _get_common_opportunities(self) -> List[Dict[str, Any]]:
        """Get common opportunities from the knowledge base."""
        opportunity_types = Counter()
        
        for entry in self.knowledge_base.values():
            for opportunity in entry["opportunities"]:
                opportunity_types[opportunity["type"]] += 1
        
        common_opportunities = []
        for opportunity_type, count in opportunity_types.most_common(3):
            common_opportunities.append({
                "type": opportunity_type,
                "count": count
            })
        
        return common_opportunities