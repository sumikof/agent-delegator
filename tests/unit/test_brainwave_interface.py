"""
Unit tests for brainwave interface components.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from orchestrator.interfaces.brainwave.processor import BrainwaveProcessor, SignalProcessor, FeatureExtractor, StateClassifier
from orchestrator.interfaces.brainwave.adapter import BrainwaveAgentAdapter, ActionMapper
from orchestrator.interfaces.brainwave.mapper import ActionMapper as DetailedActionMapper


def test_signal_processor_initialization():
    """Test SignalProcessor initialization."""
    processor = SignalProcessor(sampling_rate=256)
    assert processor.sampling_rate == 256
    assert processor.filter_band == (1, 50)


def test_signal_processor_clean():
    """Test SignalProcessor clean method."""
    processor = SignalProcessor()
    
    # Create mock EEG data (channels x samples)
    raw_data = np.random.randn(8, 256)  # 8 channels, 256 samples
    
    # Should return cleaned data (even if just placeholder)
    cleaned = processor.clean(raw_data)
    assert cleaned.shape == raw_data.shape


def test_feature_extractor_extract():
    """Test FeatureExtractor extract method."""
    extractor = FeatureExtractor()
    
    # Create mock cleaned EEG data
    cleaned_data = np.random.randn(8, 256)
    
    # Should return dictionary of features
    features = extractor.extract(cleaned_data)
    assert isinstance(features, dict)
    assert 'delta_power' in features
    assert 'theta_power' in features
    assert 'alpha_power' in features
    assert 'beta_power' in features
    assert 'gamma_power' in features


def test_state_classifier_classify():
    """Test StateClassifier classify method."""
    classifier = StateClassifier()
    
    # Create mock features
    features = {
        'delta_power': 0.5,
        'theta_power': 0.3,
        'alpha_power': 0.8,
        'beta_power': 0.6,
        'gamma_power': 0.4,
        'mean_amplitude': 1.2,
        'variance': 0.8,
        'hjorth_mobility': 0.7,
        'hjorth_complexity': 0.5,
        'coherence_frontal_parietal': 0.6,
        'phase_locking_value': 0.4,
        'granger_causality': 0.3
    }
    
    # Should return cognitive state classification
    state = classifier.classify(features)
    assert isinstance(state, dict)
    assert 'focus_level' in state
    assert 'stress_level' in state
    assert 'cognitive_load' in state
    assert 'engagement' in state
    assert 'confidence' in state


def test_brainwave_processor_process():
    """Test BrainwaveProcessor complete processing pipeline."""
    processor = BrainwaveProcessor()
    
    # Create mock raw EEG data
    raw_data = np.random.randn(8, 256)
    
    # Should process through complete pipeline
    result = processor.process(raw_data)
    assert isinstance(result, dict)
    assert 'focus_level' in result
    assert 'stress_level' in result
    assert 'features' in result


def test_action_mapper_initialization():
    """Test ActionMapper initialization."""
    mapper = ActionMapper()
    assert hasattr(mapper, 'thresholds')
    assert hasattr(mapper, 'action_mappings')
    assert 'focus_high' in mapper.thresholds
    assert 'stress_high' in mapper.thresholds


def test_action_mapper_map_state_to_action():
    """Test ActionMapper state to action mapping."""
    mapper = ActionMapper()
    
    # Test high focus state (should trigger start_task)
    high_focus_state = {
        'focus_level': 0.9,
        'engagement': 0.8,
        'stress_level': 0.2,
        'cognitive_load': 0.3,
        'confidence': 0.95
    }
    
    action = mapper.map_state_to_action(high_focus_state)
    assert action is not None
    assert action['type'] == 'start_task'
    
    # Test low focus state (should trigger pause_task)
    low_focus_state = {
        'focus_level': 0.2,
        'engagement': 0.3,
        'stress_level': 0.8,
        'cognitive_load': 0.4,
        'confidence': 0.7
    }
    
    action = mapper.map_state_to_action(low_focus_state)
    assert action is not None
    assert action['type'] == 'pause_task'


def test_detailed_action_mapper_methods():
    """Test DetailedActionMapper additional methods."""
    mapper = DetailedActionMapper()
    
    # Test threshold updates
    new_thresholds = {'focus_high': 0.85, 'stress_high': 0.75}
    mapper.update_thresholds(new_thresholds)
    assert mapper.thresholds['focus_high'] == 0.85
    assert mapper.thresholds['stress_high'] == 0.75
    
    # Test getting available actions
    actions = mapper.get_available_actions()
    assert isinstance(actions, list)
    assert 'start_task' in actions
    assert 'pause_task' in actions


def test_brainwave_adapter_initialization():
    """Test BrainwaveAgentAdapter initialization."""
    mock_orchestrator = Mock()
    adapter = BrainwaveAgentAdapter(mock_orchestrator)
    
    assert adapter.orchestrator == mock_orchestrator
    assert adapter.enabled == True
    assert isinstance(adapter.brainwave_processor, BrainwaveProcessor)
    assert isinstance(adapter.action_mapper, ActionMapper)


def test_brainwave_adapter_handle_input():
    """Test BrainwaveAgentAdapter handle_brainwave_input method."""
    mock_orchestrator = Mock()
    adapter = BrainwaveAgentAdapter(mock_orchestrator)
    
    # Create mock EEG data
    eeg_data = np.random.randn(8, 256)
    
    # Should process EEG data and potentially trigger actions
    result = adapter.handle_brainwave_input(eeg_data)
    assert isinstance(result, dict)
    assert 'eeg_processing' in result
    assert 'action_taken' in result


def test_brainwave_adapter_disabled():
    """Test BrainwaveAgentAdapter when disabled."""
    mock_orchestrator = Mock()
    adapter = BrainwaveAgentAdapter(mock_orchestrator)
    adapter.disable()
    
    # Create mock EEG data
    eeg_data = np.random.randn(8, 256)
    
    # Should return disabled status
    result = adapter.handle_brainwave_input(eeg_data)
    assert result['status'] == 'disabled'


@patch('orchestrator.interfaces.brainwave.adapter.BrainwaveAgentAdapter')
def test_parallel_orchestrator_brainwave_integration(mock_adapter_class):
    """Test ParallelOrchestrator brainwave integration."""
    from orchestrator.parallel.orchestrator import ParallelOrchestrator
    from orchestrator.agents.registry import AgentRegistry
    
    # Create mock adapter instance
    mock_adapter_instance = Mock()
    mock_adapter_class.return_value = mock_adapter_instance
    
    # Create orchestrator with brainwave enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2, 
        agent_registry=AgentRegistry(),
        enable_brainwave=True
    )
    
    # Should have brainwave adapter
    assert orchestrator.brainwave_adapter == mock_adapter_instance
    
    # Test brainwave methods
    mock_eeg_data = np.random.randn(8, 256)
    orchestrator.handle_brainwave_input(mock_eeg_data)
    mock_adapter_instance.handle_brainwave_input.assert_called_once_with(mock_eeg_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])