"""
Unit tests for predictive UI components.
"""

import pytest
from unittest.mock import Mock, patch
from orchestrator.interfaces.predictive_ui.predictor import (
    UIPredictor, InteractionPatternAnalyzer, ContextAnalyzer
)
from orchestrator.interfaces.predictive_ui.adapter import PredictiveUIAdapter
from orchestrator.interfaces.predictive_ui.personalization import UserProfileManager


def test_interaction_pattern_analyzer_initialization():
    """Test InteractionPatternAnalyzer initialization."""
    analyzer = InteractionPatternAnalyzer()
    assert analyzer.interaction_history == []
    assert analyzer.pattern_cache == {}
    assert analyzer.learning_rate == 0.1


def test_interaction_pattern_analyzer_record_interaction():
    """Test InteractionPatternAnalyzer record_interaction method."""
    analyzer = InteractionPatternAnalyzer()
    
    # Record some interactions
    analyzer.record_interaction({'action_type': 'click', 'feature': 'button'})
    analyzer.record_interaction({'action_type': 'scroll', 'feature': 'list'})
    
    # Check that interactions were recorded
    assert len(analyzer.interaction_history) == 2
    assert analyzer.interaction_history[0]['data']['action_type'] == 'click'


def test_interaction_pattern_analyzer_analyze_patterns():
    """Test InteractionPatternAnalyzer analyze_patterns method."""
    analyzer = InteractionPatternAnalyzer()
    
    # Record some interactions for analysis
    analyzer.record_interaction({'action_type': 'click', 'ui_theme': 'dark'})
    analyzer.record_interaction({'action_type': 'click', 'ui_theme': 'dark'})
    analyzer.record_interaction({'action_type': 'scroll', 'ui_theme': 'light'})
    
    # Analyze patterns
    patterns = analyzer.analyze_patterns()
    
    # Check that patterns were identified
    assert 'frequent_actions' in patterns
    assert 'preference_trends' in patterns


def test_context_analyzer_initialization():
    """Test ContextAnalyzer initialization."""
    analyzer = ContextAnalyzer()
    assert hasattr(analyzer, 'context_rules')
    assert 'high_stress' in analyzer.context_rules


def test_context_analyzer_analyze_context():
    """Test ContextAnalyzer analyze_context method."""
    analyzer = ContextAnalyzer()
    
    # Test with high stress cognitive state
    cognitive_state = {
        'focus_level': 0.3,
        'stress_level': 0.8,
        'cognitive_load': 0.7,
        'engagement': 0.4
    }
    
    workflow_context = {
        'pending_tasks': ['task1', 'task2'],
        'current_stage': 'execution'
    }
    
    # Analyze context
    recommendations = analyzer.analyze_context(cognitive_state, workflow_context)
    
    # Check that recommendations were generated
    assert 'color_scheme' in recommendations
    assert 'information_density' in recommendations
    assert 'animation_speed' in recommendations


def test_ui_predictor_initialization():
    """Test UIPredictor initialization."""
    predictor = UIPredictor()
    assert isinstance(predictor.pattern_analyzer, InteractionPatternAnalyzer)
    assert isinstance(predictor.context_analyzer, ContextAnalyzer)
    assert predictor.prediction_cache == {}


def test_ui_predictor_predict_optimal_ui():
    """Test UIPredictor predict_optimal_ui method."""
    predictor = UIPredictor()
    
    # Test with sample cognitive state and workflow context
    cognitive_state = {
        'focus_level': 0.7,
        'stress_level': 0.3,
        'cognitive_load': 0.5,
        'engagement': 0.8
    }
    
    workflow_context = {
        'pending_tasks': ['task1'],
        'current_stage': 'execution'
    }
    
    # Predict optimal UI
    ui_config = predictor.predict_optimal_ui(cognitive_state, workflow_context)
    
    # Check that UI configuration was generated
    assert isinstance(ui_config, dict)
    assert 'color_scheme' in ui_config
    assert 'information_density' in ui_config


def test_user_profile_manager_initialization():
    """Test UserProfileManager initialization."""
    with patch('os.path.exists', return_value=False):
        with patch('os.makedirs'):
            manager = UserProfileManager()
            assert manager.current_user_id == "default_user"
            assert 'preferences' in manager.user_profile


def test_user_profile_manager_get_preferences():
    """Test UserProfileManager get_user_preferences method."""
    with patch('os.path.exists', return_value=False):
        with patch('os.makedirs'):
            manager = UserProfileManager()
            preferences = manager.get_user_preferences()
            
            # Check that default preferences were returned
            assert 'ui_theme' in preferences
            assert 'color_scheme' in preferences


def test_user_profile_manager_update_preferences():
    """Test UserProfileManager update_preferences method."""
    with patch('os.path.exists', return_value=False):
        with patch('os.makedirs'):
            with patch('builtins.open'):
                manager = UserProfileManager()
                
                # Update preferences
                new_prefs = {'ui_theme': 'dark', 'font_size': 'large'}
                manager.update_preferences(new_prefs)
                
                # Check that preferences were updated
                updated_prefs = manager.get_user_preferences()
                assert updated_prefs['ui_theme'] == 'dark'
                assert updated_prefs['font_size'] == 'large'


def test_predictive_ui_adapter_initialization():
    """Test PredictiveUIAdapter initialization."""
    mock_orchestrator = Mock()
    adapter = PredictiveUIAdapter(mock_orchestrator)
    
    assert adapter.orchestrator == mock_orchestrator
    assert adapter.enabled == True
    assert isinstance(adapter.ui_predictor, UIPredictor)
    assert isinstance(adapter.profile_manager, UserProfileManager)


def test_predictive_ui_adapter_get_optimal_ui():
    """Test PredictiveUIAdapter get_optimal_ui_configuration method."""
    mock_orchestrator = Mock()
    adapter = PredictiveUIAdapter(mock_orchestrator)
    
    # Mock the orchestrator methods
    mock_orchestrator.get_brainwave_status.return_value = {'enabled': False}
    mock_orchestrator.task_queue.get_all_tasks.return_value = []
    
    # Get optimal UI configuration
    result = adapter.get_optimal_ui_configuration()
    
    # Check that result was returned
    assert 'status' in result
    assert 'ui_configuration' in result


def test_predictive_ui_adapter_record_interaction():
    """Test PredictiveUIAdapter record_user_interaction method."""
    mock_orchestrator = Mock()
    adapter = PredictiveUIAdapter(mock_orchestrator)
    
    # Record a user interaction
    interaction_data = {
        'action_type': 'click',
        'feature': 'button',
        'timestamp': '2023-01-01T00:00:00'
    }
    
    result = adapter.record_user_interaction(interaction_data)
    
    # Check that interaction was recorded
    assert result['status'] == 'success'


def test_predictive_ui_adapter_disabled():
    """Test PredictiveUIAdapter when disabled."""
    mock_orchestrator = Mock()
    adapter = PredictiveUIAdapter(mock_orchestrator)
    adapter.disable()
    
    # Try to get optimal UI when disabled
    result = adapter.get_optimal_ui_configuration()
    
    # Should return disabled status
    assert result['status'] == 'disabled'


@patch('orchestrator.interfaces.predictive_ui.adapter.PredictiveUIAdapter')
def test_parallel_orchestrator_predictive_ui_integration(mock_adapter_class):
    """Test ParallelOrchestrator predictive UI integration."""
    from orchestrator.parallel.orchestrator import ParallelOrchestrator
    from orchestrator.agents.registry import AgentRegistry
    
    # Create mock adapter instance
    mock_adapter_instance = Mock()
    mock_adapter_class.return_value = mock_adapter_instance
    
    # Create orchestrator with predictive UI enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2, 
        agent_registry=AgentRegistry(),
        enable_predictive_ui=True
    )
    
    # Should have predictive UI adapter
    assert orchestrator.predictive_ui_adapter == mock_adapter_instance
    
    # Test predictive UI methods
    orchestrator.get_optimal_ui_configuration()
    mock_adapter_instance.get_optimal_ui_configuration.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])