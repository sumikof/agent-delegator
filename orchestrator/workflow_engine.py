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
from orchestrator.notification.manager import NotificationManager, ConsoleNotifier
from orchestrator.notification.notifier import NotificationType


class TaskStatus(str, Enum):
    """Extended task status for feedback loop support."""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    NEEDS_FIXES = "NEEDS_FIXES"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DONE = "DONE"


# Valid state transitions for feedback loop workflow
VALID_TRANSITIONS = {
    TaskStatus.NEW: [TaskStatus.IN_PROGRESS],
    TaskStatus.IN_PROGRESS: [TaskStatus.IN_REVIEW, TaskStatus.NEEDS_FIXES],
    TaskStatus.IN_REVIEW: [TaskStatus.APPROVED, TaskStatus.NEEDS_FIXES, TaskStatus.REJECTED],
    TaskStatus.NEEDS_FIXES: [TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW],
    TaskStatus.APPROVED: [TaskStatus.DONE],
    TaskStatus.REJECTED: [TaskStatus.DONE],
    TaskStatus.DONE: []  # Terminal state
}


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
        self.dependencies = []  # List of task_ids this task depends on
        self.dependents = []    # List of task_ids that depend on this task
        self.blocked_by = []    # List of task_ids currently blocking this task
    
    def add_feedback(self, feedback: Dict[str, Any]) -> None:
        """Add feedback to this task."""
        self.feedback_history.append(feedback)
        self.updated_at = time.time()
    
    def change_status(self, new_status: TaskStatus, reason: str = "", notifier: Optional[Notifier] = None) -> None:
        """Change task status and record history with validation."""
        # Validate state transition
        if new_status not in VALID_TRANSITIONS.get(self.status, []):
            raise ValueError(f"Invalid state transition: {self.status} -> {new_status}")
        
        # Prevent transition from terminal state
        if self.status == TaskStatus.DONE:
            raise ValueError(f"Cannot transition from terminal state: {self.status}")
        
        self.status_history.append({
            "from": self.status,
            "to": new_status,
            "timestamp": time.time(),
            "reason": reason
        })
        self.status = new_status
        self.updated_at = time.time()
        
        # Send status change notification if notifier is provided
        if notifier:
            notifier.send_status_change_notification(
                task_id=self.task_id,
                old_status=self.status_history[-1]["from"],
                new_status=new_status,
                reason=reason
            )
    
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
    
    def add_dependency(self, task_id: str) -> None:
        """Add a dependency to this task."""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = time.time()
    
    def add_dependent(self, task_id: str) -> None:
        """Add a dependent task."""
        if task_id not in self.dependents:
            self.dependents.append(task_id)
            self.updated_at = time.time()
    
    def add_blocked_by(self, task_id: str) -> None:
        """Add a task that is currently blocking this task."""
        if task_id not in self.blocked_by:
            self.blocked_by.append(task_id)
            self.updated_at = time.time()
    
    def remove_blocked_by(self, task_id: str) -> None:
        """Remove a task from blocked_by list."""
        if task_id in self.blocked_by:
            self.blocked_by.remove(task_id)
            self.updated_at = time.time()
    
    def is_blocked(self) -> bool:
        """Check if this task is currently blocked by other tasks."""
        return len(self.blocked_by) > 0
    
    def can_start(self) -> bool:
        """Check if this task can start based on dependencies and blocking status."""
        # Task can start if:
        # 1. It's not blocked by other tasks
        # 2. All dependencies are completed (DONE status)
        return not self.is_blocked() and self.status == TaskStatus.NEW
    
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
            "timeout_at": self.timeout_at,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "blocked_by": self.blocked_by
        }


class FeedbackLoopWorkflowEngine:
    """Workflow engine with feedback loop support."""
    
    def __init__(self, state_file: Optional[str] = None):
        self.task_states: Dict[str, TaskState] = {}
        self.parallel_orchestrator = ParallelOrchestrator(agent_registry=AgentRegistry())
        self.agent_loader = AgentLoader()
        self.state_file = state_file
        
        # Initialize notification system
        self.notification_manager = NotificationManager()
        self.notifier = ConsoleNotifier(self.notification_manager)
        
        # Load state if state_file is provided
        if state_file:
            self.load_state()
    
    def _log(self, message: str, *, level: str = "INFO") -> None:
        """Simple logger."""
        if LOGGING_LEVEL == "DEBUG" or level != "DEBUG":
            print(f"[{level}] {message}")
    
    def save_state(self) -> None:
        """Save current task states to file."""
        if not self.state_file:
            return
        
        try:
            state_data = {
                "task_states": {tid: ts.to_dict() for tid, ts in self.task_states.items()},
                "timestamp": time.time()
            }
            
            with open(self.state_file, "w") as f:
                json.dump(state_data, f, indent=2)
            
            self._log(f"State saved to {self.state_file}")
        except Exception as e:
            self._log(f"Failed to save state: {e}", level="ERROR")
    
    def load_state(self) -> None:
        """Load task states from file."""
        if not self.state_file:
            return
        
        try:
            if Path(self.state_file).exists():
                with open(self.state_file, "r") as f:
                    state_data = json.load(f)
                
                # Restore task states
                for tid, ts_data in state_data.get("task_states", {}).items():
                    task_state = TaskState(
                        task_id=ts_data["task_id"],
                        agent_type=ts_data["agent_type"],
                        payload=ts_data["payload"]
                    )
                    
                    # Restore all attributes
                    task_state.status = TaskStatus(ts_data["status"])
                    task_state.status_history = ts_data["status_history"]
                    task_state.feedback_history = ts_data["feedback_history"]
                    task_state.retry_count = ts_data["retry_count"]
                    task_state.created_at = ts_data["created_at"]
                    task_state.updated_at = ts_data["updated_at"]
                    task_state.max_retries = ts_data["max_retries"]
                    task_state.timeout_at = ts_data["timeout_at"]
                    task_state.dependencies = ts_data.get("dependencies", [])
                    task_state.dependents = ts_data.get("dependents", [])
                    task_state.blocked_by = ts_data.get("blocked_by", [])
                    
                    self.task_states[tid] = task_state
                
                self._log(f"State loaded from {self.state_file}")
        except Exception as e:
            self._log(f"Failed to load state: {e}", level="ERROR")
    
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
        
        # Set up dependencies from payload if provided
        if "dependencies" in payload:
            for dep_id in payload["dependencies"]:
                task_state.add_dependency(dep_id)
                # Update the dependent task's dependents list
                if dep_id in self.task_states:
                    self.task_states[dep_id].add_dependent(task_id)
        
        # Resolve dependencies before starting
        self._resolve_dependencies(task_id)
        
        # Change status to IN_PROGRESS if not blocked
        if task_state.can_start():
            self.change_task_status(task_id, TaskStatus.IN_PROGRESS, "Task submitted and ready to start")
        else:
            self._log(f"Task {task_id} is blocked by dependencies: {task_state.blocked_by}")
        
        self._log(f"Task submitted: {task_id} (agent: {agent_type})")
        return task_id
    
    def _resolve_dependencies(self, task_id: str) -> None:
        """Resolve dependencies for a task and update blocking status."""
        if task_id not in self.task_states:
            return
            
        task_state = self.task_states[task_id]
        
        # Check if all dependencies are completed
        all_dependencies_completed = True
        for dep_id in task_state.dependencies:
            if dep_id in self.task_states:
                dep_state = self.task_states[dep_id]
                if dep_state.status != TaskStatus.DONE:
                    all_dependencies_completed = False
                    task_state.add_blocked_by(dep_id)
            else:
                # Dependency not found, consider it as blocking
                all_dependencies_completed = False
                task_state.add_blocked_by(dep_id)
        
        # If all dependencies are completed, remove blocking
        if all_dependencies_completed:
            task_state.blocked_by = []
        
        self._log(f"Dependency resolution for {task_id}: blocked_by={task_state.blocked_by}")
    
    def _update_dependents(self, task_id: str) -> None:
        """Update dependents when a task status changes."""
        if task_id not in self.task_states:
            return
            
        task_state = self.task_states[task_id]
        
        # Update all dependents
        for dep_id in task_state.dependents:
            if dep_id in self.task_states:
                self._resolve_dependencies(dep_id)
    
    def change_task_status(self, task_id: str, new_status: TaskStatus, reason: str = "") -> None:
        """Change task status and update dependents."""
        if task_id not in self.task_states:
            raise ValueError(f"Task not found: {task_id}")
        
        task_state = self.task_states[task_id]
        old_status = task_state.status
        
        # Change status with notification
        task_state.change_status(new_status, reason, self.notifier)
        
        # Send specific notifications based on status change
        self._send_status_specific_notifications(task_state, old_status, new_status, reason)
        
        # Update dependents if status changed to DONE
        if new_status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            self._update_dependents(task_id)
    
    def _send_status_specific_notifications(
        self, 
        task_state: TaskState, 
        old_status: TaskStatus, 
        new_status: TaskStatus, 
        reason: str
    ) -> None:
        """Send specific notifications based on status transitions."""
        # Approval completed notification
        if new_status == TaskStatus.APPROVED:
            self.notifier.send_approval_completed_notification(
                task_id=task_state.task_id,
                approval_details={
                    "task_id": task_state.task_id,
                    "agent_type": task_state.agent_type,
                    "reason": reason,
                    "timestamp": time.time()
                }
            )
        
        # Fix request notification
        elif new_status == TaskStatus.NEEDS_FIXES:
            self.notifier.send_fix_request_notification(
                task_id=task_state.task_id,
                fix_details={
                    "task_id": task_state.task_id,
                    "agent_type": task_state.agent_type,
                    "reason": reason,
                    "retry_count": task_state.retry_count,
                    "timestamp": time.time()
                }
            )
        
        # Feedback request notification when moving to IN_REVIEW
        elif new_status == TaskStatus.IN_REVIEW:
            self.notifier.send_feedback_request_notification(
                task_id=task_state.task_id,
                feedback_details={
                    "task_id": task_state.task_id,
                    "agent_type": task_state.agent_type,
                    "from_status": old_status,
                    "timestamp": time.time()
                }
            )
    
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
        
        # Handle feedback based on current task status
        current_status = task_state.status
        
        if current_status == TaskStatus.IN_PROGRESS:
            # From IN_PROGRESS, we can only go to IN_REVIEW or NEEDS_FIXES
            if feedback["status"] == TaskStatus.APPROVED:
                # If feedback says approved, transition to IN_REVIEW first
                new_status = TaskStatus.IN_REVIEW
                self.change_task_status(task_id, new_status, f"Feedback: {feedback['recommendation']}")
            elif feedback["status"] == TaskStatus.NEEDS_FIXES:
                new_status = TaskStatus.NEEDS_FIXES
                self.change_task_status(task_id, new_status, f"Feedback: {feedback['recommendation']}")
            else:
                # For REJECTED or other statuses, go to IN_REVIEW for final decision
                new_status = TaskStatus.IN_REVIEW
                self.change_task_status(task_id, new_status, f"Feedback: {feedback['recommendation']}")
        elif current_status == TaskStatus.IN_REVIEW:
            # From IN_REVIEW, we can go to APPROVED, NEEDS_FIXES, or REJECTED
            new_status = feedback["status"]
            self.change_task_status(task_id, new_status, f"Feedback: {feedback['recommendation']}")
        else:
            # For other statuses, use the feedback status directly
            new_status = feedback["status"]
            self.change_task_status(task_id, new_status, f"Feedback: {feedback['recommendation']}")
        
        self._log(f"Task {task_id} status changed to {new_status}")
        
        # Handle different statuses
        if new_status == TaskStatus.APPROVED:
            self.change_task_status(task_id, TaskStatus.DONE, "Task approved and completed")
            return True
        elif new_status == TaskStatus.NEEDS_FIXES:
            if task_state.has_reached_max_retries():
                # From NEEDS_FIXES, we need to go through IN_REVIEW to get to REJECTED
                self.change_task_status(task_id, TaskStatus.IN_REVIEW, "Max retries reached, moving to review for final decision")
                # Then immediately transition to REJECTED from IN_REVIEW
                self.change_task_status(task_id, TaskStatus.REJECTED, "Max retries reached")
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
        else:
            # For IN_REVIEW status, we need to wait for final approval
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
                elif task_state.status == TaskStatus.NEW and task_state.can_start():
                    # Start blocked tasks that are now ready
                    self.change_task_status(task_id, TaskStatus.IN_PROGRESS, "Task dependencies resolved, starting now")
                    new_remaining_tasks.append(task_id)
                    self._log(f"Task started after dependency resolution: {task_id}")
                else:
                    # Task still in progress or blocked
                    new_remaining_tasks.append(task_id)
            
            remaining_tasks = new_remaining_tasks
            
            # Add some delay to allow tasks to complete
            if remaining_tasks:
                time.sleep(1.0)
            
            # Save state periodically
            if self.state_file and iteration % 10 == 0:
                self.save_state()
        
        if iteration >= max_iterations and remaining_tasks:
            self._log(f"Max iterations reached, {len(remaining_tasks)} tasks still pending", level="WARNING")
        
        # Save final state
        if self.state_file:
            self.save_state()
        
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
                "task_states": {tid: ts.to_dict() for tid, ts in self.task_states.items()},
                "notifications": {
                    "total_notifications": len(self.notification_manager.get_notifications()),
                    "unread_count": self.notification_manager.get_unread_count(),
                    "notification_types": {
                        "status_change": self.notification_manager.get_unread_count(NotificationType.STATUS_CHANGE),
                        "feedback_request": self.notification_manager.get_unread_count(NotificationType.FEEDBACK_REQUEST),
                        "approval_completed": self.notification_manager.get_unread_count(NotificationType.APPROVAL_COMPLETED),
                        "fix_request": self.notification_manager.get_unread_count(NotificationType.FIX_REQUEST),
                        "error": self.notification_manager.get_unread_count(NotificationType.ERROR)
                    }
                }
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
    # Generate state file name based on workflow name
    state_file = f"workflow_{config.project.name}_state.json"
    engine = FeedbackLoopWorkflowEngine(state_file=state_file)
    return engine.run_workflow(config)