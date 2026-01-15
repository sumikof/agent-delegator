"""Task management system for autonomous agents.

This module provides advanced task splitting and integration capabilities
for autonomous agents to handle complex workflows.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import math
from collections import defaultdict


class TaskManager:
    """Advanced task management system."""

    def __init__(self) -> None:
        self.task_splitting_strategies = {
            "size_based": self._split_by_size,
            "complexity_based": self._split_by_complexity,
            "resource_based": self._split_by_resources,
            "dependency_based": self._split_by_dependencies
        }
        self.task_integration_strategies = {
            "sequential": self._integrate_sequentially,
            "parallel": self._integrate_in_parallel,
            "conditional": self._integrate_conditionally
        }
        self.task_history = []
        self.error_log = []
        self.splitting_metrics = {
            "total_splits": 0,
            "successful_integrations": 0,
            "average_split_size": 0,
            "failed_splits": 0
        }

    def _log_error(self, error_message: str) -> None:
        """Log an error message for debugging and monitoring."""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": "task_management_error",
            "message": error_message
        }
        
        self.error_log.append(error_record)
        self.splitting_metrics["failed_splits"] += 1
        
        # Keep error log size manageable
        if len(self.error_log) > 20:
            self.error_log = self.error_log[-20:]

    def split_task(self, task: Dict[str, Any], strategy: str = "size_based", context: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """Split a complex task into smaller subtasks with improved error handling."""
        try:
            # Validate task input
            if not isinstance(task, dict) or "id" not in task:
                raise ValueError("Invalid task: must be a dictionary with 'id' field")
            
            # Validate strategy
            if strategy not in self.task_splitting_strategies:
                strategy = "size_based"
            
            # Use the selected strategy
            split_function = self.task_splitting_strategies[strategy]
            subtasks = split_function(task, context or {})
            
            # Validate subtasks
            if not isinstance(subtasks, list):
                raise ValueError("Task splitting returned invalid result")
            
            # Log the splitting operation
            self._log_task_splitting(task, subtasks, strategy)
            
            return subtasks
            
        except Exception as e:
            # Log error and return a minimal task structure
            self._log_error(f"Task splitting failed: {str(e)}")
            # Return a single task with minimal structure to avoid empty results
            return [{
                "id": f"task_{datetime.now().timestamp()}",
                "name": "Fallback Task",
                "description": "Created due to task splitting error",
                "status": "pending",
                "error": str(e)
            }]

    def integrate_tasks(self, subtasks: List[Dict[str, Any]], strategy: str = "sequential", context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Integrate multiple subtasks into a completed task with improved error handling."""
        try:
            # Validate subtasks input
            if not isinstance(subtasks, list):
                raise ValueError("Invalid subtasks: must be a list")
            
            # Handle empty subtask list
            if not subtasks:
                return {}
            
            # Validate strategy
            if strategy not in self.task_integration_strategies:
                strategy = "sequential"
            
            # Use the selected strategy
            integrate_function = self.task_integration_strategies[strategy]
            integrated_task = integrate_function(subtasks, context or {})
            
            # Validate integrated task
            if not isinstance(integrated_task, dict):
                raise ValueError("Task integration returned invalid result")
            
            # Log the integration operation
            self._log_task_integration(subtasks, integrated_task, strategy)
            
            return integrated_task
            
        except Exception as e:
            # Log error and return empty task
            self._log_error(f"Task integration failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "subtasks": [subtask.get("id", "unknown") for subtask in subtasks if isinstance(subtask, dict)]
            }

    def _split_by_size(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split task based on size/complexity metrics."""
        subtasks = []
        
        # Validate task structure
        if not task or not isinstance(task, dict):
            self._log_error("Invalid task structure: task is None or not a dictionary")
            return []
        
        # Generate task ID if missing
        task_id = task.get("id", f"task_{datetime.now().timestamp()}")
        
        # Estimate task complexity
        complexity = self._estimate_task_complexity(task)
        
        # Determine number of subtasks based on complexity
        num_subtasks = max(2, min(5, math.ceil(complexity / 2)))
        
        # Create subtasks
        for i in range(num_subtasks):
            subtask = {
                "id": f"{task_id}_subtask_{i+1}",
                "name": f"{task.get('name', 'Task')} - Part {i+1}",
                "description": f"Subtask {i+1} of {task.get('name', 'Task')}",
                "original_task_id": task_id,
                "subtask_index": i + 1,
                "total_subtasks": num_subtasks,
                "priority": task.get("priority", 5),
                "dependencies": [],
                "required_resources": task.get("required_resources", []),
                "estimated_complexity": complexity / num_subtasks,
                "status": "pending"
            }
            
            # Add dependencies for sequential execution
            if i > 0:
                subtask["dependencies"] = [f"{task_id}_subtask_{i}"]
            
            subtasks.append(subtask)
        
        return subtasks

    def _split_by_complexity(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split task based on functional complexity."""
        subtasks = []
        
        # Analyze task components
        components = self._analyze_task_components(task)
        
        # Create subtask for each component
        for i, component in enumerate(components):
            subtask = {
                "id": f"{task['id']}_component_{i+1}",
                "name": f"{task.get('name', 'Task')} - {component['name']}",
                "description": component.get("description", f"Component {i+1} implementation"),
                "original_task_id": task["id"],
                "component_type": component["type"],
                "priority": task.get("priority", 5),
                "dependencies": component.get("dependencies", []),
                "required_resources": component.get("resources", []),
                "estimated_complexity": component.get("complexity", 1.0),
                "status": "pending"
            }
            
            subtasks.append(subtask)
        
        return subtasks

    def _split_by_resources(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split task based on resource requirements."""
        subtasks = []
        
        required_resources = task.get("required_resources", [])
        
        if not required_resources:
            # Fallback to size-based splitting if no resources specified
            return self._split_by_size(task, context)
        
        # Create subtask for each resource type
        for i, resource_id in enumerate(required_resources):
            subtask = {
                "id": f"{task['id']}_resource_{i+1}",
                "name": f"{task.get('name', 'Task')} - Resource {resource_id}",
                "description": f"Task component requiring resource {resource_id}",
                "original_task_id": task["id"],
                "required_resources": [resource_id],
                "priority": task.get("priority", 5),
                "dependencies": [],
                "estimated_complexity": 1.0 / len(required_resources),
                "status": "pending"
            }
            
            # Add dependencies if resources have dependencies
            resource_info = context.get("resources", {}).get(resource_id, {})
            if "dependencies" in resource_info:
                subtask["dependencies"] = resource_info["dependencies"]
            
            subtasks.append(subtask)
        
        return subtasks

    def _split_by_dependencies(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split task based on dependency analysis."""
        subtasks = []
        
        dependencies = task.get("dependencies", [])
        
        if not dependencies:
            # Fallback to size-based splitting if no dependencies
            return self._split_by_size(task, context)
        
        # Create subtask for each dependency group
        dependency_groups = self._group_dependencies(dependencies, context)
        
        for i, dep_group in enumerate(dependency_groups):
            subtask = {
                "id": f"{task['id']}_depgroup_{i+1}",
                "name": f"{task.get('name', 'Task')} - Dependency Group {i+1}",
                "description": f"Task component depending on {', '.join(dep_group)}",
                "original_task_id": task["id"],
                "dependencies": dep_group,
                "priority": task.get("priority", 5),
                "required_resources": task.get("required_resources", []),
                "estimated_complexity": 1.0 / len(dependency_groups),
                "status": "pending"
            }
            
            subtasks.append(subtask)
        
        return subtasks

    def _integrate_sequentially(self, subtasks: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate subtasks sequentially."""
        if not subtasks:
            return {}
        
        # Get the first subtask as base
        integrated_task = subtasks[0].copy()
        
        # Update task information
        integrated_task["id"] = integrated_task.get("original_task_id", subtasks[0]["id"])
        integrated_task["name"] = integrated_task.get("name", "Integrated Task")
        integrated_task["description"] = "Task integrated from multiple subtasks"
        
        # Combine subtask results
        integrated_task["subtasks"] = []
        integrated_task["subtask_results"] = {}
        
        for subtask in subtasks:
            subtask_info = {
                "subtask_id": subtask["id"],
                "status": subtask.get("status", "unknown"),
                "result": subtask.get("result", {})
            }
            
            integrated_task["subtasks"].append(subtask_info)
            
            # Store subtask results
            if "result" in subtask:
                integrated_task["subtask_results"][subtask["id"]] = subtask["result"]
        
        # Determine overall status
        all_completed = all(subtask.get("status") == "completed" for subtask in subtasks)
        integrated_task["status"] = "completed" if all_completed else "partial"
        
        # Calculate overall completion percentage
        completed_count = sum(1 for subtask in subtasks if subtask.get("status") == "completed")
        integrated_task["completion_percentage"] = (completed_count / len(subtasks)) * 100
        
        return integrated_task

    def _integrate_in_parallel(self, subtasks: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate subtasks that were executed in parallel."""
        if not subtasks:
            return {}
        
        # Create integrated task
        integrated_task = {
            "id": subtasks[0].get("original_task_id", f"integrated_{subtasks[0]['id']}"),
            "name": subtasks[0].get("name", "Parallel Integrated Task"),
            "description": "Task integrated from parallel subtasks",
            "subtasks": [],
            "subtask_results": {},
            "execution_mode": "parallel",
            "status": "pending"
        }
        
        # Process each subtask
        all_completed = True
        for subtask in subtasks:
            subtask_info = {
                "subtask_id": subtask["id"],
                "status": subtask.get("status", "unknown"),
                "result": subtask.get("result", {})
            }
            
            integrated_task["subtasks"].append(subtask_info)
            
            # Store subtask results
            if "result" in subtask:
                integrated_task["subtask_results"][subtask["id"]] = subtask["result"]
            
            if subtask.get("status") != "completed":
                all_completed = False
        
        # Determine overall status
        integrated_task["status"] = "completed" if all_completed else "partial"
        
        # Calculate parallel execution metrics
        if all_completed:
            # Estimate time savings from parallel execution
            start_times = []
            end_times = []
            
            for subtask in subtasks:
                if "start_time" in subtask and "end_time" in subtask:
                    try:
                        start_times.append(datetime.fromisoformat(subtask["start_time"]))
                        end_times.append(datetime.fromisoformat(subtask["end_time"]))
                    except (ValueError, TypeError):
                        pass
            
            if start_times and end_times:
                parallel_duration = (max(end_times) - min(start_times)).total_seconds()
                sequential_duration = sum((end - start).total_seconds() for start, end in zip(start_times, end_times))
                
                if sequential_duration > 0:
                    time_saved = sequential_duration - parallel_duration
                    time_saved_percentage = (time_saved / sequential_duration) * 100
                    
                    integrated_task["parallel_metrics"] = {
                        "time_saved_seconds": time_saved,
                        "time_saved_percentage": time_saved_percentage,
                        "parallel_efficiency": min(1.0, parallel_duration / sequential_duration)
                    }
        
        return integrated_task

    def _integrate_conditionally(self, subtasks: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate subtasks with conditional logic."""
        if not subtasks:
            return {}
        
        # Analyze subtask results to determine integration approach
        integration_approach = self._determine_integration_approach(subtasks)
        
        if integration_approach == "merge_results":
            return self._integrate_by_merging_results(subtasks)
        elif integration_approach == "select_best":
            return self._integrate_by_selecting_best(subtasks)
        elif integration_approach == "conditional_combination":
            return self._integrate_by_conditional_combination(subtasks, context)
        else:
            # Fallback to sequential integration
            return self._integrate_sequentially(subtasks, context)

    def _determine_integration_approach(self, subtasks: List[Dict[str, Any]]) -> str:
        """Determine the best integration approach based on subtask results."""
        # Check if subtasks have similar results (suggesting merge approach)
        if self._have_similar_results(subtasks):
            return "merge_results"
        
        # Check if subtasks have quality metrics (suggesting selection approach)
        if any("quality_score" in subtask for subtask in subtasks):
            return "select_best"
        
        # Check if context suggests conditional combination
        # For now, use simple heuristic
        if len(subtasks) > 2:
            return "conditional_combination"
        
        return "merge_results"

    def _have_similar_results(self, subtasks: List[Dict[str, Any]]) -> bool:
        """Check if subtasks have similar results."""
        if len(subtasks) < 2:
            return True
        
        # Simple comparison: check if results have similar structure
        first_result = subtasks[0].get("result", {})
        
        for subtask in subtasks[1:]:
            current_result = subtask.get("result", {})
            
            # Compare result structure
            if set(first_result.keys()) != set(current_result.keys()):
                return False
        
        return True

    def _integrate_by_merging_results(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Integrate subtasks by merging their results."""
        integrated_task = {
            "id": subtasks[0].get("original_task_id", f"merged_{subtasks[0]['id']}"),
            "name": subtasks[0].get("name", "Merged Task"),
            "description": "Task created by merging subtask results",
            "subtasks": [],
            "merged_results": {},
            "status": "completed"
        }
        
        # Merge results from all subtasks
        for subtask in subtasks:
            subtask_info = {
                "subtask_id": subtask["id"],
                "status": subtask.get("status", "unknown")
            }
            
            integrated_task["subtasks"].append(subtask_info)
            
            # Merge subtask results
            if "result" in subtask:
                for key, value in subtask["result"].items():
                    if key not in integrated_task["merged_results"]:
                        integrated_task["merged_results"][key] = []
                    integrated_task["merged_results"][key].append(value)
        
        return integrated_task

    def _integrate_by_selecting_best(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Integrate subtasks by selecting the best result."""
        if not subtasks:
            return {}
        
        # Find subtask with highest quality score
        best_subtask = max(subtasks, key=lambda x: x.get("quality_score", 0))
        
        integrated_task = {
            "id": best_subtask.get("original_task_id", f"best_{best_subtask['id']}"),
            "name": best_subtask.get("name", "Best Result Task"),
            "description": "Task using the best subtask result",
            "subtasks": [],
            "selected_result": best_subtask.get("result", {}),
            "selection_criteria": "quality_score",
            "best_subtask_id": best_subtask["id"],
            "best_quality_score": best_subtask.get("quality_score", 0),
            "status": "completed"
        }
        
        # Add information about all subtasks
        for subtask in subtasks:
            subtask_info = {
                "subtask_id": subtask["id"],
                "quality_score": subtask.get("quality_score", 0),
                "status": subtask.get("status", "unknown"),
                "selected": subtask["id"] == best_subtask["id"]
            }
            
            integrated_task["subtasks"].append(subtask_info)
        
        return integrated_task

    def _integrate_by_conditional_combination(self, subtasks: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate subtasks using conditional combination logic."""
        integrated_task = {
            "id": subtasks[0].get("original_task_id", f"conditional_{subtasks[0]['id']}"),
            "name": subtasks[0].get("name", "Conditional Task"),
            "description": "Task created by conditional combination of subtasks",
            "subtasks": [],
            "conditional_results": {},
            "status": "completed"
        }
        
        # Apply conditional logic based on subtask results
        for subtask in subtasks:
            subtask_info = {
                "subtask_id": subtask["id"],
                "status": subtask.get("status", "unknown")
            }
            
            integrated_task["subtasks"].append(subtask_info)
            
            # Apply simple conditional logic
            if "result" in subtask:
                result = subtask["result"]
                
                # Example: combine results based on success/failure
                if subtask.get("status") == "completed":
                    integrated_task["conditional_results"]["success"] = result
                else:
                    integrated_task["conditional_results"]["failure"] = result
        
        return integrated_task

    def _estimate_task_complexity(self, task: Dict[str, Any]) -> float:
        """Estimate the complexity of a task."""
        complexity = 1.0
        
        # Add complexity based on task size
        if "description" in task:
            complexity += min(2.0, len(task["description"]) / 100)
        
        # Add complexity based on dependencies
        dependencies = task.get("dependencies", [])
        complexity += min(1.5, len(dependencies) * 0.5)
        
        # Add complexity based on resources
        resources = task.get("required_resources", [])
        complexity += min(1.0, len(resources) * 0.3)
        
        # Add complexity based on deadline urgency
        if "deadline" in task:
            try:
                deadline = datetime.fromisoformat(task["deadline"])
                current_time = datetime.now()
                time_remaining = (deadline - current_time).total_seconds()
                
                if time_remaining > 0:
                    hours_remaining = time_remaining / 3600
                    urgency_factor = max(0, 1 - (math.log10(hours_remaining + 1) / 2))
                    complexity += min(1.0, urgency_factor)
            except (ValueError, TypeError):
                pass
        
        return min(5.0, complexity)

    def _analyze_task_components(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze task components for splitting."""
        components = []
        
        # Simple component analysis based on task description
        description = task.get("description", "")
        
        if "backend" in description.lower():
            components.append({
                "name": "Backend Implementation",
                "type": "backend",
                "description": "Backend component implementation",
                "complexity": 2.0,
                "resources": ["backend_server", "database"],
                "dependencies": []
            })
        
        if "frontend" in description.lower():
            components.append({
                "name": "Frontend Implementation",
                "type": "frontend",
                "description": "Frontend component implementation",
                "complexity": 1.5,
                "resources": ["frontend_framework", "ui_components"],
                "dependencies": ["backend"] if any(c["type"] == "backend" for c in components) else []
            })
        
        if "api" in description.lower():
            components.append({
                "name": "API Development",
                "type": "api",
                "description": "API development and integration",
                "complexity": 1.8,
                "resources": ["api_gateway", "auth_service"],
                "dependencies": []
            })
        
        if "testing" in description.lower():
            components.append({
                "name": "Testing",
                "type": "testing",
                "description": "Comprehensive testing of all components",
                "complexity": 1.2,
                "resources": ["test_framework", "test_data"],
                "dependencies": [c["name"].split()[0].lower() for c in components if c["type"] != "testing"]
            })
        
        # If no specific components found, create generic ones
        if not components:
            components.append({
                "name": "Main Implementation",
                "type": "main",
                "description": "Main task implementation",
                "complexity": 2.0,
                "resources": task.get("required_resources", []),
                "dependencies": []
            })
            
            components.append({
                "name": "Validation and Testing",
                "type": "validation",
                "description": "Validation and testing of implementation",
                "complexity": 1.0,
                "resources": [],
                "dependencies": ["main"]
            })
        
        return components

    def _group_dependencies(self, dependencies: List[str], context: Dict[str, Any]) -> List[List[str]]:
        """Group dependencies for task splitting."""
        dependency_groups = []
        
        # Simple grouping: create groups based on dependency types
        backend_deps = [dep for dep in dependencies if "backend" in dep.lower()]
        frontend_deps = [dep for dep in dependencies if "frontend" in dep.lower()]
        api_deps = [dep for dep in dependencies if "api" in dep.lower()]
        other_deps = [dep for dep in dependencies if dep not in backend_deps + frontend_deps + api_deps]
        
        if backend_deps:
            dependency_groups.append(backend_deps)
        if frontend_deps:
            dependency_groups.append(frontend_deps)
        if api_deps:
            dependency_groups.append(api_deps)
        if other_deps:
            dependency_groups.append(other_deps)
        
        # If no specific groups, create single group
        if not dependency_groups and dependencies:
            dependency_groups.append(dependencies)
        
        return dependency_groups

    def _log_task_splitting(self, original_task: Dict[str, Any], subtasks: List[Dict[str, Any]], strategy: str) -> None:
        """Log task splitting operation."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "task_splitting",
            "original_task_id": original_task["id"],
            "strategy": strategy,
            "subtask_count": len(subtasks),
            "original_complexity": self._estimate_task_complexity(original_task),
            "average_subtask_complexity": sum(self._estimate_task_complexity(subtask) for subtask in subtasks) / len(subtasks) if subtasks else 0
        }
        
        self.task_history.append(log_entry)
        self.splitting_metrics["total_splits"] += 1
        
        # Update average split size
        if len(subtasks) > 0:
            total_splits = self.splitting_metrics["total_splits"]
            current_avg = self.splitting_metrics["average_split_size"]
            new_avg = ((current_avg * (total_splits - 1)) + len(subtasks)) / total_splits
            self.splitting_metrics["average_split_size"] = new_avg
        
        # Keep history size manageable
        if len(self.task_history) > 50:
            self.task_history = self.task_history[-50:]

    def _log_task_integration(self, subtasks: List[Dict[str, Any]], integrated_task: Dict[str, Any], strategy: str) -> None:
        """Log task integration operation."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "task_integration",
            "integrated_task_id": integrated_task["id"],
            "strategy": strategy,
            "subtask_count": len(subtasks),
            "integration_status": integrated_task.get("status", "unknown")
        }
        
        self.task_history.append(log_entry)
        
        if integrated_task.get("status") == "completed":
            self.splitting_metrics["successful_integrations"] += 1
        
        # Keep history size manageable
        if len(self.task_history) > 50:
            self.task_history = self.task_history[-50:]

    def get_task_management_metrics(self) -> Dict[str, Any]:
        """Get task management metrics."""
        return {
            "splitting_metrics": self.splitting_metrics,
            "recent_operations": self.task_history[-5:] if self.task_history else [],
            "success_rate": self._calculate_integration_success_rate()
        }

    def _calculate_integration_success_rate(self) -> float:
        """Calculate the success rate of task integrations."""
        total = self.splitting_metrics["total_splits"]
        successful = self.splitting_metrics["successful_integrations"]
        
        if total > 0:
            return min(1.0, successful / total)
        return 0.0

    def get_splitting_recommendations(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommendations for splitting a task."""
        recommendations = []
        
        complexity = self._estimate_task_complexity(task)
        
        if complexity > 3.0:
            recommendations.append({
                "type": "complexity_based",
                "priority": "high",
                "message": f"High complexity task ({complexity:.1f}) - consider splitting",
                "suggested_strategy": "complexity_based",
                "estimated_subtasks": max(2, math.ceil(complexity / 2))
            })
        
        dependencies = task.get("dependencies", [])
        if len(dependencies) > 3:
            recommendations.append({
                "type": "dependency_based",
                "priority": "medium",
                "message": f"Task with many dependencies ({len(dependencies)}) - consider dependency-based splitting",
                "suggested_strategy": "dependency_based",
                "dependency_groups": len(self._group_dependencies(dependencies, {}))
            })
        
        resources = task.get("required_resources", [])
        if len(resources) > 2:
            recommendations.append({
                "type": "resource_based",
                "priority": "medium",
                "message": f"Task requiring multiple resources ({len(resources)}) - consider resource-based splitting",
                "suggested_strategy": "resource_based",
                "estimated_subtasks": len(resources)
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