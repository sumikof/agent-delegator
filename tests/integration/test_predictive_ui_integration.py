"""
Integration tests for predictive UI with the orchestration system.
"""

import pytest
from unittest.mock import Mock, patch
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry


def test_predictive_ui_integration_basic():
    """Test basic predictive UI integration with orchestrator."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Verify predictive UI adapter is initialized
    assert orchestrator.predictive_ui_adapter is not None
    assert orchestrator.predictive_ui_adapter.enabled == True


def test_predictive_ui_integration_disabled():
    """Test predictive UI interface when disabled."""
    
    # Create orchestrator with predictive UI disabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=False
    )
    
    # Verify predictive UI adapter is not initialized
    assert orchestrator.predictive_ui_adapter is None


def test_predictive_ui_status_methods():
    """Test predictive UI status and control methods."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Test status method
    status = orchestrator.get_predictive_ui_status()
    assert status['enabled'] == True
    
    # Test enable/disable methods
    orchestrator.disable_predictive_ui_interface()
    status = orchestrator.get_predictive_ui_status()
    assert status['enabled'] == False
    
    orchestrator.enable_predictive_ui_interface()
    status = orchestrator.get_predictive_ui_status()
    assert status['enabled'] == True


def test_predictive_ui_configuration():
    """Test predictive UI configuration generation."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Get optimal UI configuration
    result = orchestrator.get_optimal_ui_configuration()
    
    # Verify result structure
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'ui_configuration' in result
    
    # Verify UI configuration contains expected fields
    if result['status'] == 'success':
        ui_config = result['ui_configuration']
        assert 'color_scheme' in ui_config
        assert 'information_density' in ui_config
        assert 'layout_compactness' in ui_config


def test_predictive_ui_interaction_recording():
    """Test user interaction recording."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Record a user interaction
    interaction_data = {
        'action_type': 'click',
        'feature': 'task_button',
        'ui_theme': 'light',
        'layout_type': 'compact',
        'timestamp': '2023-01-01T12:00:00'
    }
    
    result = orchestrator.record_user_interaction(interaction_data)
    
    # Verify interaction was recorded
    assert result['status'] == 'success'


def test_predictive_ui_user_insights():
    """Test user insights generation."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Record some interactions first
    for i in range(3):
        interaction_data = {
            'action_type': f'action_{i}',
            'feature': f'feature_{i}',
            'timestamp': f'2023-01-01T12:0{i}:00'
        }
        orchestrator.record_user_interaction(interaction_data)
    
    # Get user insights
    result = orchestrator.get_user_insights()
    
    # Verify insights structure
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'interaction_insights' in result


def test_predictive_ui_preferences_update():
    """Test user preferences update."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Update user preferences
    new_preferences = {
        'ui_theme': 'dark',
        'color_scheme': 'vibrant',
        'font_size': 'large'
    }
    
    result = orchestrator.update_user_preferences(new_preferences)
    
    # Verify preferences were updated
    assert result['status'] == 'success'


def test_predictive_ui_error_handling():
    """Test error handling in predictive UI interface."""
    
    # Create orchestrator with predictive UI disabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=False
    )
    
    # Try to get UI configuration when predictive UI is disabled
    result = orchestrator.get_optimal_ui_configuration()
    
    # Should return error status
    assert result['status'] == 'error'
    assert 'message' in result


def test_predictive_ui_with_workflow():
    """Test predictive UI with actual workflow execution."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Submit some test tasks
    task1_id = orchestrator.submit_task(
        agent_type="test_agent",
        payload={"test": "data1"},
        priority="medium"
    )
    
    # Get UI configuration while tasks are running
    result = orchestrator.get_optimal_ui_configuration()
    
    # Verify system handles concurrent operations
    assert result['status'] != 'error'


def test_predictive_ui_context_adaptation():
    """Test predictive UI adaptation to different contexts."""
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Test UI configuration in different scenarios
    
    # Scenario 1: No tasks (initial state)
    result1 = orchestrator.get_optimal_ui_configuration()
    
    # Scenario 2: With tasks
    orchestrator.submit_task(agent_type="test_agent", payload={"test": "data"})
    result2 = orchestrator.get_optimal_ui_configuration()
    
    # Both should succeed but may have different configurations
    assert result1['status'] == 'success'
    assert result2['status'] == 'success'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])