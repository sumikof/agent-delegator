"""
Parallel Processing Orchestrator.

This module integrates all parallel processing components to provide
a high-level interface for parallel agent execution.
"""

import threading
import time
import numpy as np
from typing import Any, Dict, List, Optional

from orchestrator.context import ContextManager
from orchestrator.agents.registry import AgentRegistry, registry

from .task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from .worker_pool import WorkerPool
from .load_balancer import LoadBalancer
from .monitor import ResourceMonitor

# Brainwave interface integration
try:
    from orchestrator.interfaces.brainwave.adapter import BrainwaveAgentAdapter
    from orchestrator.interfaces.brainwave.processor import BrainwaveProcessor
except ImportError:
    # Fallback for when brainwave interface is not available
    BrainwaveAgentAdapter = None
    BrainwaveProcessor = None

# Predictive UI interface integration
try:
    from orchestrator.interfaces.predictive_ui.adapter import PredictiveUIAdapter
except ImportError:
    # Fallback for when predictive UI interface is not available
    PredictiveUIAdapter = None

# Personalized experience interface integration
try:
    from orchestrator.interfaces.personalized_experience.integrator import PersonalizedExperienceIntegrator
except ImportError:
    # Fallback for when personalized experience interface is not available
    PersonalizedExperienceIntegrator = None


class ParallelOrchestrator:
    """High-level orchestrator for parallel agent execution."""

    def __init__(self, max_workers: int = 4, agent_registry: Optional[AgentRegistry] = None, 
                 enable_brainwave: bool = False, enable_predictive_ui: bool = False, 
                 enable_personalized_experience: bool = False):
        self.agent_registry = agent_registry or registry
        
        # Create worker pools (for now, just one pool)
        self.worker_pools = [WorkerPool(max_workers, self.agent_registry)]
        
        # Create load balancer
        self.load_balancer = LoadBalancer(self.worker_pools)
        
        # Create task queue
        self.task_queue = TaskQueue()
        
        # Create resource monitor
        self.resource_monitor = ResourceMonitor()
        
        # Brainwave interface integration
        self.brainwave_adapter = None
        if enable_brainwave and BrainwaveAgentAdapter is not None:
            self.brainwave_adapter = BrainwaveAgentAdapter(self)
        
        # Predictive UI interface integration
        self.predictive_ui_adapter = None
        if enable_predictive_ui and PredictiveUIAdapter is not None:
            self.predictive_ui_adapter = PredictiveUIAdapter(self)
        
        # Personalized experience interface integration
        self.personalized_experience_integrator = None
        if enable_personalized_experience and PersonalizedExperienceIntegrator is not None:
            self.personalized_experience_integrator = PersonalizedExperienceIntegrator(self)
        
        # Start monitoring
        self.resource_monitor.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.running = True
        self.processing_thread.start()

    def submit_task(self, agent_type: str, payload: Dict[str, Any],
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   timeout: Optional[float] = None,
                   dependencies: Optional[List[str]] = None) -> str:
        """Submit a new task for parallel execution."""
        task_id = self.task_queue.add_task(
            agent_type=agent_type,
            payload=payload,
            priority=priority,
            timeout=timeout,
            dependencies=dependencies
        )
        return task_id

    def submit_batch(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Submit a batch of tasks."""
        task_ids = []
        for task in tasks:
            task_id = self.submit_task(
                agent_type=task['agent_type'],
                payload=task['payload'],
                priority=getattr(TaskPriority, task.get('priority', 'MEDIUM')),
                timeout=task.get('timeout'),
                dependencies=task.get('dependencies')
            )
            task_ids.append(task_id)
        return task_ids

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task."""
        status = self.task_queue.get_task_status(task_id)
        return status.name if status else None

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        return self.task_queue.get_task_result(task_id)

    def wait_for_completion(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a task to complete."""
        start_time = time.time()
        while True:
            status = self.task_queue.get_task_status(task_id)
            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
                return True
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        return self.task_queue.cancel_task(task_id)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        metrics = self.resource_monitor.get_current_system_metrics()
        if metrics:
            return {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'memory_total': metrics.memory_total,
                'disk_usage': metrics.disk_usage,
                'timestamp': metrics.timestamp
            }
        return {}

    def get_worker_status(self) -> Dict[str, Any]:
        """Get the status of worker pools."""
        status = {}
        for i, pool in enumerate(self.worker_pools):
            status[f"pool_{i}"] = {
                'active_tasks': pool.get_active_task_count(),
                'max_workers': pool.max_workers,
                'utilization': pool.get_worker_utilization()
            }
        return status

    def scale_workers(self, pool_index: int = 0, new_size: int = 4):
        """Scale the number of workers in a pool."""
        if 0 <= pool_index < len(self.worker_pools):
            self.worker_pools[pool_index].scale_workers(new_size)

    def shutdown(self):
        """Shutdown the parallel orchestrator."""
        self.running = False
        
        # Shutdown components
        self.resource_monitor.stop()
        
        for pool in self.worker_pools:
            pool.shutdown()
        
        self.task_queue.shutdown()
        
        # Wait for processing thread to finish
        if self.processing_thread:
            self.processing_thread.join()

    def _process_tasks(self):
        """Main task processing loop."""
        while self.running:
            try:
                # Get next task from queue
                task = self.task_queue.get_next_task(timeout=1.0)
                
                if task:
                    # Select worker pool using load balancer
                    worker_pool = self.load_balancer.select_worker(task)
                    
                    if worker_pool:
                        # Create execution context
                        context = ContextManager()
                        
                        # Execute task
                        worker_pool.execute_task(task, context)
                        
                        # Record task metrics
                        self.resource_monitor.record_task_metrics(task)
                        
                        # Update worker status
                        worker_id = f"pool_{self.worker_pools.index(worker_pool)}"
                        utilization = worker_pool.get_worker_utilization()
                        self.load_balancer.update_worker_status(worker_id, utilization)
                    else:
                        # No available workers, put task back in queue
                        self.task_queue.add_task(
                            agent_type=task.agent_type,
                            payload=task.payload,
                            priority=task.priority,
                            timeout=task.timeout,
                            dependencies=task.dependencies
                        )
                        time.sleep(0.1)
                
            except Exception as e:
                print(f"Task processing error: {e}")
                time.sleep(1.0)

    # Brainwave interface methods
    def handle_brainwave_input(self, eeg_data) -> Dict[str, Any]:
        """
        Process EEG data through brainwave interface.
        
        Args:
            eeg_data: Raw EEG data from brainwave device
            
        Returns:
            Processing result including cognitive state and actions taken
        """
        if self.brainwave_adapter is None:
            return {
                'status': 'error',
                'message': 'Brainwave interface is not enabled'
            }
        
        return self.brainwave_adapter.handle_brainwave_input(eeg_data)
    
    def get_brainwave_status(self) -> Dict[str, Any]:
        """
        Get current status of brainwave interface.
        
        Returns:
            Status information about brainwave interface
        """
        if self.brainwave_adapter is None:
            return {
                'enabled': False,
                'message': 'Brainwave interface is not enabled'
            }
        
        return self.brainwave_adapter.get_status()
    
    def enable_brainwave_interface(self):
        """Enable brainwave interface."""
        if self.brainwave_adapter is not None:
            self.brainwave_adapter.enable()
    
    def disable_brainwave_interface(self):
        """Disable brainwave interface."""
        if self.brainwave_adapter is not None:
            self.brainwave_adapter.disable()
    
    # Predictive UI interface methods
    def get_optimal_ui_configuration(self) -> Dict[str, Any]:
        """
        Get optimal UI configuration based on current context.
        
        Returns:
            Dictionary containing optimal UI configuration
        """
        if self.predictive_ui_adapter is None:
            return {
                'status': 'error',
                'message': 'Predictive UI interface is not enabled'
            }
        
        return self.predictive_ui_adapter.get_optimal_ui_configuration()
    
    def record_user_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record user interaction for pattern analysis.
        
        Args:
            interaction_data: Dictionary containing interaction details
            
        Returns:
            Result of recording operation
        """
        if self.predictive_ui_adapter is None:
            return {
                'status': 'error',
                'message': 'Predictive UI interface is not enabled'
            }
        
        return self.predictive_ui_adapter.record_user_interaction(interaction_data)
    
    def get_user_insights(self) -> Dict[str, Any]:
        """
        Get insights about user patterns and preferences.
        
        Returns:
            Dictionary of user insights
        """
        if self.predictive_ui_adapter is None:
            return {
                'status': 'error',
                'message': 'Predictive UI interface is not enabled'
            }
        
        return self.predictive_ui_adapter.get_user_insights()
    
    def update_user_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user preferences.
        
        Args:
            preferences: Dictionary of user preferences
            
        Returns:
            Result of update operation
        """
        if self.predictive_ui_adapter is None:
            return {
                'status': 'error',
                'message': 'Predictive UI interface is not enabled'
            }
        
        return self.predictive_ui_adapter.update_user_preferences(preferences)
    
    def enable_predictive_ui_interface(self):
        """Enable predictive UI interface."""
        if self.predictive_ui_adapter is not None:
            self.predictive_ui_adapter.enable()
    
    def disable_predictive_ui_interface(self):
        """Disable predictive UI interface."""
        if self.predictive_ui_adapter is not None:
            self.predictive_ui_adapter.disable()
    
    def get_predictive_ui_status(self) -> Dict[str, Any]:
        """Get current status of predictive UI interface."""
        if self.predictive_ui_adapter is None:
            return {
                'enabled': False,
                'message': 'Predictive UI interface is not enabled'
            }
        
        return self.predictive_ui_adapter.get_status()
    
    # Personalized experience interface methods
    def create_personalized_experience(self) -> Dict[str, Any]:
        """
        Create a comprehensive personalized experience configuration.
        
        Returns:
            Dictionary containing personalized experience configuration
        """
        if self.personalized_experience_integrator is None:
            return {
                'status': 'error',
                'message': 'Personalized experience interface is not enabled'
            }
        
        return self.personalized_experience_integrator.create_personalized_experience()
    
    def update_personalized_profile(self, profile_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update personalized experience profile.
        
        Args:
            profile_updates: Dictionary of profile updates
            
        Returns:
            Result of update operation
        """
        if self.personalized_experience_integrator is None:
            return {
                'status': 'error',
                'message': 'Personalized experience interface is not enabled'
            }
        
        return self.personalized_experience_integrator.update_user_profile(profile_updates)
    
    def get_personalization_status(self) -> Dict[str, Any]:
        """Get current status of personalized experience system."""
        if self.personalized_experience_integrator is None:
            return {
                'enabled': False,
                'message': 'Personalized experience interface is not enabled'
            }
        
        return self.personalized_experience_integrator.get_personalization_status()
    
    def enable_personalized_experience(self):
        """Enable personalized experience system."""
        if self.personalized_experience_integrator is not None:
            self.personalized_experience_integrator.enable()
    
    def disable_personalized_experience(self):
        """Disable personalized experience system."""
        if self.personalized_experience_integrator is not None:
            self.personalized_experience_integrator.disable()
    
    # Methods required by brainwave adapter
    def start_next_task(self, **kwargs) -> Dict[str, Any]:
        """Start next task in queue (called by brainwave adapter)."""
        # Find next task that can be executed
        for task in self.task_queue.get_all_tasks():
            if task.status == TaskStatus.PENDING and not task.dependencies:
                # Submit the task
                task_id = self.submit_task(
                    agent_type=task.agent_type,
                    payload=task.payload,
                    priority=task.priority,
                    timeout=task.timeout
                )
                return {
                    'status': 'success',
                    'task_id': task_id,
                    'message': f'Started task {task_id}'
                }
        
        return {
            'status': 'no_tasks',
            'message': 'No tasks available to start'
        }
    
    def pause_current_task(self, **kwargs) -> Dict[str, Any]:
        """Pause current task (called by brainwave adapter)."""
        # Find currently running tasks and pause them
        paused_tasks = []
        for worker_pool in self.worker_pools:
            for worker in worker_pool.workers:
                if worker.current_task:
                    worker.current_task.status = TaskStatus.PAUSED
                    paused_tasks.append(worker.current_task.task_id)
        
        if paused_tasks:
            return {
                'status': 'success',
                'paused_tasks': paused_tasks,
                'message': f'Paused {len(paused_tasks)} tasks'
            }
        else:
            return {
                'status': 'no_tasks',
                'message': 'No running tasks to pause'
            }
    
    def adjust_task_priorities(self, **kwargs) -> Dict[str, Any]:
        """Adjust task priorities based on cognitive load (called by brainwave adapter)."""
        target_load = kwargs.get('target_load', 0.6)
        reduction_factor = kwargs.get('reduction_factor', 0.2)
        
        # Adjust priorities of pending tasks
        adjusted_count = 0
        for task in self.task_queue.get_all_tasks():
            if task.status == TaskStatus.PENDING:
                # Reduce priority to decrease cognitive load
                if task.priority.value > 1:  # Don't reduce below LOW
                    task.priority = TaskPriority(task.priority.value - 1)
                    adjusted_count += 1
        
        return {
            'status': 'success',
            'adjusted_tasks': adjusted_count,
            'target_load': target_load,
            'message': f'Adjusted {adjusted_count} task priorities'
        }
    
    def suggest_user_break(self, **kwargs) -> Dict[str, Any]:
        """Suggest user break (called by brainwave adapter)."""
        duration = kwargs.get('duration_minutes', 10)
        break_type = kwargs.get('break_type', 'stress_reduction')
        
        # Pause all current tasks
        self.pause_current_task()
        
        return {
            'status': 'success',
            'break_type': break_type,
            'duration_minutes': duration,
            'message': f'Suggesting {duration}-minute {break_type} break'
        }
    
    def auto_approve_current_work(self, **kwargs) -> Dict[str, Any]:
        """Auto-approve current work based on high confidence (called by brainwave adapter)."""
        confidence = kwargs.get('confidence', 0.9)
        
        # Find completed tasks and mark as approved
        approved_tasks = []
        for task in self.task_queue.get_all_tasks():
            if task.status == TaskStatus.COMPLETED:
                task.status = TaskStatus.APPROVED
                approved_tasks.append(task.task_id)
        
        if approved_tasks:
            return {
                'status': 'success',
                'approved_tasks': approved_tasks,
                'confidence': confidence,
                'message': f'Auto-approved {len(approved_tasks)} tasks with confidence {confidence}'
            }
        else:
            return {
                'status': 'no_tasks',
                'message': 'No completed tasks to approve'
            }
    
    def request_human_review(self, **kwargs) -> Dict[str, Any]:
        """Request human review based on high cognitive load (called by brainwave adapter)."""
        priority = kwargs.get('priority', 'high')
        cognitive_load = kwargs.get('cognitive_load', 0.8)
        
        # Find tasks that need review
        review_tasks = []
        for task in self.task_queue.get_all_tasks():
            if task.status == TaskStatus.COMPLETED:
                task.status = TaskStatus.NEEDS_REVIEW
                review_tasks.append(task.task_id)
        
        if review_tasks:
            return {
                'status': 'success',
                'review_tasks': review_tasks,
                'priority': priority,
                'cognitive_load': cognitive_load,
                'message': f'Requested human review for {len(review_tasks)} tasks (cognitive load: {cognitive_load})'
            }
        else:
            return {
                'status': 'no_tasks',
                'message': 'No completed tasks to review'
            }