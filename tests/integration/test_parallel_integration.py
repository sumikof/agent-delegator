"""
Integration tests for parallel processing functionality.
"""

import unittest
import tempfile
import json
import time
from pathlib import Path

from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry
from orchestrator.parallel.task_queue import TaskPriority


class TestParallelIntegration(unittest.TestCase):
    """Integration tests for parallel processing."""

    def setUp(self):
        self.orchestrator = ParallelOrchestrator(max_workers=2, agent_registry=AgentRegistry())

    def tearDown(self):
        self.orchestrator.shutdown()

    def test_basic_parallel_execution(self):
        """Test basic parallel execution with mock tasks."""
        # Submit multiple tasks
        task_ids = []
        for i in range(3):
            task_id = self.orchestrator.submit_task(
                agent_type="client_liaison",  # Use an existing agent type
                payload={
                    "test_data": f"task_{i}",
                    "iteration": i
                },
                priority=TaskPriority.MEDIUM
            )
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        for task_id in task_ids:
            success = self.orchestrator.wait_for_completion(task_id, timeout=10.0)
            self.assertTrue(success, f"Task {task_id} did not complete in time")
        
        # Check results
        completed_count = 0
        for task_id in task_ids:
            result = self.orchestrator.get_task_result(task_id)
            if result:
                completed_count += 1
        
        # At least some tasks should complete successfully
        self.assertGreater(completed_count, 0)

    def test_task_status_tracking(self):
        """Test task status tracking."""
        # Submit a task
        task_id = self.orchestrator.submit_task(
            agent_type="planner",
            payload={"test": "status_tracking"}
        )
        
        # Check initial status
        status = self.orchestrator.get_task_status(task_id)
        self.assertIn(status, ["PENDING", "RUNNING"])
        
        # Wait for completion
        self.orchestrator.wait_for_completion(task_id, timeout=5.0)
        
        # Check final status
        final_status = self.orchestrator.get_task_status(task_id)
        self.assertIn(final_status, ["COMPLETED", "FAILED"])

    def test_system_monitoring(self):
        """Test system monitoring functionality."""
        # Wait for monitor to collect metrics
        time.sleep(1.0)
        
        # Get system metrics
        metrics = self.orchestrator.get_system_metrics()
        
        # Should return some metrics
        self.assertIsInstance(metrics, dict)
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertGreaterEqual(metrics['cpu_usage'], 0)  # CPU usage should be non-negative
        self.assertGreater(metrics['memory_usage'], 0)  # Memory usage should be positive

    def test_worker_status(self):
        """Test worker status monitoring."""
        # Get worker status
        status = self.orchestrator.get_worker_status()
        
        # Should return worker status information
        self.assertIsInstance(status, dict)
        self.assertGreater(len(status), 0)
        
        # Check that we have the expected pool
        self.assertIn('pool_0', status)
        pool_status = status['pool_0']
        self.assertIn('active_tasks', pool_status)
        self.assertIn('max_workers', pool_status)
        self.assertIn('utilization', pool_status)


if __name__ == "__main__":
    unittest.main()