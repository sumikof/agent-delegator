"""Edge case tests for autonomous agent functionality.

This module contains tests for edge cases and unusual scenarios to ensure
robustness of the autonomous agent components.
"""

import unittest
from datetime import datetime, timedelta

from orchestrator.agents.autonomous_base import AutonomousAgent
from orchestrator.agents.context_understanding import ContextAnalyzer
from orchestrator.agents.priority_manager import PriorityManager
from orchestrator.agents.learning_system import LearningSystem
from orchestrator.agents.coordination_system import CoordinationSystem
from orchestrator.agents.task_management import TaskManager
from orchestrator.agents.negotiation_system import NegotiationSystem


class TestAutonomousAgentEdgeCases(unittest.TestCase):
    """Edge case tests for AutonomousAgent."""

    def test_empty_context(self):
        """Test agent behavior with empty context."""
        agent = AutonomousAgent("test_agent", "Test Agent")
        
        result = agent.run({})
        
        self.assertEqual(result["status"], "OK")
        self.assertIn("autonomy_info", result)

    def test_none_context(self):
        """Test agent behavior with None context."""
        agent = AutonomousAgent("test_agent", "Test Agent")
        
        result = agent.run(None)
        
        self.assertEqual(result["status"], "OK")
        self.assertIn("autonomy_info", result)

    def test_very_large_context(self):
        """Test agent behavior with very large context."""
        agent = AutonomousAgent("test_agent", "Test Agent")
        
        # Create a very large context
        large_context = {f"field_{i}": f"value_{i}" * 100 for i in range(1000)}
        
        result = agent.run(large_context)
        
        self.assertEqual(result["status"], "OK")
        self.assertIn("autonomy_info", result)

    def test_memory_overflow(self):
        """Test agent behavior when memory overflows."""
        agent = AutonomousAgent("test_agent", "Test Agent")
        
        # Add more contexts than memory limit
        for i in range(150):
            context = {f"field_{i}": f"value_{i}"}
            agent.run(context)
        
        # Memory should be managed (not exceed limit)
        self.assertLessEqual(len(agent.context_memory), 100)

    def test_unknown_message_type(self):
        """Test agent behavior with unknown message type."""
        agent = AutonomousAgent("test_agent", "Test Agent")
        
        message = {
            "message_type": "unknown_type",
            "payload": {"some": "data"}
        }
        
        response = agent.receive_message(message)
        
        self.assertEqual(response["status"], "ignored")

    def test_malformed_context(self):
        """Test agent behavior with malformed context."""
        agent = AutonomousAgent("test_agent", "Test Agent")
        
        # Context with non-standard data types
        malformed_context = {
            "normal_field": "normal_value",
            "weird_field": object(),  # Non-serializable object
            "none_field": None,
            "nested": {
                "circular": None
            }
        }
        
        # Should not crash
        result = agent.run(malformed_context)
        self.assertEqual(result["status"], "OK")


class TestContextAnalyzerEdgeCases(unittest.TestCase):
    """Edge case tests for ContextAnalyzer."""

    def test_empty_context_analysis(self):
        """Test context analysis with empty context."""
        analyzer = ContextAnalyzer()
        
        result = analyzer.analyze_context({})
        
        self.assertIn("context_type", result)
        self.assertEqual(result["context_type"], "general")

    def test_context_with_circular_references(self):
        """Test context analysis with circular references."""
        analyzer = ContextAnalyzer()
        
        # Create context with potential circular reference issues
        context = {"tasks": [{"id": "task_1", "dependencies": ["task_2"]}]}
        
        # Should not crash
        result = analyzer.analyze_context(context)
        self.assertIn("key_entities", result)

    def test_context_with_none_values(self):
        """Test context analysis with None values."""
        analyzer = ContextAnalyzer()
        
        context = {
            "tasks": None,
            "resources": None,
            "workflow": None
        }
        
        result = analyzer.analyze_context(context)
        self.assertIn("context_type", result)

    def test_context_with_very_long_strings(self):
        """Test context analysis with very long strings."""
        analyzer = ContextAnalyzer()
        
        context = {
            "description": "x" * 10000,  # Very long string
            "tasks": [
                {
                    "id": "task_1",
                    "description": "y" * 5000  # Another long string
                }
            ]
        }
        
        # Should not crash or take too long
        result = analyzer.analyze_context(context)
        self.assertIn("complexity_score", result)

    def test_context_with_special_characters(self):
        """Test context analysis with special characters."""
        analyzer = ContextAnalyzer()
        
        context = {
            "tasks": [
                {
                    "id": "task_1",
                    "name": "Task with special chars: !@#$%^&*()",
                    "description": "Description with \n newlines and \t tabs"
                }
            ],
            "resources": {
                "resource_1": {
                    "name": "Resource with unicode: 你好世界 🚀",
                    "availability": 0.8
                }
            }
        }
        
        result = analyzer.analyze_context(context)
        self.assertGreater(len(result["key_entities"]), 0)


class TestPriorityManagerEdgeCases(unittest.TestCase):
    """Edge case tests for PriorityManager."""

    def test_empty_task_list(self):
        """Test priority calculation with empty task list."""
        priority_manager = PriorityManager()
        
        result = priority_manager.calculate_priorities([])
        
        self.assertEqual(result, [])

    def test_tasks_with_missing_fields(self):
        """Test priority calculation with tasks missing required fields."""
        priority_manager = PriorityManager()
        
        tasks = [
            {"id": "task_1"},  # Missing priority
            {"priority": 5},   # Missing id
            {}                  # Empty task
        ]
        
        # Should not crash
        result = priority_manager.calculate_priorities(tasks)
        self.assertEqual(len(result), 3)

    def test_tasks_with_invalid_priority_values(self):
        """Test priority calculation with invalid priority values."""
        priority_manager = PriorityManager()
        
        tasks = [
            {"id": "task_1", "priority": -5},    # Negative priority
            {"id": "task_2", "priority": 15},    # Very high priority
            {"id": "task_3", "priority": "high"},  # String priority
            {"id": "task_4", "priority": None}    # None priority
        ]
        
        # Should not crash
        result = priority_manager.calculate_priorities(tasks)
        self.assertEqual(len(result), 4)

    def test_tasks_with_invalid_deadlines(self):
        """Test priority calculation with invalid deadline formats."""
        priority_manager = PriorityManager()
        
        tasks = [
            {"id": "task_1", "priority": 5, "deadline": "invalid_date"},
            {"id": "task_2", "priority": 5, "deadline": 12345},  # Number instead of string
            {"id": "task_3", "priority": 5, "deadline": None}
        ]
        
        # Should not crash
        result = priority_manager.calculate_priorities(tasks)
        self.assertEqual(len(result), 3)

    def test_unknown_strategy(self):
        """Test priority manager with unknown strategy."""
        priority_manager = PriorityManager()
        
        # Try to set unknown strategy
        result = priority_manager.set_strategy("unknown_strategy")
        
        self.assertFalse(result)
        self.assertEqual(priority_manager.current_strategy, "default")


class TestLearningSystemEdgeCases(unittest.TestCase):
    """Edge case tests for LearningSystem."""

    def test_empty_feedback(self):
        """Test learning system with empty feedback."""
        learning_system = LearningSystem()
        
        # Should not crash
        learning_system.process_feedback({})
        self.assertEqual(len(learning_system.feedback_history), 1)

    def test_feedback_with_missing_fields(self):
        """Test learning system with feedback missing required fields."""
        learning_system = LearningSystem()
        
        feedback = {
            "adjustments": [
                {"effectiveness": 0.8}  # Missing reason
            ]
        }
        
        # Should not crash
        learning_system.process_feedback(feedback)
        self.assertEqual(len(learning_system.feedback_history), 1)

    def test_learning_with_no_feedback(self):
        """Test learning cycle with no feedback."""
        learning_system = LearningSystem()
        
        # Should not crash
        result = learning_system.perform_learning_cycle()
        self.assertIn("new_patterns_learned", result)

    def test_learning_with_malformed_feedback(self):
        """Test learning system with malformed feedback."""
        learning_system = LearningSystem()
        
        feedback = {
            "type": "priority_adjustment",
            "adjustments": [
                {
                    "reason": object(),  # Non-serializable object
                    "effectiveness": "high"  # String instead of number
                }
            ]
        }
        
        # Should not crash
        learning_system.process_feedback(feedback)
        self.assertEqual(len(learning_system.feedback_history), 1)

    def test_performance_recording_with_invalid_data(self):
        """Test performance recording with invalid data."""
        learning_system = LearningSystem()
        
        performance_data = {
            "invalid_metric": object(),
            "another_metric": "not_a_number",
            "nested": {
                "circular": None
            }
        }
        
        # Should not crash
        learning_system.record_performance(performance_data)
        self.assertEqual(len(learning_system.performance_history), 1)


class TestCoordinationSystemEdgeCases(unittest.TestCase):
    """Edge case tests for CoordinationSystem."""

    def test_unknown_conflict_type(self):
        """Test coordination system with unknown conflict type."""
        coordination_system = CoordinationSystem()
        
        request = {
            "conflict_type": "unknown_conflict",
            "requesting_agent": "agent_1"
        }
        
        result = coordination_system.handle_coordination_request(request)
        
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["decision"], "default_resolution")

    def test_conflict_with_missing_fields(self):
        """Test coordination system with conflict missing required fields."""
        coordination_system = CoordinationSystem()
        
        request = {
            "conflict_type": "resource_conflict"
            # Missing resource_id, requesting_agent, etc.
        }
        
        # Should not crash
        result = coordination_system.handle_coordination_request(request)
        self.assertEqual(result["status"], "resolved")

    def test_negotiation_with_no_participants(self):
        """Test negotiation with no participants."""
        coordination_system = CoordinationSystem()
        
        result = coordination_system.initiate_negotiation(
            "resource_allocation",
            [],  # No participants
            {"resources": {}}
        )
        
        self.assertEqual(result["status"], "error")

    def test_negotiation_with_unknown_type(self):
        """Test negotiation with unknown type."""
        coordination_system = CoordinationSystem()
        
        result = coordination_system.initiate_negotiation(
            "unknown_negotiation",
            ["agent_1"],
            {}
        )
        
        self.assertEqual(result["status"], "error")

    def test_conflict_with_invalid_resource_info(self):
        """Test conflict resolution with invalid resource info."""
        coordination_system = CoordinationSystem()
        
        request = {
            "conflict_type": "resource_conflict",
            "resource_id": "test_resource",
            "resource_info": {
                "availability": "high",  # String instead of number
                "contention": -0.5,       # Negative value
                "invalid_field": object() # Non-serializable object
            }
        }
        
        # Should not crash
        result = coordination_system.handle_coordination_request(request)
        self.assertEqual(result["status"], "resolved")


class TestTaskManagerEdgeCases(unittest.TestCase):
    """Edge case tests for TaskManager."""

    def test_splitting_task_with_no_id(self):
        """Test task splitting with task missing id."""
        task_manager = TaskManager()
        
        task = {
            "name": "Task without ID",
            "description": "This task has no ID"
        }
        
        # Should not crash
        result = task_manager.split_task(task)
        self.assertGreater(len(result), 0)

    def test_splitting_task_with_invalid_strategy(self):
        """Test task splitting with invalid strategy."""
        task_manager = TaskManager()
        
        task = {
            "id": "test_task",
            "name": "Test Task"
        }
        
        # Should use default strategy
        result = task_manager.split_task(task, "invalid_strategy")
        self.assertGreater(len(result), 0)

    def test_integrating_empty_subtask_list(self):
        """Test task integration with empty subtask list."""
        task_manager = TaskManager()
        
        result = task_manager.integrate_tasks([])
        
        self.assertEqual(result, {})

    def test_integrating_subtasks_with_missing_fields(self):
        """Test task integration with subtasks missing required fields."""
        task_manager = TaskManager()
        
        subtasks = [
            {"id": "subtask_1"},  # Missing original_task_id
            {"original_task_id": "parent_task"},  # Missing id
            {}  # Empty subtask
        ]
        
        # Should not crash
        result = task_manager.integrate_tasks(subtasks)
        self.assertIn("subtasks", result)

    def test_splitting_task_with_circular_dependencies(self):
        """Test task splitting with circular dependencies."""
        task_manager = TaskManager()
        
        task = {
            "id": "circular_task",
            "name": "Task with circular dependencies",
            "dependencies": ["circular_task"]  # Self-reference
        }
        
        # Should not crash
        result = task_manager.split_task(task)
        self.assertGreater(len(result), 0)


class TestNegotiationSystemEdgeCases(unittest.TestCase):
    """Edge case tests for NegotiationSystem."""

    def test_negotiation_with_empty_context(self):
        """Test negotiation with empty context."""
        negotiation_system = NegotiationSystem()
        
        result = negotiation_system.initiate_negotiation(
            "resource_allocation",
            ["agent_1"],
            {}  # Empty context
        )
        
        self.assertEqual(result["status"], "error")

    def test_negotiation_with_invalid_participants(self):
        """Test negotiation with invalid participants."""
        negotiation_system = NegotiationSystem()
        
        result = negotiation_system.initiate_negotiation(
            "resource_allocation",
            [None, "", 123, object()],  # Invalid participant types
            {"resources": {}}
        )
        
        self.assertEqual(result["status"], "error")

    def test_negotiation_with_malformed_context(self):
        """Test negotiation with malformed context."""
        negotiation_system = NegotiationSystem()
        
        context = {
            "participants": ["agent_1", "agent_2"],
            "resources": {
                "resource_1": {
                    "availability": object(),  # Non-serializable
                    "contention": "high"       # String instead of number
                }
            },
            "agent_1_priority": "high",  # String instead of number
            "agent_2_priority": -5        # Negative priority
        }
        
        # Should not crash
        result = negotiation_system.initiate_negotiation(
            "resource_allocation",
            ["agent_1", "agent_2"],
            context
        )
        
        self.assertIn("status", result)

    def test_get_negotiation_status_with_invalid_id(self):
        """Test getting negotiation status with invalid ID."""
        negotiation_system = NegotiationSystem()
        
        result = negotiation_system.get_negotiation_status("invalid_negotiation_id")
        
        self.assertIsNone(result)

    def test_negotiation_with_no_resources(self):
        """Test resource negotiation with no resources."""
        negotiation_system = NegotiationSystem()
        
        context = {
            "participants": ["agent_1", "agent_2"],
            "resources": {}  # No resources
        }
        
        result = negotiation_system.initiate_negotiation(
            "resource_allocation",
            ["agent_1", "agent_2"],
            context
        )
        
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()