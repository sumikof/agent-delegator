"""
Integration tests for personalized experience with the orchestration system.
"""

import pytest
from unittest.mock import Mock, patch
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry


def test_personalized_experience_integration_basic():
    """Test basic personalized experience integration with orchestrator."""
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Verify personalized experience integrator is initialized
    assert orchestrator.personalized_experience_integrator is not None
    assert orchestrator.personalized_experience_integrator.enabled == True


def test_personalized_experience_integration_disabled():
    """Test personalized experience interface when disabled."""
    
    # Create orchestrator with personalized experience disabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=False
    )
    
    # Verify personalized experience integrator is not initialized
    assert orchestrator.personalized_experience_integrator is None


def test_personalized_experience_status_methods():
    """Test personalized experience status and control methods."""
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Test status method
    status = orchestrator.get_personalization_status()
    assert status['enabled'] == True
    
    # Test enable/disable methods
    orchestrator.disable_personalized_experience()
    status = orchestrator.get_personalization_status()
    assert status['enabled'] == False
    
    orchestrator.enable_personalized_experience()
    status = orchestrator.get_personalization_status()
    assert status['enabled'] == True


def test_personalized_experience_creation():
    """Test personalized experience creation."""
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Create personalized experience
    result = orchestrator.create_personalized_experience()
    
    # Verify result structure
    assert isinstance(result, dict)
    assert 'status' in result
    
    if result['status'] == 'success':
        assert 'personalized_experience' in result
        assert 'components' in result


def test_personalized_experience_profile_update():
    """Test personalized experience profile update."""
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Update profile
    profile_updates = {
        'cognitive_style': 'analytical',
        'work_pattern': 'intensive',
        'preferred_interaction': 'detailed_control'
    }
    
    result = orchestrator.update_personalized_profile(profile_updates)
    
    # Verify profile was updated
    assert result['status'] == 'success'


def test_personalized_experience_error_handling():
    """Test error handling in personalized experience interface."""
    
    # Create orchestrator with personalized experience disabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=False
    )
    
    # Try to create personalized experience when disabled
    result = orchestrator.create_personalized_experience()
    
    # Should return error status
    assert result['status'] == 'error'
    assert 'message' in result


def test_personalized_experience_with_workflow():
    """Test personalized experience with actual workflow execution."""
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Submit some test tasks
    task1_id = orchestrator.submit_task(
        agent_type="test_agent",
        payload={"test": "data1"},
        priority="medium"
    )
    
    # Create personalized experience while tasks are running
    result = orchestrator.create_personalized_experience()
    
    # Verify system handles concurrent operations
    assert result['status'] != 'error'


def test_personalized_experience_context_adaptation():
    """Test personalized experience adaptation to different contexts."""
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Test experience creation in different scenarios
    
    # Scenario 1: No tasks (initial state)
    result1 = orchestrator.create_personalized_experience()
    
    # Scenario 2: With tasks
    orchestrator.submit_task(agent_type="test_agent", payload={"test": "data"})
    result2 = orchestrator.create_personalized_experience()
    
    # Both should succeed but may have different configurations
    assert result1['status'] == 'success'
    assert result2['status'] == 'success'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])