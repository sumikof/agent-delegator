"""
Integration tests for brainwave interface with the orchestration system.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from orchestrator.agents.registry import AgentRegistry


def test_brainwave_integration_basic():
    """Test basic brainwave integration with orchestrator."""
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Verify brainwave adapter is initialized
    assert orchestrator.brainwave_adapter is not None
    assert orchestrator.brainwave_adapter.enabled == True


def test_brainwave_integration_disabled():
    """Test brainwave interface when disabled."""
    
    # Create orchestrator with brainwave disabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=False
    )
    
    # Verify brainwave adapter is not initialized
    assert orchestrator.brainwave_adapter is None


def test_brainwave_status_methods():
    """Test brainwave status and control methods."""
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Test status method
    status = orchestrator.get_brainwave_status()
    assert status['enabled'] == True
    
    # Test enable/disable methods
    orchestrator.disable_brainwave_interface()
    status = orchestrator.get_brainwave_status()
    assert status['enabled'] == False
    
    orchestrator.enable_brainwave_interface()
    status = orchestrator.get_brainwave_status()
    assert status['enabled'] == True


def test_brainwave_workflow_control():
    """Test brainwave-based workflow control methods."""
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Test task control methods
    result = orchestrator.start_next_task()
    assert 'status' in result
    
    result = orchestrator.pause_current_task()
    assert 'status' in result
    
    result = orchestrator.adjust_task_priorities()
    assert 'status' in result
    
    result = orchestrator.suggest_user_break()
    assert 'status' in result


def test_brainwave_eeg_processing():
    """Test EEG data processing through brainwave interface."""
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Create mock EEG data (8 channels, 256 samples)
    eeg_data = np.random.randn(8, 256)
    
    # Process EEG data
    result = orchestrator.handle_brainwave_input(eeg_data)
    
    # Verify result structure
    assert isinstance(result, dict)
    assert 'eeg_processing' in result
    assert 'action_taken' in result
    
    # Verify EEG processing contains expected fields
    if result['eeg_processing']:
        eeg_result = result['eeg_processing']
        assert 'focus_level' in eeg_result
        assert 'stress_level' in eeg_result
        assert 'cognitive_load' in eeg_result
        assert 'engagement' in eeg_result


def test_brainwave_action_triggering():
    """Test action triggering based on cognitive states."""
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Create mock EEG data that should trigger actions
    # This is a simplified test - in practice, the EEG data would need to
    # be crafted to produce specific cognitive states
    eeg_data = np.random.randn(8, 256)
    
    # Process multiple EEG samples to test different scenarios
    results = []
    for _ in range(5):
        result = orchestrator.handle_brainwave_input(eeg_data)
        results.append(result)
    
    # Check that some actions were triggered
    actions_triggered = [r for r in results if r['action_taken'] is not None]
    assert len(actions_triggered) > 0, "Expected some actions to be triggered"


def test_brainwave_error_handling():
    """Test error handling in brainwave interface."""
    
    # Create orchestrator with brainwave disabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=False
    )
    
    # Try to process EEG data when brainwave is disabled
    eeg_data = np.random.randn(8, 256)
    result = orchestrator.handle_brainwave_input(eeg_data)
    
    # Should return error status
    assert result['status'] == 'error'
    assert 'message' in result


def test_brainwave_with_parallel_tasks():
    """Test brainwave interface with actual parallel task execution."""
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2,
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Submit some test tasks
    task1_id = orchestrator.submit_task(
        agent_type="test_agent",
        payload={"test": "data1"},
        priority="medium"
    )
    
    task2_id = orchestrator.submit_task(
        agent_type="test_agent",
        payload={"test": "data2"},
        priority="high"
    )
    
    # Process EEG data while tasks are running
    eeg_data = np.random.randn(8, 256)
    result = orchestrator.handle_brainwave_input(eeg_data)
    
    # Verify system handles concurrent operations
    assert result['status'] != 'error'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])