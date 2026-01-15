"""Orchestrator entry point.

This module provides a minimal skeleton for executing a workflow configuration.
It loads a workflow file, validates it using the existing ``ConfigLoader`` and
``ConfigValidator`` utilities, and then iterates over the defined stages.

Each stage contains a list of agent IDs. The actual agent execution is out of
scope for the initial skeleton – we simply log the intended execution order and
return a summary response that conforms to the common response schema defined in
``response_schema.json``.

The implementation is deliberately lightweight to allow incremental development
of concrete agent classes later in the project.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from orchestrator.config.models import WorkflowConfig
from typing import List, Optional

from orchestrator.config.loader import ConfigLoader
from orchestrator.config.validator import ConfigValidator
from orchestrator.utils.constants import LOGGING_LEVEL
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry
from orchestrator.coordination import conflict_resolution_system
from orchestrator.plugin.registry import PluginRegistry
from orchestrator.plugin.loader import PluginLoader
from orchestrator.plugin.manager import PluginManager
from orchestrator.monitoring.metrics_collector import MetricsCollector
from orchestrator.monitoring.resource_monitor import ResourceMonitor
from orchestrator.monitoring.stability_tracker import StabilityTracker
from orchestrator.self_organizing.engine import SelfOrganizingEngine
from orchestrator.self_organizing.adaptation import AdaptationAlgorithm
from orchestrator.self_organizing.role_assignment import RoleAssignmentSystem
from orchestrator.self_organizing.communication import CommunicationTopologyManager


# Import feedback loop workflow engine
from orchestrator.workflow_engine import run_workflow_with_feedback


# Global monitoring system instances
metrics_collector = None
resource_monitor = None
stability_tracker = None

# Global self-organizing system instances
self_organizing_engine = None
adaptation_algorithm = None
role_assignment_system = None
communication_topology_manager = None


# Simple logger – in a full implementation this would be replaced by a structured
# logging system defined in ``orchestrator/logging.py``.
def _log(message: str, *, level: str = "INFO") -> None:
    if LOGGING_LEVEL == "DEBUG" or level != "DEBUG":
        print(f"[{level}] {message}")


def _load_and_validate(workflow_path: Path) -> "WorkflowConfig":
    """Load a workflow file and validate it.

    Returns the parsed ``WorkflowConfig`` model on success; exits the process on
    validation failure.
    """
    loader = ConfigLoader()
    validator = ConfigValidator()

    # Load raw YAML for schema validation
    raw_docs = loader._load_yaml_file(workflow_path)
    workflow_dict = raw_docs[0] if isinstance(raw_docs, list) else raw_docs

    is_valid, errors = validator.validate_workflow(workflow_dict)
    if not is_valid:
        _log("Workflow validation failed:", level="ERROR")
        for err in errors:
            _log(f"  - {err}", level="ERROR")
        sys.exit(1)

    # Pydantic validation (will raise ValidationError on failure)
    try:
        config = loader.load_workflow(workflow_path)
    except Exception as exc:  # pragma: no cover – defensive
        _log(f"Pydantic validation error: {exc}", level="ERROR")
        sys.exit(1)

    _log("Workflow configuration loaded and validated successfully")
    return config


def _execute_stage(stage_name: str, agents: List[str], config: WorkflowConfig) -> List[Dict[str, Any]]:
    """Execute a stage by running all agents in sequence.

    Args:
        stage_name: The name of the stage being executed.
        agents: List of agent IDs to execute.
        config: The workflow configuration.

    Returns:
        List of agent execution results.
    """
    _log(f"Executing stage '{stage_name}' with agents: {', '.join(agents)}")
    
    # Import agent loader
    from orchestrator.agents.loader import loader
    
    results = []
    
    for agent_id in agents:
        try:
            # Load the agent instance
            agent = loader.load_agent(agent_id)
            
            # Create context for this agent execution
            context = {
                "stage": stage_name,
                "agent_id": agent_id,
                "workflow_config": config.model_dump(),
                "project": config.project.model_dump() if config.project else {},
                "workflow": config.workflow.model_dump() if config.workflow else {}
            }
            
            # Execute the agent with monitoring
            _log(f"  Executing agent '{agent_id}'...")
            
            # Start monitoring context
            with metrics_collector.start_agent_monitoring(agent_id, f"{stage_name}_{agent_id}") as monitor:
                result = agent.run(context)
            
            # Record monitoring data and stability events
            if result.get('status') == 'ERROR':
                stability_tracker.record_error(
                    agent_name=agent_id,
                    task_name=f"{stage_name}_{agent_id}",
                    error_message=result.get('findings', [{}])[0].get('message', 'Unknown error'),
                    severity='error'
                )
            
            # Store the result
            results.append(result)
            _log(f"  Agent '{agent_id}' completed with status: {result.get('status', 'UNKNOWN')}")
            
        except Exception as e:
            _log(f"  Error executing agent '{agent_id}': {str(e)}", level="ERROR")
            
            # Record crash event
            stability_tracker.record_crash(
                agent_name=agent_id,
                task_name=f"{stage_name}_{agent_id}",
                error_message=str(e)
            )
            
            results.append({
                "status": "ERROR",
                "summary": f"Failed to execute agent {agent_id}",
                "findings": [{
                    "severity": "ERROR",
                    "message": str(e),
                    "ref": f"agent_execution_{agent_id}"
                }],
                "artifacts": [],
                "next_actions": [],
                "context": {"error": str(e)},
                "trace_id": "error-trace-id",
                "execution_time_ms": 0
            })
    
    return results


def run(workflow_file: str, use_parallel: bool = False, use_feedback_loop: bool = False) -> dict:
    """Run the orchestrator against a workflow file.

    Returns a JSON‑serialisable dictionary matching the common response schema.
    """
    workflow_path = Path(workflow_file)
    config = _load_and_validate(workflow_path)
    
    # Initialize plugin system
    plugin_registry = PluginRegistry()
    plugin_loader = PluginLoader(plugin_registry)
    
    # Load built-in plugins
    plugin_loader.load_plugins_from_directory("orchestrator/plugins")
    
    # Create plugin manager (we'll use a simple context manager for now)
    from orchestrator.context import ContextManager
    context_manager = ContextManager()
    plugin_manager = PluginManager(plugin_registry, context_manager)
    
    # Initialize monitoring system
    global metrics_collector, resource_monitor, stability_tracker
    metrics_collector = MetricsCollector()
    resource_monitor = ResourceMonitor()
    stability_tracker = StabilityTracker()
    
    # Initialize self-organizing system
    global self_organizing_engine, adaptation_algorithm, role_assignment_system, communication_topology_manager
    
    # Create agent registry for self-organizing system
    agent_registry = AgentRegistry()
    
    # Initialize self-organizing components
    adaptation_algorithm = AdaptationAlgorithm()
    role_assignment_system = RoleAssignmentSystem()
    communication_topology_manager = CommunicationTopologyManager()
    
    # Initialize self-organizing engine
    self_organizing_engine = SelfOrganizingEngine(agent_registry, metrics_collector)
    
    # Register agents with role assignment system
    for agent_id, agent_info in agent_registry.get_all_agents().items():
        capabilities = agent_info.get("capabilities", [])
        current_role = agent_info.get("current_role", "idle")
        performance_score = agent_info.get("performance_score", 0.5)
        role_assignment_system.register_agent(agent_id, capabilities, current_role, performance_score)
    
    # Initialize communication topology
    agent_ids = list(agent_registry.get_all_agents().keys())
    communication_topology_manager.initialize_topology(agent_ids)

    try:
        if use_feedback_loop:
            return run_workflow_with_feedback(workflow_path)
        elif use_parallel:
            return _run_parallel_workflow(config, plugin_manager)
        else:
            return _run_sequential_workflow(config, plugin_manager)
    finally:
        # Shutdown monitoring system
        if metrics_collector:
            metrics_collector.shutdown()
        if resource_monitor:
            resource_monitor.shutdown()
        if stability_tracker:
            stability_tracker.shutdown()


def _run_sequential_workflow(config: WorkflowConfig, plugin_manager: PluginManager) -> dict:
    """Run workflow using sequential execution (original implementation)."""
    import time
    import uuid
    
    start_time = time.time()
    all_results = []
    
    # Iterate over stages in order
    for stage in config.workflow.stages:
        stage_results = _execute_stage(stage.name, stage.agents, config)
        all_results.extend(stage_results)
        
        # Check if system adaptation is needed after each stage
        if self_organizing_engine and self_organizing_engine.evaluate_adaptation_needed():
            _log("System adaptation triggered after stage completion")
            adaptation_result = self_organizing_engine.adapt_system()
            _log(f"Adaptation result: {adaptation_result['status']}")
            
            if adaptation_result['status'] == 'adapted':
                # Update role assignment based on new structure
                current_structure = self_organizing_engine.get_system_state()
                role_assignment = {}
                for agent_id, profile in current_structure.agent_profiles.items():
                    role_assignment[agent_id] = profile.current_role
                
                # Update communication topology
                new_topology = communication_topology_manager.optimize_topology(
                    role_assignment, 
                    metrics_collector.get_current_metrics()
                )
                communication_topology_manager.update_topology(new_topology)
                
                _log("System structure adapted successfully")

    execution_time = time.time() - start_time
    
    # Build response with execution details
    response = {
        "status": "OK",
        "summary": f"Workflow '{config.project.name}' executed successfully",
        "findings": [],
        "artifacts": [],
        "next_actions": [],
        "context": {
            "plugins_loaded": plugin_manager.list_active_plugins(),
            "available_plugins": plugin_manager.registry.list_plugins(),
            "execution_results": all_results,
            "stage_count": len(config.workflow.stages),
            "agent_execution_count": len(all_results)
        },
        "trace_id": str(uuid.uuid4()),
        "execution_time_ms": int(execution_time * 1000),
    }
    
    # Add monitoring data to response
    if metrics_collector:
        response["monitoring"] = {
            "performance_metrics": metrics_collector.get_aggregated_stats(),
            "resource_usage": resource_monitor.get_aggregated_stats(),
            "stability": stability_tracker.get_aggregated_stats()
        }
    
    # Add self-organizing system data to response
    if self_organizing_engine:
        response["self_organizing"] = {
            "system_state": {
                "agent_count": len(self_organizing_engine.get_system_state().agent_profiles),
                "adaptation_count": 1 if adaptation_result and adaptation_result['status'] == 'adapted' else 0,
                "last_adaptation_time": self_organizing_engine.last_adaptation_time
            },
            "communication_topology": {
                "link_count": len(communication_topology_manager.get_current_topology().links),
                "cluster_count": len(communication_topology_manager.get_current_topology().clusters)
            },
            "role_distribution": role_assignment_system.get_current_role_distribution()
        }
    
    return response


def _run_parallel_workflow(config: WorkflowConfig, plugin_manager: PluginManager) -> dict:
    """Run workflow using parallel execution."""
    import time
    import uuid
    
    start_time = time.time()
    
    # Start conflict resolution monitoring
    conflict_resolution_system.start_monitoring()
    
    # Create parallel orchestrator
    orchestrator = ParallelOrchestrator(agent_registry=AgentRegistry())
    
    # Submit tasks for all stages
    task_ids = []
    for stage in config.workflow.stages:
        for agent in stage.agents:
            task_id = orchestrator.submit_task(
                agent_type=agent,
                payload={
                    "stage": stage.name,
                    "config": config.dict(),
                    "workflow": config.workflow.dict()
                }
            )
            task_ids.append(task_id)
    
    # Wait for all tasks to complete
    for task_id in task_ids:
        orchestrator.wait_for_completion(task_id)
    
    # Collect results
    results = []
    for task_id in task_ids:
        result = orchestrator.get_task_result(task_id)
        if result:
            results.append(result)
    
    # Stop conflict resolution monitoring
    conflict_resolution_system.stop_monitoring()
    
    # Shutdown orchestrator
    orchestrator.shutdown()
    
    execution_time = time.time() - start_time
    
    # Build response
    response = {
        "status": "OK",
        "summary": f"Parallel workflow '{config.project.name}' executed successfully",
        "findings": [
            {
                "severity": "INFO",
                "message": f"Executed {len(task_ids)} tasks in parallel",
                "ref": "parallel_execution"
            }
        ],
        "artifacts": [],
        "next_actions": [],
        "context": {
            "parallel_execution": True,
            "task_count": len(task_ids),
            "execution_time_ms": int(execution_time * 1000),
            "conflict_resolution": conflict_resolution_system.get_system_status(),
            "plugins_loaded": plugin_manager.list_active_plugins(),
            "available_plugins": plugin_manager.registry.list_plugins()
        },
        "trace_id": str(uuid.uuid4()),
        "execution_time_ms": int(execution_time * 1000),
    }
    
    # Add monitoring data to response
    if metrics_collector:
        response["monitoring"] = {
            "performance_metrics": metrics_collector.get_aggregated_stats(),
            "resource_usage": resource_monitor.get_aggregated_stats(),
            "stability": stability_tracker.get_aggregated_stats()
        }
    
    return response


def main() -> None:
    if len(sys.argv) != 2:
        _log("Usage: python -m orchestrator.main <workflow.yaml>", level="ERROR")
        sys.exit(1)
    result = run(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
