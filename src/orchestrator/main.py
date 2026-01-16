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


# Import feedback loop workflow engine
from orchestrator.workflow_engine import run_workflow_with_feedback


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


def _execute_stage(stage_name: str, agents: List[str]) -> None:
    """Placeholder for stage execution.

    In a complete system each agent ID would be resolved to an implementation
    class and its ``run`` method invoked. For now we simply log the intended
    actions.
    """
    _log(f"Executing stage '{stage_name}' with agents: {', '.join(agents)}")
    # TODO: Resolve agents and invoke their execution logic.


def run(workflow_file: str, use_parallel: bool = False, use_feedback_loop: bool = False) -> dict:
    """Run the orchestrator against a workflow file.

    Returns a JSON‑serialisable dictionary matching the common response schema.
    """
    workflow_path = Path(workflow_file)
    config = _load_and_validate(workflow_path)

    if use_feedback_loop:
        return run_workflow_with_feedback(workflow_path)
    elif use_parallel:
        return _run_parallel_workflow(config)
    else:
        return _run_sequential_workflow(config)


def _run_sequential_workflow(config: WorkflowConfig) -> dict:
    """Run workflow using sequential execution (original implementation)."""
    # Iterate over stages in order
    for stage in config.workflow.stages:
        _execute_stage(stage.name, stage.agents)

    # Build a minimal success response
    response = {
        "status": "OK",
        "summary": f"Workflow '{config.project.name}' executed successfully",
        "findings": [],
        "artifacts": [],
        "next_actions": [],
        "context": {},
        "trace_id": "${{uuid4()}}",  # placeholder – real implementation would generate a UUID
        "execution_time_ms": 0,
    }
    return response


def _run_parallel_workflow(config: WorkflowConfig) -> dict:
    """Run workflow using parallel execution."""
    import time
    import uuid
    
    start_time = time.time()
    
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
            "execution_time_ms": int(execution_time * 1000)
        },
        "trace_id": str(uuid.uuid4()),
        "execution_time_ms": int(execution_time * 1000),
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
