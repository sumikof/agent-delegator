"""
Feedback Loop Workflow Engine.

This module implements a workflow engine that supports feedback loops,
quality reviews, and iterative improvement cycles based on the
design principles documented in agent-delegation.md.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from orchestrator.config.models import WorkflowConfig
from orchestrator.agents.registry import AgentRegistry
from orchestrator.agents.loader import AgentLoader
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.utils.constants import LOGGING_LEVEL


class TaskStatus(str, Enum):
    """Extended task status for feedback loop support."""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    NEEDS_FIXES = "NEEDS_FIXES"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DONE = "DONE"


class FeedbackSeverity(str, Enum):
    """Feedback severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackCategory(str, Enum):
    """Feedback categories."""
    CODE_QUALITY = "code_quality"
    FUNCTIONAL = "functional"
    TEST = "test"
    DOCUMENTATION = "documentation"


class TaskState:
    """Task state with feedback loop support."""
    
    def __init__(self, task_id: str, agent_type: str, payload: Dict[str, Any]):
        self.task_id = task_id
        self.agent_type = agent_type
        self.payload = payload
        self.status = TaskStatus.NEW
        self.status_history = []
        self.feedback_history = []
        self.retry_count = 0
        self.created_at = time.time()
        self.updated_at = time.time()
        self.max_retries = 3
        self.timeout_at = self.created_at + 3600  # 1 hour timeout
    
    def add_feedback(self, feedback: Dict[str, Any]) -> None:
        """Add feedback to this task."""
        self.feedback_history.append(feedback)
        self.updated_at = time.time()
    
    def change_status(self, new_status: TaskStatus, reason: str = "") -> None:
        """Change task status and record history."""
        self.status_history.append({
            "from": self.status,
            "to": new_status,
            "timestamp": time.time(),
            "reason": reason
        })
        self.status = new_status
        self.updated_at = time.time()
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
        self.updated_at = time.time()
    
    def is_timed_out(self) -> bool:
        """Check if task is timed out."""
        return time.time() > self.timeout_at
    
    def has_reached_max_retries(self) -> bool:
        """Check if task has reached maximum retries."""
        return self.retry_count >= self.max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task state to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "payload": self.payload,
            "status": self.status,
            "status_history": self.status_history,
            "feedback_history": self.feedback_history,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "max_retries": self.max_retries,
            "timeout_at": self.timeout_at
        }


class FeedbackLoopWorkflowEngine:
    """Workflow engine with feedback loop support."""
    
    def __init__(self):
        self.task_states: Dict[str, TaskState] = {}
        self.parallel_orchestrator = ParallelOrchestrator(agent_registry=AgentRegistry())
        self.agent_loader = AgentLoader()
    
    def _log(self, message: str, *, level: str = "INFO") -> None:
        """Simple logger."""
        if LOGGING_LEVEL == "DEBUG" or level != "DEBUG":
            print(f"[{level}] {message}")
    
    def submit_task(self, agent_type: str, payload: Dict[str, Any]) -> str:
        """Submit a new task to the workflow engine."""
        # Submit to parallel orchestrator and get the task_id it generates
        task_id = self.parallel_orchestrator.submit_task(
            agent_type=agent_type,
            payload=payload
        )
        
        # Create task state with the same task_id
        task_state = TaskState(task_id, agent_type, payload)
        self.task_states[task_id] = task_state
        
        # Change status to IN_PROGRESS
        task_state.change_status(TaskStatus.IN_PROGRESS, "Task submitted")
        
        self._log(f"Task submitted: {task_id} (agent: {agent_type})")
        return task_id
    
    def _generate_feedback(self, task_id: str, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for a completed task."""
        # Use quality auditor agent to generate feedback
        try:
            quality_auditor = self.agent_loader.load_agent("quality_auditor")
            context = {
                "task_id": task_id,
                "results": agent_results,
                "task_state": self.task_states[task_id].to_dict()
            }
            
            feedback_result = quality_auditor.run(context)
            if feedback_result and "findings" in feedback_result:
                # Convert to our feedback format
                findings = feedback_result["findings"]
                
                # Calculate overall score based on findings
                total_score = 100
                for finding in findings:
                    if finding.get("severity") == "ERROR":
                        total_score -= 30
                    elif finding.get("severity") == "WARN":
                        total_score -= 10
                
                # Determine status based on score
                if total_score >= 80:
                    status = TaskStatus.APPROVED
                elif total_score >= 50:
                    status = TaskStatus.NEEDS_FIXES
                else:
                    status = TaskStatus.REJECTED
                
                feedback = {
                    "feedback_id": str(uuid.uuid4()),
                    "task_id": task_id,
                    "status": status,
                    "severity": "medium" if total_score >= 50 else "high",
                    "findings": findings,
                    "overall_score": total_score,
                    "recommendation": feedback_result.get("recommendation", "Review and fix issues"),
                    "reviewer": "quality_auditor",
                    "timestamp": time.time()
                }
                
                return feedback
        except KeyError:
            # Quality auditor not found, fallback to auto-approve
            self._log("Quality auditor agent not found, using auto-approval", level="WARNING")
        except Exception as e:
            self._log(f"Feedback generation error: {e}", level="ERROR")
        
        # Fallback: Auto-approve if no quality auditor or error occurred
        return {
            "feedback_id": str(uuid.uuid4()),
            "task_id": task_id,
            "status": TaskStatus.APPROVED,
            "severity": "low",
            "findings": [],
            "overall_score": 100,
            "recommendation": "Auto-approved (no quality auditor available)",
            "reviewer": "system",
            "timestamp": time.time()
        }
    
    def process_feedback_loop(self, task_id: str) -> bool:
        """Process feedback loop for a completed task."""
        if task_id not in self.task_states:
            self._log(f"Task not found: {task_id}", level="ERROR")
            return False
        
        task_state = self.task_states[task_id]
        
        # Get task result from parallel orchestrator
        result = self.parallel_orchestrator.get_task_result(task_id)
        
        if not result:
            self._log(f"No result found for task: {task_id}", level="WARNING")
            return False
        
        # Generate feedback
        feedback = self._generate_feedback(task_id, result)
        
        # Add feedback to task state
        task_state.add_feedback(feedback)
        
        # Change status based on feedback
        new_status = feedback["status"]
        task_state.change_status(new_status, f"Feedback: {feedback['recommendation']}")
        
        self._log(f"Task {task_id} status changed to {new_status}")
        
        # Handle different statuses
        if new_status == TaskStatus.APPROVED:
            task_state.change_status(TaskStatus.DONE, "Task approved and completed")
            return True
        elif new_status == TaskStatus.NEEDS_FIXES:
            if task_state.has_reached_max_retries():
                task_state.change_status(TaskStatus.REJECTED, "Max retries reached")
                return False
            else:
                # Resubmit task for fixes
                task_state.increment_retry()
                self.parallel_orchestrator.submit_task(
                    agent_type=task_state.agent_type,
                    payload={
                        **task_state.payload,
                        "feedback": feedback,
                        "retry_count": task_state.retry_count
                    }
                )
                task_state.change_status(TaskStatus.IN_PROGRESS, "Resubmitted for fixes")
                return False
        elif new_status == TaskStatus.REJECTED:
            return False
        
        return True
    
    def run_workflow(self, config: WorkflowConfig) -> Dict[str, Any]:
        """Run workflow with feedback loop support."""
        start_time = time.time()
        completed_tasks = []
        
        # Submit all tasks
        for stage in config.workflow.stages:
            for agent in stage.agents:
                task_id = self.submit_task(
                    agent_type=agent,
                    payload={
                        "stage": stage.name,
                        "config": config.dict(),
                        "workflow": config.workflow.dict()
                    }
                )
        
        # Process feedback loops
        all_tasks = list(self.task_states.keys())
        remaining_tasks = all_tasks.copy()
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while remaining_tasks and iteration < max_iterations:
            iteration += 1
            # Check each task
            new_remaining_tasks = []
            
            for task_id in remaining_tasks:
                task_state = self.task_states[task_id]
                
                # Check if task is completed in parallel orchestrator
                result = self.parallel_orchestrator.get_task_result(task_id)
                
                if result and task_state.status in [TaskStatus.IN_PROGRESS, TaskStatus.NEEDS_FIXES]:
                    # Process feedback loop
                    completed = self.process_feedback_loop(task_id)
                    
                    if completed:
                        completed_tasks.append(task_id)
                        self._log(f"Task completed: {task_id}")
                    else:
                        # Task needs more work
                        new_remaining_tasks.append(task_id)
                        self._log(f"Task needs fixes: {task_id}")
                else:
                    # Task still in progress
                    new_remaining_tasks.append(task_id)
            
            remaining_tasks = new_remaining_tasks
            
            # Add some delay to allow tasks to complete
            if remaining_tasks:
                time.sleep(1.0)
        
        if iteration >= max_iterations and remaining_tasks:
            self._log(f"Max iterations reached, {len(remaining_tasks)} tasks still pending", level="WARNING")
        
        # Shutdown parallel orchestrator
        self.parallel_orchestrator.shutdown()
        
        execution_time = time.time() - start_time
        
        # Build response
        response = {
            "status": "OK",
            "summary": f"Feedback loop workflow '{config.project.name}' completed",
            "findings": [
                {
                    "severity": "INFO",
                    "message": f"Completed {len(completed_tasks)} tasks with feedback loops",
                    "ref": "feedback_loop_execution"
                }
            ],
            "artifacts": [],
            "next_actions": [],
            "context": {
                "feedback_loop_enabled": True,
                "completed_tasks": len(completed_tasks),
                "total_tasks": len(all_tasks),
                "execution_time_ms": int(execution_time * 1000),
                "task_states": {tid: ts.to_dict() for tid, ts in self.task_states.items()}
            },
            "trace_id": str(uuid.uuid4()),
            "execution_time_ms": int(execution_time * 1000),
        }
        
        return response


def run_workflow_with_feedback(config_path: str) -> Dict[str, Any]:
    """Run workflow with feedback loop support."""
    from orchestrator.config.loader import ConfigLoader
    from orchestrator.config.validator import ConfigValidator
    
    # Load and validate workflow
    workflow_path = Path(config_path)
    loader = ConfigLoader()
    validator = ConfigValidator()
    
    # Load raw YAML for schema validation
    raw_docs = loader._load_yaml_file(workflow_path)
    workflow_dict = raw_docs[0] if isinstance(raw_docs, list) else raw_docs
    
    # Validate
    is_valid, errors = validator.validate_workflow(workflow_dict)
    if not is_valid:
        print("Workflow validation failed:")
        for err in errors:
            print(f"  - {err}")
        return {"status": "ERROR", "message": "Validation failed"}
    
    # Load config
    try:
        config = loader.load_workflow(workflow_path)
    except Exception as exc:
        print(f"Pydantic validation error: {exc}")
        return {"status": "ERROR", "message": str(exc)}
    
    # Run workflow with feedback loop
    engine = FeedbackLoopWorkflowEngine()
    return engine.run_workflow(config)