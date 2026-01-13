"""
Unit tests for parallel processing functionality.
"""

import unittest
import time
from unittest.mock import Mock, patch

from orchestrator.parallel.task_queue import TaskQueue, Task, TaskPriority, TaskStatus
from orchestrator.parallel.worker_pool import WorkerPool
from orchestrator.parallel.load_balancer import LoadBalancer
from orchestrator.parallel.monitor import ResourceMonitor


class TestTaskQueue(unittest.TestCase):
    """Test the task queue functionality."""

    def setUp(self):
        self.queue = TaskQueue()

    def test_add_and_get_task(self):
        """Test adding and getting tasks from the queue."""
        # Add a task
        task_id = self.queue.add_task(
            agent_type="test_agent",
            payload={"test": "data"},
            priority=TaskPriority.MEDIUM
        )
        
        # Get the task
        task = self.queue.get_next_task()
        
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, task_id)
        self.assertEqual(task.agent_type, "test_agent")
        self.assertEqual(task.payload, {"test": "data"})
        self.assertEqual(task.status, TaskStatus.RUNNING)

    def test_task_priority(self):
        """Test that tasks are processed in priority order."""
        # Add tasks with different priorities
        low_id = self.queue.add_task("test_agent", {}, TaskPriority.LOW)
        high_id = self.queue.add_task("test_agent", {}, TaskPriority.HIGH)
        medium_id = self.queue.add_task("test_agent", {}, TaskPriority.MEDIUM)
        
        # Get tasks in order
        first_task = self.queue.get_next_task()
        second_task = self.queue.get_next_task()
        third_task = self.queue.get_next_task()
        
        # High priority should come first
        self.assertEqual(first_task.task_id, high_id)
        self.assertEqual(second_task.task_id, medium_id)
        self.assertEqual(third_task.task_id, low_id)

    def test_task_completion(self):
        """Test task completion functionality."""
        task_id = self.queue.add_task("test_agent", {})
        task = self.queue.get_next_task()
        
        # Complete the task
        self.queue.complete_task(task_id, result={"success": True})
        
        # Check status
        status = self.queue.get_task_status(task_id)
        self.assertEqual(status, TaskStatus.COMPLETED)
        
        # Check result
        result = self.queue.get_task_result(task_id)
        self.assertEqual(result, {"success": True})


class TestWorkerPool(unittest.TestCase):
    """Test the worker pool functionality."""

    def setUp(self):
        self.pool = WorkerPool(max_workers=2)

    def test_worker_pool_initialization(self):
        """Test worker pool initialization."""
        self.assertEqual(self.pool.max_workers, 2)
        self.assertEqual(self.pool.get_active_task_count(), 0)

    def test_worker_utilization(self):
        """Test worker utilization calculation."""
        # With no active tasks, utilization should be 0
        self.assertEqual(self.pool.get_worker_utilization(), 0.0)


class TestLoadBalancer(unittest.TestCase):
    """Test the load balancer functionality."""

    def setUp(self):
        # Create mock worker pools
        mock_pool1 = Mock()
        mock_pool1.max_workers = 4
        mock_pool1.get_worker_utilization.return_value = 0.5
        
        mock_pool2 = Mock()
        mock_pool2.max_workers = 2
        mock_pool2.get_worker_utilization.return_value = 0.8
        
        self.worker_pools = [mock_pool1, mock_pool2]
        self.balancer = LoadBalancer(self.worker_pools)

    def test_worker_selection(self):
        """Test worker selection logic."""
        # Create a mock task
        mock_task = Mock()
        mock_task.priority = TaskPriority.MEDIUM
        
        # Select worker (should pick the least loaded one)
        selected_pool = self.balancer.select_worker(mock_task)
        
        # Should select the first pool (lower utilization)
        self.assertEqual(selected_pool, self.worker_pools[0])


class TestResourceMonitor(unittest.TestCase):
    """Test the resource monitor functionality."""

    def setUp(self):
        self.monitor = ResourceMonitor(monitoring_interval=0.1, history_size=5)

    def test_monitor_start_stop(self):
        """Test monitor start/stop functionality."""
        # Start monitor
        self.monitor.start()
        self.assertTrue(self.monitor.running)
        
        # Stop monitor
        self.monitor.stop()
        self.assertFalse(self.monitor.running)

    def test_task_metrics_recording(self):
        """Test task metrics recording."""
        # Create a mock task
        task = Task(
            task_id="test_task",
            agent_type="test_agent",
            payload={},
            status=TaskStatus.COMPLETED
        )
        task.started_at = time.time() - 1.0
        task.completed_at = time.time()
        
        # Record metrics
        self.monitor.record_task_metrics(task)
        
        # Check that metrics were recorded
        metrics = self.monitor.get_task_metrics_history()
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].task_id, "test_task")
        self.assertAlmostEqual(metrics[0].execution_time, 1.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()