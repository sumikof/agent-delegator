"""Performance benchmarks for autonomous agent functionality.

This module contains performance tests to measure the efficiency and scalability
of autonomous agent components.
"""

import time
import unittest
from datetime import datetime

from orchestrator.agents.autonomous_base import AutonomousAgent
from orchestrator.agents.context_understanding import ContextAnalyzer
from orchestrator.agents.priority_manager import PriorityManager
from orchestrator.agents.learning_system import LearningSystem
from orchestrator.agents.coordination_system import CoordinationSystem
from orchestrator.agents.task_management import TaskManager
from orchestrator.agents.negotiation_system import NegotiationSystem


class AutonomousAgentPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for AutonomousAgent."""

    def test_context_processing_performance(self):
        """Benchmark context processing performance."""
        agent = AutonomousAgent("perf_agent", "Performance Agent")
        
        # Create contexts of different sizes
        contexts = [
            self._create_context(size=10),    # Small
            self._create_context(size=50),    # Medium
            self._create_context(size=100),   # Large
            self._create_context(size=200)    # Very large
        ]
        
        for i, context in enumerate(contexts):
            start_time = time.time()
            
            # Run multiple iterations for more accurate measurement
            iterations = max(1, 100 // (i + 1))  # Adjust iterations based on context size
            for _ in range(iterations):
                agent.run(context)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            print(f"Context processing (size {len(context)}): {avg_time:.4f}s per operation")
            
            # Basic performance assertions
            if len(context) <= 50:
                self.assertLess(avg_time, 0.1, f"Small context processing should be fast: {avg_time}s")
            elif len(context) <= 100:
                self.assertLess(avg_time, 0.2, f"Medium context processing should be reasonable: {avg_time}s")

    def test_memory_management_performance(self):
        """Benchmark memory management performance."""
        agent = AutonomousAgent("mem_agent", "Memory Agent")
        
        # Add many contexts to test memory management
        start_time = time.time()
        
        for i in range(150):  # More than memory limit
            context = self._create_context(size=20)
            agent.run(context)
        
        end_time = time.time()
        
        # Memory should be managed (not grow indefinitely)
        self.assertLess(len(agent.context_memory), 110, "Memory should be managed efficiently")
        
        memory_management_time = end_time - start_time
        print(f"Memory management (150 contexts): {memory_management_time:.2f}s total")
        
        # Should complete in reasonable time
        self.assertLess(memory_management_time, 10.0, "Memory management should be efficient")

    def _create_context(self, size: int) -> dict:
        """Create a context of specified size for testing."""
        context = {
            "task_id": f"task_{size}",
            "priority": 5,
            "description": "Test task" * (size // 10)
        }
        
        # Add additional fields to reach desired size
        for i in range(size - 3):
            context[f"field_{i}"] = f"value_{i}"
        
        return context


class ContextAnalyzerPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for ContextAnalyzer."""

    def test_context_analysis_performance(self):
        """Benchmark context analysis performance."""
        analyzer = ContextAnalyzer()
        
        # Create contexts with different complexity
        contexts = [
            self._create_simple_context(),
            self._create_medium_context(),
            self._create_complex_context()
        ]
        
        for i, context in enumerate(contexts):
            start_time = time.time()
            
            # Run multiple iterations
            iterations = 10
            for _ in range(iterations):
                analyzer.analyze_context(context)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            complexity = "simple" if i == 0 else "medium" if i == 1 else "complex"
            print(f"Context analysis ({complexity}): {avg_time:.4f}s per operation")
            
            # Performance assertions
            if i == 0:  # Simple context
                self.assertLess(avg_time, 0.05, "Simple context analysis should be very fast")
            elif i == 1:  # Medium context
                self.assertLess(avg_time, 0.1, "Medium context analysis should be fast")

    def test_knowledge_base_performance(self):
        """Benchmark knowledge base performance."""
        analyzer = ContextAnalyzer()
        
        # Add many contexts to knowledge base
        start_time = time.time()
        
        for i in range(250):  # More than knowledge base limit
            context = self._create_simple_context()
            analyzer.analyze_context(context)
        
        end_time = time.time()
        
        # Knowledge base should be managed efficiently
        self.assertLess(len(analyzer.knowledge_base), 210, "Knowledge base should be managed")
        
        knowledge_base_time = end_time - start_time
        print(f"Knowledge base management (250 contexts): {knowledge_base_time:.2f}s total")
        
        self.assertLess(knowledge_base_time, 15.0, "Knowledge base management should be efficient")

    def _create_simple_context(self) -> dict:
        """Create a simple context for testing."""
        return {
            "tasks": [
                {"id": "task_1", "priority": 5, "dependencies": []}
            ],
            "resources": {
                "resource_1": {"availability": 0.8, "contention": 0.2}
            }
        }

    def _create_medium_context(self) -> dict:
        """Create a medium complexity context."""
        return {
            "tasks": [
                {"id": "task_1", "priority": 7, "dependencies": ["task_2"], "required_resources": ["resource_1"]},
                {"id": "task_2", "priority": 5, "dependencies": [], "required_resources": ["resource_2"]},
                {"id": "task_3", "priority": 3, "dependencies": ["task_1"], "required_resources": ["resource_1", "resource_2"]}
            ],
            "resources": {
                "resource_1": {"availability": 0.6, "contention": 0.4, "type": "critical"},
                "resource_2": {"availability": 0.9, "contention": 0.1, "type": "standard"}
            },
            "workflow": {
                "steps": ["analysis", "development", "testing", "deployment"],
                "current_step": "development"
            }
        }

    def _create_complex_context(self) -> dict:
        """Create a complex context for testing."""
        tasks = []
        resources = {}
        
        # Create 10 tasks with complex relationships
        for i in range(10):
            task_id = f"task_{i+1}"
            dependencies = [f"task_{j+1}" for j in range(i) if j % 2 == 0]  # Some dependencies
            required_resources = [f"resource_{j+1}" for j in range(3) if (i + j) % 3 == 0]
            
            tasks.append({
                "id": task_id,
                "name": f"Complex Task {i+1}",
                "priority": 5 + (i % 3),
                "dependencies": dependencies,
                "required_resources": required_resources,
                "description": f"This is a complex task number {i+1} with multiple components and requirements"
            })
            
            # Create resources
            for res_id in required_resources:
                if res_id not in resources:
                    resources[res_id] = {
                        "name": f"Resource {res_id}",
                        "availability": 0.5 + (i % 5) * 0.1,
                        "contention": 0.1 + (i % 4) * 0.1,
                        "type": "standard" if i % 2 == 0 else "critical"
                    }
        
        return {
            "tasks": tasks,
            "resources": resources,
            "workflow": {
                "steps": [f"step_{i+1}" for i in range(8)],
                "current_step": "step_4",
                "bottlenecks": [
                    {"location": "step_3", "severity": "medium"},
                    {"location": "step_6", "severity": "high"}
                ]
            },
            "agents": [
                {"agent_id": f"agent_{i+1}", "status": "active", "priority": 5 + (i % 2)}
                for i in range(5)
            ]
        }


class PriorityManagerPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for PriorityManager."""

    def test_priority_calculation_performance(self):
        """Benchmark priority calculation performance."""
        priority_manager = PriorityManager()
        
        # Create task sets of different sizes
        task_sets = [
            self._create_task_set(10),   # Small
            self._create_task_set(50),   # Medium
            self._create_task_set(100),  # Large
            self._create_task_set(200)   # Very large
        ]
        
        for i, tasks in enumerate(task_sets):
            start_time = time.time()
            
            # Test different strategies
            strategies = ["default", "dependency_aware", "resource_aware", "balanced"]
            
            for strategy in strategies:
                priority_manager.set_strategy(strategy)
                iterations = max(1, 50 // (i + 1))
                
                for _ in range(iterations):
                    priority_manager.calculate_priorities(tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time_per_strategy = total_time / (len(strategies) * iterations)
            
            size = "small" if i == 0 else "medium" if i == 1 else "large" if i == 2 else "very large"
            print(f"Priority calculation ({size} - {len(tasks)} tasks): {avg_time_per_strategy:.4f}s per strategy")
            
            # Performance assertions
            if len(tasks) <= 50:
                self.assertLess(avg_time_per_strategy, 0.1, f"Small task set should be fast: {avg_time_per_strategy}s")
            elif len(tasks) <= 100:
                self.assertLess(avg_time_per_strategy, 0.2, f"Medium task set should be reasonable: {avg_time_per_strategy}s")

    def test_strategy_switching_performance(self):
        """Benchmark strategy switching performance."""
        priority_manager = PriorityManager()
        tasks = self._create_task_set(20)
        
        start_time = time.time()
        
        # Switch strategies multiple times
        strategies = ["default", "dependency_aware", "resource_aware", "balanced", "deadline_aware"]
        for _ in range(10):  # 10 cycles
            for strategy in strategies:
                priority_manager.set_strategy(strategy)
                priority_manager.calculate_priorities(tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / (len(strategies) * 10)
        
        print(f"Strategy switching: {avg_time:.4f}s per strategy switch")
        
        # Should be very fast
        self.assertLess(avg_time, 0.05, "Strategy switching should be very fast")

    def _create_task_set(self, size: int) -> list:
        """Create a set of tasks for testing."""
        tasks = []
        
        for i in range(size):
            dependencies = [f"task_{j}" for j in range(i) if j % 3 == 0 and j < i]
            required_resources = [f"resource_{j % 5 + 1}" for j in range(2)]
            
            task = {
                "id": f"task_{i}",
                "name": f"Task {i}",
                "priority": 3 + (i % 5),
                "dependencies": dependencies,
                "required_resources": required_resources,
                "description": f"Test task number {i}"
            }
            
            # Add deadline to some tasks
            if i % 4 == 0:
                task["deadline"] = (datetime.now() + timedelta(days=i % 7 + 1)).isoformat()
            
            tasks.append(task)
        
        return tasks


class LearningSystemPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for LearningSystem."""

    def test_feedback_processing_performance(self):
        """Benchmark feedback processing performance."""
        learning_system = LearningSystem()
        
        # Create feedback items of different complexity
        feedback_items = [
            self._create_simple_feedback(),
            self._create_medium_feedback(),
            self._create_complex_feedback()
        ]
        
        for i, feedback in enumerate(feedback_items):
            start_time = time.time()
            
            # Process feedback multiple times
            iterations = 20
            for _ in range(iterations):
                learning_system.process_feedback(feedback)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            complexity = "simple" if i == 0 else "medium" if i == 1 else "complex"
            print(f"Feedback processing ({complexity}): {avg_time:.4f}s per feedback")
            
            # Performance assertions
            if i == 0:  # Simple feedback
                self.assertLess(avg_time, 0.01, "Simple feedback processing should be very fast")
            elif i == 1:  # Medium feedback
                self.assertLess(avg_time, 0.02, "Medium feedback processing should be fast")

    def test_learning_cycle_performance(self):
        """Benchmark learning cycle performance."""
        learning_system = LearningSystem()
        
        # Add some feedback first
        for _ in range(20):
            learning_system.process_feedback(self._create_simple_feedback())
        
        start_time = time.time()
        
        # Perform multiple learning cycles
        iterations = 5
        for _ in range(iterations):
            learning_system.perform_learning_cycle()
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        print(f"Learning cycle: {avg_time:.4f}s per cycle")
        
        # Should be reasonably fast
        self.assertLess(avg_time, 0.5, "Learning cycles should be efficient")

    def _create_simple_feedback(self) -> dict:
        """Create simple feedback for testing."""
        return {
            "type": "priority_adjustment",
            "adjustments": [
                {"reason": "dependency_analysis", "effectiveness": 0.8}
            ]
        }

    def _create_medium_feedback(self) -> dict:
        """Create medium complexity feedback."""
        return {
            "type": "resource_management",
            "resource_usage": {
                f"resource_{i}": {
                    "availability": 0.5 + (i % 5) * 0.1,
                    "contention": 0.1 + (i % 4) * 0.1,
                    "usage_pattern": "intermittent"
                } for i in range(5)
            },
            "suggestions": [
                {"type": "optimization", "resource": "resource_1", "action": "increase_capacity"},
                {"type": "scheduling", "resource": "resource_3", "action": "balance_load"}
            ]
        }

    def _create_complex_feedback(self) -> dict:
        """Create complex feedback for testing."""
        return {
            "type": "performance",
            "metrics": {
                "strategy_performance": {
                    f"strategy_{i}": {
                        "success_rate": 0.6 + (i % 5) * 0.05,
                        "average_time": 1.0 + (i % 3) * 0.5,
                        "resource_usage": 0.3 + (i % 4) * 0.1
                    } for i in range(8)
                },
                "overall_performance": {
                    "efficiency": 0.75,
                    "effectiveness": 0.82,
                    "adaptation_rate": 0.68
                }
            },
            "recommendations": [
                {
                    "area": "priority_management",
                    "suggestion": "Use dependency_aware strategy more frequently",
                    "expected_improvement": 0.15
                },
                {
                    "area": "resource_allocation",
                    "suggestion": "Implement dynamic resource pooling",
                    "expected_improvement": 0.20
                }
            ],
            "context": {
                "workload": "high",
                "environment": "production",
                "team_size": 8
            }
        }


class CoordinationSystemPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for CoordinationSystem."""

    def test_conflict_resolution_performance(self):
        """Benchmark conflict resolution performance."""
        coordination_system = CoordinationSystem()
        
        # Create conflicts of different complexity
        conflicts = [
            self._create_simple_conflict(),
            self._create_medium_conflict(),
            self._create_complex_conflict()
        ]
        
        for i, conflict in enumerate(conflicts):
            start_time = time.time()
            
            # Resolve conflict multiple times
            iterations = 15
            for _ in range(iterations):
                coordination_system.handle_coordination_request(conflict)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            complexity = "simple" if i == 0 else "medium" if i == 1 else "complex"
            print(f"Conflict resolution ({complexity}): {avg_time:.4f}s per conflict")
            
            # Performance assertions
            if i == 0:  # Simple conflict
                self.assertLess(avg_time, 0.01, "Simple conflict resolution should be very fast")
            elif i == 1:  # Medium conflict
                self.assertLess(avg_time, 0.02, "Medium conflict resolution should be fast")

    def test_negotiation_performance(self):
        """Benchmark negotiation performance."""
        coordination_system = CoordinationSystem()
        
        # Test different negotiation types
        negotiation_contexts = [
            ("resource_allocation", self._create_resource_negotiation_context()),
            ("task_prioritization", self._create_prioritization_negotiation_context()),
            ("workflow_coordination", self._create_workflow_negotiation_context())
        ]
        
        for negotiation_type, context in negotiation_contexts:
            start_time = time.time()
            
            # Perform negotiation multiple times
            iterations = 10
            for _ in range(iterations):
                coordination_system.initiate_negotiation(negotiation_type, context["participants"], context)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            print(f"Negotiation ({negotiation_type}): {avg_time:.4f}s per negotiation")
            
            # Performance assertions
            self.assertLess(avg_time, 0.05, f"{negotiation_type} negotiation should be efficient")

    def _create_simple_conflict(self) -> dict:
        """Create a simple conflict for testing."""
        return {
            "conflict_type": "resource_conflict",
            "resource_id": "test_resource",
            "requesting_agent": "agent_1",
            "conflicting_agent": "agent_2",
            "resource_info": {"availability": 0.6, "contention": 0.3}
        }

    def _create_medium_conflict(self) -> dict:
        """Create a medium complexity conflict."""
        return {
            "conflict_type": "priority_conflict",
            "involved_tasks": ["task_1", "task_2", "task_3"],
            "task_task_1": {
                "id": "task_1",
                "priority": 8,
                "dependencies": ["task_2"],
                "deadline": (datetime.now() + timedelta(days=2)).isoformat()
            },
            "task_task_2": {
                "id": "task_2",
                "priority": 6,
                "dependencies": [],
                "required_resources": ["resource_1"]
            },
            "task_task_3": {
                "id": "task_3",
                "priority": 7,
                "dependencies": ["task_1"],
                "required_resources": ["resource_2"]
            }
        }

    def _create_complex_conflict(self) -> dict:
        """Create a complex conflict for testing."""
        conflict = {
            "conflict_type": "agent_coordination",
            "agents_involved": [f"agent_{i}" for i in range(5)],
            "coordination_type": "workflow_sync",
            "workflow_context": {
                "current_step": "development",
                "steps": ["analysis", "design", "development", "testing", "deployment"],
                "dependencies": {
                    f"step_{i}": [f"step_{j}" for j in range(i)] for i in range(1, 5)
                }
            },
            "resource_context": {
                f"resource_{i}": {
                    "availability": 0.4 + (i % 6) * 0.1,
                    "contention": 0.1 + (i % 5) * 0.15,
                    "critical": i % 3 == 0
                } for i in range(8)
            }
        }
        
        # Add detailed agent information
        for i, agent_id in enumerate(conflict["agents_involved"]):
            conflict[f"{agent_id}_context"] = {
                "priority": 5 + (i % 3),
                "current_task": f"task_{i % 4 + 1}",
                "required_resources": [f"resource_{j}" for j in range(3) if (i + j) % 2 == 0],
                "flexibility": 0.3 + (i % 4) * 0.15
            }
        
        return conflict

    def _create_resource_negotiation_context(self) -> dict:
        """Create resource negotiation context."""
        return {
            "participants": ["agent_1", "agent_2", "agent_3"],
            "resources": {
                "resource_1": {"availability": 0.6, "contention": 0.4},
                "resource_2": {"availability": 0.8, "contention": 0.2}
            },
            "agent_1_priority": 7,
            "agent_2_priority": 5,
            "agent_3_priority": 6,
            "agent_1_required_resources": ["resource_1", "resource_2"],
            "agent_2_required_resources": ["resource_1"],
            "agent_3_required_resources": ["resource_2"]
        }

    def _create_prioritization_negotiation_context(self) -> dict:
        """Create task prioritization negotiation context."""
        return {
            "participants": ["agent_1", "agent_2"],
            "tasks": ["task_1", "task_2", "task_3", "task_4"],
            "agent_1_task_1_priority": 8,
            "agent_1_task_2_priority": 6,
            "agent_1_task_3_priority": 7,
            "agent_1_task_4_priority": 5,
            "agent_2_task_1_priority": 7,
            "agent_2_task_2_priority": 9,
            "agent_2_task_3_priority": 6,
            "agent_2_task_4_priority": 8
        }

    def _create_workflow_negotiation_context(self) -> dict:
        """Create workflow coordination negotiation context."""
        return {
            "participants": ["agent_1", "agent_2", "agent_3"],
            "communication_frequency": "regular",
            "synchronization_points": ["task_completion", "milestone_reached", "daily_sync"],
            "conflict_resolution": "negotiation_based",
            "status_reporting": "continuous",
            "resource_sharing": "cooperative",
            "decision_making": "consensus_based"
        }


class TaskManagerPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for TaskManager."""

    def test_task_splitting_performance(self):
        """Benchmark task splitting performance."""
        task_manager = TaskManager()
        
        # Create tasks of different complexity
        tasks = [
            self._create_simple_task(),
            self._create_medium_task(),
            self._create_complex_task()
        ]
        
        strategies = ["size_based", "complexity_based", "resource_based"]
        
        for i, task in enumerate(tasks):
            for strategy in strategies:
                start_time = time.time()
                
                # Split task multiple times
                iterations = 8
                for _ in range(iterations):
                    task_manager.split_task(task, strategy)
                
                end_time = time.time()
                avg_time = (end_time - start_time) / iterations
                
                complexity = "simple" if i == 0 else "medium" if i == 1 else "complex"
                print(f"Task splitting ({complexity} - {strategy}): {avg_time:.4f}s per split")
                
                # Performance assertions
                if i == 0:  # Simple task
                    self.assertLess(avg_time, 0.02, f"Simple task splitting should be fast: {avg_time}s")
                elif i == 1:  # Medium task
                    self.assertLess(avg_time, 0.05, f"Medium task splitting should be reasonable: {avg_time}s")

    def test_task_integration_performance(self):
        """Benchmark task integration performance."""
        task_manager = TaskManager()
        
        # Create subtask sets of different sizes
        subtask_sets = [
            self._create_subtask_set(5),   # Small
            self._create_subtask_set(15),  # Medium
            self._create_subtask_set(30)   # Large
        ]
        
        strategies = ["sequential", "parallel", "conditional"]
        
        for i, subtasks in enumerate(subtask_sets):
            for strategy in strategies:
                start_time = time.time()
                
                # Integrate tasks multiple times
                iterations = 5
                for _ in range(iterations):
                    task_manager.integrate_tasks(subtasks, strategy)
                
                end_time = time.time()
                avg_time = (end_time - start_time) / iterations
                
                size = "small" if i == 0 else "medium" if i == 1 else "large"
                print(f"Task integration ({size} - {len(subtasks)} subtasks - {strategy}): {avg_time:.4f}s per integration")
                
                # Performance assertions
                if len(subtasks) <= 10:
                    self.assertLess(avg_time, 0.05, f"Small subtask integration should be fast: {avg_time}s")
                elif len(subtasks) <= 20:
                    self.assertLess(avg_time, 0.1, f"Medium subtask integration should be reasonable: {avg_time}s")

    def _create_simple_task(self) -> dict:
        """Create a simple task for testing."""
        return {
            "id": "simple_task",
            "name": "Simple Task",
            "description": "A simple task with minimal complexity",
            "priority": 5,
            "dependencies": [],
            "required_resources": ["resource_1"],
            "estimated_complexity": 1.2
        }

    def _create_medium_task(self) -> dict:
        """Create a medium complexity task."""
        return {
            "id": "medium_task",
            "name": "Medium Complexity Task",
            "description": "A task with moderate complexity involving multiple components and some dependencies",
            "priority": 6,
            "dependencies": ["prereq_task_1", "prereq_task_2"],
            "required_resources": ["resource_1", "resource_2", "resource_3"],
            "estimated_complexity": 2.8,
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }

    def _create_complex_task(self) -> dict:
        """Create a complex task for testing."""
        return {
            "id": "complex_task",
            "name": "Complex Development Task",
            "description": "Develop a full-stack application with backend services, frontend components, API integrations, database design, and comprehensive testing. This task involves multiple teams and has complex dependencies and resource requirements.",
            "priority": 8,
            "dependencies": ["architecture_task", "requirements_task", "setup_task"],
            "required_resources": ["backend_server", "frontend_framework", "api_gateway", "database", "test_environment"],
            "estimated_complexity": 4.5,
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "components": [
                {"name": "Backend Services", "complexity": 2.0, "resources": ["backend_server", "database"]},
                {"name": "Frontend Components", "complexity": 1.8, "resources": ["frontend_framework"]},
                {"name": "API Integrations", "complexity": 1.5, "resources": ["api_gateway", "backend_server"]},
                {"name": "Testing Suite", "complexity": 1.2, "resources": ["test_environment", "database"]}
            ]
        }

    def _create_subtask_set(self, size: int) -> list:
        """Create a set of subtasks for testing."""
        subtasks = []
        
        for i in range(size):
            subtask = {
                "id": f"subtask_{i}",
                "original_task_id": "parent_task",
                "name": f"Subtask {i}",
                "description": f"Subtask number {i} of the parent task",
                "priority": 3 + (i % 5),
                "dependencies": [f"subtask_{j}" for j in range(i) if j % 3 == 0],
                "required_resources": [f"resource_{j % 4 + 1}" for j in range(2)],
                "status": "completed" if i % 2 == 0 else "pending",
                "result": {
                    "output": f"Result from subtask {i}",
                    "quality_score": 0.7 + (i % 3) * 0.1
                },
                "start_time": (datetime.now() - timedelta(hours=i)).isoformat(),
                "end_time": (datetime.now() - timedelta(hours=i // 2)).isoformat()
            }
            
            subtasks.append(subtask)
        
        return subtasks


class NegotiationSystemPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarks for NegotiationSystem."""

    def test_negotiation_performance(self):
        """Benchmark negotiation performance."""
        negotiation_system = NegotiationSystem()
        
        # Create negotiation contexts of different complexity
        negotiation_contexts = [
            ("resource_allocation", self._create_simple_resource_context()),
            ("task_prioritization", self._create_medium_prioritization_context()),
            ("conflict_resolution", self._create_complex_conflict_context())
        ]
        
        for negotiation_type, context in negotiation_contexts:
            start_time = time.time()
            
            # Perform negotiation multiple times
            iterations = 8
            for _ in range(iterations):
                negotiation_system.initiate_negotiation(
                    negotiation_type,
                    context["participants"],
                    context
                )
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            complexity = "simple" if negotiation_type == "resource_allocation" else "medium" if negotiation_type == "task_prioritization" else "complex"
            print(f"Negotiation ({negotiation_type} - {complexity}): {avg_time:.4f}s per negotiation")
            
            # Performance assertions
            if complexity == "simple":
                self.assertLess(avg_time, 0.05, f"Simple negotiation should be fast: {avg_time}s")
            elif complexity == "medium":
                self.assertLess(avg_time, 0.1, f"Medium negotiation should be reasonable: {avg_time}s")

    def _create_simple_resource_context(self) -> dict:
        """Create simple resource negotiation context."""
        return {
            "participants": ["agent_1", "agent_2"],
            "resources": {
                "resource_1": {"availability": 0.7, "contention": 0.3}
            },
            "agent_1_priority": 6,
            "agent_2_priority": 5,
            "agent_1_required_resources": ["resource_1"],
            "agent_2_required_resources": ["resource_1"]
        }

    def _create_medium_prioritization_context(self) -> dict:
        """Create medium complexity prioritization context."""
        return {
            "participants": ["agent_1", "agent_2", "agent_3"],
            "tasks": ["task_1", "task_2", "task_3", "task_4", "task_5"],
            "agent_1_task_1_priority": 8,
            "agent_1_task_2_priority": 6,
            "agent_1_task_3_priority": 7,
            "agent_1_task_4_priority": 5,
            "agent_1_task_5_priority": 9,
            "agent_2_task_1_priority": 7,
            "agent_2_task_2_priority": 9,
            "agent_2_task_3_priority": 6,
            "agent_2_task_4_priority": 8,
            "agent_2_task_5_priority": 7,
            "agent_3_task_1_priority": 6,
            "agent_3_task_2_priority": 8,
            "agent_3_task_3_priority": 9,
            "agent_3_task_4_priority": 7,
            "agent_3_task_5_priority": 6
        }

    def _create_complex_conflict_context(self) -> dict:
        """Create complex conflict resolution context."""
        return {
            "conflict_type": "resource_conflict",
            "participants": ["agent_1", "agent_2", "agent_3", "agent_4"],
            "resource_id": "critical_resource",
            "resource_info": {
                "availability": 0.3,
                "contention": 0.8,
                "type": "critical"
            },
            "agent_1_priority": 8,
            "agent_2_priority": 7,
            "agent_3_priority": 9,
            "agent_4_priority": 6,
            "agent_1_resource_need": 0.9,
            "agent_2_resource_need": 0.7,
            "agent_3_resource_need": 0.8,
            "agent_4_resource_need": 0.6,
            "agent_1_flexibility": 0.3,
            "agent_2_flexibility": 0.5,
            "agent_3_flexibility": 0.2,
            "agent_4_flexibility": 0.7
        }


if __name__ == "__main__":
    # Run performance benchmarks
    print("Running Autonomous Agent Performance Benchmarks...")
    print("=" * 60)
    
    # Run each benchmark suite
    suites = [
        AutonomousAgentPerformanceBenchmark,
        ContextAnalyzerPerformanceBenchmark,
        PriorityManagerPerformanceBenchmark,
        LearningSystemPerformanceBenchmark,
        CoordinationSystemPerformanceBenchmark,
        TaskManagerPerformanceBenchmark,
        NegotiationSystemPerformanceBenchmark
    ]
    
    for suite in suites:
        print(f"\n{suite.__name__}:")
        print("-" * 40)
        
        # Create test suite and run
        test_suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(test_suite)
        
        print()
    
    print("=" * 60)
    print("Performance benchmarks completed.")