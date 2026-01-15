"""
Test cases for self-organizing AI agent system
"""

import pytest
from unittest.mock import Mock, MagicMock
from orchestrator.self_organizing.engine import SelfOrganizingEngine, AgentProfile, SystemState
from orchestrator.self_organizing.adaptation import AdaptationAlgorithm, AdaptationStrategy
from orchestrator.self_organizing.role_assignment import RoleAssignmentSystem, RoleRequirement, AgentCapability
from orchestrator.self_organizing.communication import CommunicationTopologyManager, CommunicationLink, CommunicationTopology


def test_agent_profile_creation():
    """Test AgentProfile creation"""
    profile = AgentProfile(
        agent_id="test_agent",
        capabilities=["coding", "testing"],
        performance_metrics={"success_rate": 0.95, "response_time": 0.8},
        current_role="developer",
        adaptability_score=0.9
    )
    
    assert profile.agent_id == "test_agent"
    assert profile.capabilities == ["coding", "testing"]
    assert profile.current_role == "developer"
    assert profile.adaptability_score == 0.9


def test_system_state_creation():
    """Test SystemState creation"""
    profiles = {
        "agent1": AgentProfile(
            agent_id="agent1",
            capabilities=["planning"],
            performance_metrics={"success_rate": 0.9},
            current_role="planner",
            adaptability_score=0.8
        )
    }
    
    state = SystemState(
        agent_profiles=profiles,
        task_queue_status={"queue_length": 5},
        communication_topology={"links": []},
        performance_metrics={"stability": 0.95}
    )
    
    assert len(state.agent_profiles) == 1
    assert state.task_queue_status["queue_length"] == 5


def test_self_organizing_engine_initialization():
    """Test SelfOrganizingEngine initialization"""
    mock_registry = Mock()
    mock_monitor = Mock()
    
    # Mock the registry to return agent info
    mock_registry.get_all_agents.return_value = {
        "agent1": {
            "capabilities": ["coding"],
            "current_role": "developer",
            "performance_metrics": {"success_rate": 0.9},
            "adaptability_score": 0.8
        }
    }
    
    engine = SelfOrganizingEngine(mock_registry, mock_monitor)
    
    assert engine.adaptation_threshold == 0.75
    assert engine.adaptation_cooldown == 300
    assert len(engine.get_system_state().agent_profiles) == 1


def test_adaptation_algorithm_initialization():
    """Test AdaptationAlgorithm initialization"""
    algorithm = AdaptationAlgorithm()
    
    assert len(algorithm.strategies) == 4
    assert algorithm.max_history_length == 100
    
    # Check that all expected strategies are present
    strategy_names = [s.name for s in algorithm.strategies]
    expected_strategies = ["role_swap", "load_balancing", "capability_matching", "performance_based"]
    
    for expected in expected_strategies:
        assert expected in strategy_names


def test_role_assignment_system_initialization():
    """Test RoleAssignmentSystem initialization"""
    system = RoleAssignmentSystem()
    
    assert len(system.role_requirements) == 5
    assert len(system.agent_capabilities) == 0
    
    # Check that all expected roles are present
    role_names = [r.role_name for r in system.role_requirements]
    expected_roles = ["orchestrator", "planner", "developer", "reviewer", "tester"]
    
    for expected in expected_roles:
        assert expected in role_names


def test_communication_topology_manager_initialization():
    """Test CommunicationTopologyManager initialization"""
    manager = CommunicationTopologyManager()
    
    assert len(manager.current_topology.links) == 0
    assert len(manager.current_topology.clusters) == 0
    assert len(manager.agent_positions) == 0


def test_role_assignment_system_register_agent():
    """Test agent registration in RoleAssignmentSystem"""
    system = RoleAssignmentSystem()
    
    system.register_agent(
        agent_id="test_agent",
        capabilities=["coding", "testing"],
        current_role="developer",
        performance_score=0.9
    )
    
    assert len(system.agent_capabilities) == 1
    assert "test_agent" in system.agent_capabilities
    
    agent_cap = system.agent_capabilities["test_agent"]
    assert agent_cap.agent_id == "test_agent"
    assert agent_cap.capabilities == ["coding", "testing"]
    assert agent_cap.current_role == "developer"
    assert agent_cap.performance_score == 0.9


def test_communication_topology_manager_initialize_topology():
    """Test topology initialization"""
    manager = CommunicationTopologyManager()
    agent_ids = ["agent1", "agent2", "agent3"]
    
    manager.initialize_topology(agent_ids)
    
    # Check that links were created
    assert len(manager.current_topology.links) > 0
    
    # Check that clusters were created
    assert len(manager.current_topology.clusters) == 1
    assert "default" in manager.current_topology.clusters
    
    # Check that agent positions were set
    assert len(manager.agent_positions) == 3


def test_self_organizing_engine_monitor_environment():
    """Test environment monitoring"""
    mock_registry = Mock()
    mock_monitor = Mock()
    
    # Mock the monitor to return performance data
    mock_monitor.get_task_queue_status.return_value = {"queue_length": 3, "max_capacity": 10}
    mock_monitor.get_current_metrics.return_value = {"stability_score": 0.85}
    
    # Mock the registry to return agent info
    mock_registry.get_all_agents.return_value = {
        "agent1": {
            "capabilities": ["coding"],
            "current_role": "developer",
            "performance_metrics": {"success_rate": 0.9},
            "adaptability_score": 0.8
        }
    }
    
    engine = SelfOrganizingEngine(mock_registry, mock_monitor)
    environment_data = engine.monitor_environment()
    
    assert "timestamp" in environment_data
    assert "agents" in environment_data
    assert "tasks" in environment_data
    assert "performance" in environment_data
    
    assert len(environment_data["agents"]) == 1
    assert environment_data["tasks"]["queue_length"] == 3


def test_self_organizing_engine_evaluate_adaptation_needed():
    """Test adaptation evaluation"""
    mock_registry = Mock()
    mock_monitor = Mock()
    
    # Mock the monitor to return performance data indicating adaptation is needed
    mock_monitor.get_task_queue_status.return_value = {"queue_length": 8, "max_capacity": 10}
    mock_monitor.get_current_metrics.return_value = {"stability_score": 0.6}
    
    # Mock the registry to return agent info with low performance
    mock_registry.get_all_agents.return_value = {
        "agent1": {
            "capabilities": ["coding"],
            "current_role": "developer",
            "performance_metrics": {"success_rate": 0.6},
            "adaptability_score": 0.8
        }
    }
    
    engine = SelfOrganizingEngine(mock_registry, mock_monitor)
    
    # Force cooldown to be expired
    engine.last_adaptation_time = 0
    
    # This should indicate adaptation is needed
    needs_adaptation = engine.evaluate_adaptation_needed()
    
    # The adaptation score should be high due to high task load and low performance/stability
    assert needs_adaptation == True


def test_adaptation_algorithm_select_strategy():
    """Test strategy selection"""
    algorithm = AdaptationAlgorithm()
    
    # Mock system state
    system_state = {
        "agent_count": 5,
        "task_load": 0.8,
        "performance": 0.7
    }
    
    # Select a strategy (should return one of the available strategies)
    strategy = algorithm.select_strategy(system_state)
    
    assert isinstance(strategy, AdaptationStrategy)
    assert strategy.name in ["role_swap", "load_balancing", "capability_matching", "performance_based"]


def test_role_assignment_system_assign_roles():
    """Test role assignment"""
    system = RoleAssignmentSystem()
    
    # Register some agents
    system.register_agent("agent1", ["coding", "planning"], "idle", 0.9)
    system.register_agent("agent2", ["coding", "testing"], "idle", 0.8)
    system.register_agent("agent3", ["reviewing"], "idle", 0.7)
    
    # Assign roles
    role_assignment = system.assign_roles()
    
    # Check that roles were assigned
    assert len(role_assignment) == 3
    
    # Check that at least one developer was assigned (has coding capability)
    developer_count = sum(1 for role in role_assignment.values() if role == "developer")
    assert developer_count >= 1


def test_communication_topology_manager_get_communication_path():
    """Test communication path finding"""
    manager = CommunicationTopologyManager()
    
    # Initialize with some agents
    agent_ids = ["agent1", "agent2", "agent3"]
    manager.initialize_topology(agent_ids)
    
    # Test path between two agents
    path = manager.get_communication_path("agent1", "agent2")
    
    assert len(path) >= 2
    assert path[0] == "agent1"
    assert path[-1] == "agent2"


def test_communication_topology_manager_get_communication_cost():
    """Test communication cost calculation"""
    manager = CommunicationTopologyManager()
    
    # Initialize with some agents
    agent_ids = ["agent1", "agent2"]
    manager.initialize_topology(agent_ids)
    
    # Test cost between two agents
    cost = manager.get_communication_cost("agent1", "agent2")
    
    assert cost >= 0
    assert isinstance(cost, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])