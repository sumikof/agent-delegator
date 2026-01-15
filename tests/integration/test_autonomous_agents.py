"""Integration tests for autonomous agent functionality.

This module contains comprehensive tests for the autonomous agent capabilities,
including context understanding, dynamic priority management, and learning systems.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from orchestrator.agents.autonomous_base import AutonomousAgent
from orchestrator.agents.context_understanding import ContextAnalyzer
from orchestrator.agents.priority_manager import PriorityManager
from orchestrator.agents.learning_system import LearningSystem
from orchestrator.agents.coordination_system import CoordinationSystem
from orchestrator.agents.task_management import TaskManager
from orchestrator.agents.negotiation_system import NegotiationSystem


class TestAutonomousAgent(unittest.TestCase):
    """Test the AutonomousAgent class."""

    def setUp(self):
        self.agent = AutonomousAgent("test_agent", "Test Agent")
        self.simple_context = {
            "task_id": "test_task_1",
            "priority": 5,
            "description": "Test task for autonomous agent",
            "dependencies": ["task_2", "task_3"],
            "resources": {
                "resource_1": {
                    "type": "compute",
                    "availability": 0.8,
                    "contention": 0.2
                }
            },
            "metadata": {
                "created_by": "test_user",
                "created_at": "2024-01-01T00:00:00Z",
                "tags": ["test", "autonomous"]
            }
        }

    def test_autonomous_agent_initialization(self):
        """Test that AutonomousAgent initializes correctly."""
        self.assertEqual(self.agent.id, "test_agent")
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.priority_strategy, "default")
        self.assertEqual(len(self.agent.context_memory), 0)
        self.assertEqual(len(self.agent.learning_data), 0)

    def test_autonomous_agent_run(self):
        """Test that AutonomousAgent.run() executes correctly."""
        result = self.agent.run(self.simple_context)
        
        self.assertEqual(result["status"], "OK")
        self.assertIn("autonomy_info", result)
        self.assertGreater(len(result["autonomy_info"]["decisions_made"]), 0)
        self.assertEqual(result["autonomy_info"]["priority_strategy"], "default")

    def test_context_storage(self):
        """Test that context is stored in memory."""
        initial_memory_size = len(self.agent.context_memory)
        
        self.agent.run(self.simple_context)
        
        self.assertEqual(len(self.agent.context_memory), initial_memory_size + 1)
        self.assertEqual(self.agent.context_memory[-1]["context_data"], self.simple_context)

    def test_autonomy_status(self):
        """Test that autonomy status is calculated correctly."""
        status = self.agent.get_autonomy_status()
        
        self.assertEqual(status["agent_id"], "test_agent")
        self.assertEqual(status["agent_name"], "Test Agent")
        self.assertEqual(status["priority_strategy"], "default")
        self.assertEqual(status["memory_size"], 0)
        self.assertEqual(status["learning_data_size"], 0)

    def test_learning_from_experience(self):
        """Test that agent can learn from experience."""
        feedback = {
            "type": "priority_adjustment",
            "priority_strategy": "dependency_aware",
            "effectiveness": 0.8
        }
        
        self.agent.learn_from_experience(feedback)
        
        self.assertEqual(self.agent.priority_strategy, "dependency_aware")
        self.assertEqual(len(self.agent.learning_data), 1)

    def test_coordination_handling(self):
        """Test that agent can handle coordination requests."""
        message = {
            "message_type": "coordination_request",
            "payload": {
                "conflict_type": "resource_conflict",
                "resource_id": "test_resource",
                "requesting_task_id": "task_1",
                "conflicting_task_id": "task_2"
            }
        }
        
        response = self.agent.receive_message(message)
        
        self.assertEqual(response["status"], "resolved")
        self.assertIn("decision", response)


class TestContextAnalyzer(unittest.TestCase):
    """Test the ContextAnalyzer class."""

    def setUp(self):
        self.analyzer = ContextAnalyzer()
        self.simple_context = {
            "tasks": [
                {
                    "id": "task_1",
                    "name": "Test Task 1",
                    "priority": 5,
                    "dependencies": []
                }
            ],
            "resources": {
                "resource_1": {
                    "name": "Test Resource",
                    "availability": 0.8,
                    "contention": 0.2
                }
            }
        }

    def test_context_analysis(self):
        """Test that context analysis works correctly."""
        result = self.analyzer.analyze_context(self.simple_context)
        
        self.assertIn("context_type", result)
        self.assertIn("complexity_score", result)
        self.assertIn("key_entities", result)
        self.assertIn("relationships", result)
        self.assertIn("potential_issues", result)
        self.assertIn("opportunities", result)

    def test_entity_extraction(self):
        """Test that entities are extracted correctly."""
        result = self.analyzer.analyze_context(self.simple_context)
        entities = result["key_entities"]
        
        self.assertEqual(len(entities), 2)  # 1 task + 1 resource
        self.assertEqual(entities[0]["type"], "task")
        self.assertEqual(entities[1]["type"], "resource")

    def test_issue_detection(self):
        """Test that potential issues are detected."""
        # Test with low resource availability
        low_resource_context = {
            "resources": {
                "critical_resource": {
                    "availability": 0.1,  # Very low
                    "contention": 0.1
                }
            }
        }
        
        result = self.analyzer.analyze_context(low_resource_context)
        issues = result["potential_issues"]
        
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]["type"], "resource_constraint")
        self.assertEqual(issues[0]["severity"], "high")

    def test_opportunity_identification(self):
        """Test that opportunities are identified."""
        # Test with multiple independent tasks
        parallel_context = {
            "tasks": [
                {"id": "task_1", "dependencies": []},
                {"id": "task_2", "dependencies": []},
                {"id": "task_3", "dependencies": []}
            ]
        }
        
        result = self.analyzer.analyze_context(parallel_context)
        opportunities = result["opportunities"]
        
        self.assertGreater(len(opportunities), 0)
        self.assertEqual(opportunities[0]["type"], "parallelization")


class TestPriorityManager(unittest.TestCase):
    """Test the PriorityManager class."""

    def setUp(self):
        self.priority_manager = PriorityManager()
        self.simple_tasks = [
            {
                "id": "task_1",
                "name": "High Priority Task",
                "priority": 8,
                "dependencies": ["task_2"]
            },
            {
                "id": "task_2",
                "name": "Dependency Task",
                "priority": 5,
                "dependencies": []
            }
        ]

    def test_priority_calculation(self):
        """Test that priorities are calculated correctly."""
        result = self.priority_manager.calculate_priorities(self.simple_tasks)
        
        self.assertEqual(len(result), 2)
        # Task 1 should have higher priority due to dependencies
        self.assertGreater(result[0]["priority"], 8)

    def test_strategy_selection(self):
        """Test that different strategies can be selected."""
        self.assertTrue(self.priority_manager.set_strategy("dependency_aware"))
        self.assertEqual(self.priority_manager.current_strategy, "dependency_aware")
        
        self.assertFalse(self.priority_manager.set_strategy("unknown_strategy"))

    def test_dependency_aware_strategy(self):
        """Test the dependency-aware priority strategy."""
        self.priority_manager.set_strategy("dependency_aware")
        result = self.priority_manager.calculate_priorities(self.simple_tasks)
        
        # Task 1 has dependencies, should get priority boost
        task1_priority = next(t["priority"] for t in result if t["id"] == "task_1")
        self.assertGreater(task1_priority, 8)

    def test_resource_aware_strategy(self):
        """Test the resource-aware priority strategy."""
        self.priority_manager.set_strategy("resource_aware")
        
        # Create tasks with resource requirements
        resource_tasks = [
            {
                "id": "task_1",
                "priority": 5,
                "required_resources": ["scarce_resource"]
            }
        ]
        
        context = {
            "resources": {
                "scarce_resource": {
                    "availability": 0.2,  # Low availability
                    "contention": 0.8    # High contention
                }
            }
        }
        
        result = self.priority_manager.calculate_priorities(resource_tasks, context)
        
        # Task should get priority boost due to scarce resource
        self.assertGreater(result[0]["priority"], 5)


class TestLearningSystem(unittest.TestCase):
    """Test the LearningSystem class."""

    def setUp(self):
        self.learning_system = LearningSystem()
        self.simple_feedback = {
            "type": "priority_adjustment",
            "adjustments": [
                {
                    "reason": "dependency_analysis",
                    "effectiveness": 0.8
                }
            ]
        }

    def test_feedback_processing(self):
        """Test that feedback is processed correctly."""
        initial_feedback_count = len(self.learning_system.feedback_history)
        
        self.learning_system.process_feedback(self.simple_feedback)
        
        self.assertEqual(len(self.learning_system.feedback_history), initial_feedback_count + 1)

    def test_learning_cycle(self):
        """Test that learning cycles work correctly."""
        # Add some feedback first
        self.learning_system.process_feedback(self.simple_feedback)
        
        result = self.learning_system.perform_learning_cycle()
        
        self.assertIn("new_patterns_learned", result)
        self.assertIn("knowledge_updated", result)

    def test_learning_status(self):
        """Test that learning status is reported correctly."""
        status = self.learning_system.get_learning_status()
        
        self.assertIn("learning_metrics", status)
        self.assertIn("knowledge_base_size", status)
        self.assertEqual(status["learning_metrics"]["total_learning_cycles"], 0)

    def test_adaptation_suggestions(self):
        """Test that adaptation suggestions are generated."""
        context = {
            "tasks": [
                {"id": "task_1", "dependencies": []},
                {"id": "task_2", "dependencies": []}
            ]
        }
        
        suggestions = self.learning_system.get_adaptation_suggestions(context)
        
        self.assertGreater(len(suggestions), 0)
        self.assertIn("type", suggestions[0])


class TestCoordinationSystem(unittest.TestCase):
    """Test the CoordinationSystem class."""

    def setUp(self):
        self.coordination_system = CoordinationSystem()
        self.simple_conflict = {
            "conflict_type": "resource_conflict",
            "resource_id": "test_resource",
            "requesting_agent": "agent_1",
            "conflicting_agent": "agent_2",
            "resource_info": {
                "availability": 0.5,
                "contention": 0.3
            }
        }

    def test_conflict_resolution(self):
        """Test that conflicts are resolved correctly."""
        result = self.coordination_system.handle_coordination_request(self.simple_conflict)
        
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["conflict_type"], "resource_conflict")

    def test_resource_conflict_resolution(self):
        """Test resource conflict resolution."""
        # Test low availability conflict
        low_availability_conflict = self.simple_conflict.copy()
        low_availability_conflict["resource_info"]["availability"] = 0.1
        
        result = self.coordination_system.handle_coordination_request(low_availability_conflict)
        
        self.assertEqual(result["resolution_strategy"], "urgency_based")

    def test_priority_conflict_resolution(self):
        """Test priority conflict resolution."""
        priority_conflict = {
            "conflict_type": "priority_conflict",
            "involved_tasks": ["task_1", "task_2"],
            "task_task_1": {"priority": 8, "dependencies": []},
            "task_task_2": {"priority": 5, "dependencies": []}
        }
        
        result = self.coordination_system.handle_coordination_request(priority_conflict)
        
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["conflict_type"], "priority_conflict")

    def test_coordination_metrics(self):
        """Test that coordination metrics are tracked."""
        initial_metrics = self.coordination_system.get_coordination_metrics()
        initial_total = initial_metrics["coordination_metrics"]["total_coordination_events"]
        
        # Handle a conflict
        self.coordination_system.handle_coordination_request(self.simple_conflict)
        
        updated_metrics = self.coordination_system.get_coordination_metrics()
        self.assertEqual(updated_metrics["coordination_metrics"]["total_coordination_events"], initial_total + 1)


class TestTaskManager(unittest.TestCase):
    """Test the TaskManager class."""

    def setUp(self):
        self.task_manager = TaskManager()
        self.complex_task = {
            "id": "complex_task_1",
            "name": "Complex Development Task",
            "description": "Develop a full-stack application with backend, frontend, and API components",
            "priority": 7,
            "dependencies": ["setup_task"],
            "required_resources": ["backend_server", "frontend_framework", "api_gateway"],
            "estimated_complexity": 4.2
        }

    def test_task_splitting(self):
        """Test that tasks are split correctly."""
        subtasks = self.task_manager.split_task(self.complex_task, "complexity_based")
        
        self.assertGreater(len(subtasks), 1)
        self.assertEqual(subtasks[0]["original_task_id"], "complex_task_1")

    def test_size_based_splitting(self):
        """Test size-based task splitting."""
        subtasks = self.task_manager.split_task(self.complex_task, "size_based")
        
        self.assertGreater(len(subtasks), 1)
        self.assertLess(len(subtasks), 6)  # Should not create too many subtasks

    def test_resource_based_splitting(self):
        """Test resource-based task splitting."""
        subtasks = self.task_manager.split_task(self.complex_task, "resource_based")
        
        # Should create subtasks for each resource
        self.assertEqual(len(subtasks), 3)
        self.assertEqual(subtasks[0]["required_resources"], ["backend_server"])

    def test_task_integration(self):
        """Test that subtasks are integrated correctly."""
        # Create some subtasks
        subtasks = [
            {
                "id": "subtask_1",
                "original_task_id": "complex_task_1",
                "status": "completed",
                "result": {"backend": "implemented"}
            },
            {
                "id": "subtask_2",
                "original_task_id": "complex_task_1",
                "status": "completed",
                "result": {"frontend": "implemented"}
            }
        ]
        
        integrated_task = self.task_manager.integrate_tasks(subtasks)
        
        self.assertEqual(integrated_task["id"], "complex_task_1")
        self.assertEqual(integrated_task["status"], "completed")
        self.assertEqual(len(integrated_task["subtasks"]), 2)

    def test_parallel_integration(self):
        """Test parallel task integration."""
        # Create subtasks with timing information
        subtasks = [
            {
                "id": "subtask_1",
                "original_task_id": "parallel_task",
                "status": "completed",
                "result": {"part": "A"},
                "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "end_time": (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                "id": "subtask_2",
                "original_task_id": "parallel_task",
                "status": "completed",
                "result": {"part": "B"},
                "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "end_time": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat()
            }
        ]
        
        integrated_task = self.task_manager.integrate_tasks(subtasks, "parallel")
        
        self.assertEqual(integrated_task["status"], "completed")
        self.assertIn("parallel_metrics", integrated_task)


class TestNegotiationSystem(unittest.TestCase):
    """Test the NegotiationSystem class."""

    def setUp(self):
        self.negotiation_system = NegotiationSystem()
        self.resource_negotiation_context = {
            "participants": ["agent_1", "agent_2"],
            "resources": {
                "shared_resource": {
                    "availability": 0.6,
                    "contention": 0.4
                }
            },
            "agent_1_priority": 8,
            "agent_2_priority": 6,
            "agent_1_required_resources": ["shared_resource"],
            "agent_2_required_resources": ["shared_resource"]
        }

    def test_resource_allocation_negotiation(self):
        """Test resource allocation negotiation."""
        result = self.negotiation_system.initiate_negotiation(
            "resource_allocation",
            ["agent_1", "agent_2"],
            self.resource_negotiation_context
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["negotiation_type"], "resource_allocation")
        self.assertIn("allocation_plan", result)

    def test_task_prioritization_negotiation(self):
        """Test task prioritization negotiation."""
        prioritization_context = {
            "participants": ["agent_1", "agent_2"],
            "tasks": ["task_1", "task_2"],
            "agent_1_task_1_priority": 7,
            "agent_1_task_2_priority": 5,
            "agent_2_task_1_priority": 6,
            "agent_2_task_2_priority": 8
        }
        
        result = self.negotiation_system.initiate_negotiation(
            "task_prioritization",
            ["agent_1", "agent_2"],
            prioritization_context
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("consensus_priorities", result)

    def test_negotiation_metrics(self):
        """Test that negotiation metrics are tracked."""
        initial_metrics = self.negotiation_system.get_negotiation_metrics()
        initial_total = initial_metrics["negotiation_metrics"]["total_negotiations"]
        
        # Perform a negotiation
        self.negotiation_system.initiate_negotiation(
            "resource_allocation",
            ["agent_1", "agent_2"],
            self.resource_negotiation_context
        )
        
        updated_metrics = self.negotiation_system.get_negotiation_metrics()
        self.assertEqual(updated_metrics["negotiation_metrics"]["total_negotiations"], initial_total + 1)


if __name__ == "__main__":
    unittest.main()