"""
Unit tests for personalized experience components.
"""

import pytest
from unittest.mock import Mock, patch
from orchestrator.interfaces.personalized_experience.integrator import PersonalizedExperienceIntegrator
from orchestrator.interfaces.personalized_experience.adaptation_engine import AdaptationEngine
from orchestrator.interfaces.personalized_experience.feedback_system import ExperienceFeedbackSystem


def test_personalized_experience_integrator_initialization():
    """Test PersonalizedExperienceIntegrator initialization."""
    mock_orchestrator = Mock()
    integrator = PersonalizedExperienceIntegrator(mock_orchestrator)
    
    assert integrator.orchestrator == mock_orchestrator
    assert integrator.enabled == True
    assert 'cognitive_style' in integrator.user_profile
    assert 'work_pattern' in integrator.user_profile


def test_personalized_experience_integrator_create_experience():
    """Test PersonalizedExperienceIntegrator create_personalized_experience method."""
    mock_orchestrator = Mock()
    integrator = PersonalizedExperienceIntegrator(mock_orchestrator)
    
    # Mock orchestrator methods
    mock_orchestrator.get_brainwave_status.return_value = {'enabled': False}
    mock_orchestrator.get_optimal_ui_configuration.return_value = {
        'status': 'success',
        'ui_configuration': {
            'color_scheme': 'default',
            'information_density': 'medium'
        }
    }
    mock_orchestrator.get_user_insights.return_value = {
        'status': 'success',
        'interaction_insights': {
            'interaction_count': 10,
            'frequent_actions': []
        }
    }
    
    # Create personalized experience
    result = integrator.create_personalized_experience()
    
    # Check result structure
    assert result['status'] == 'success'
    assert 'personalized_experience' in result
    assert 'components' in result


def test_personalized_experience_integrator_update_profile():
    """Test PersonalizedExperienceIntegrator update_user_profile method."""
    mock_orchestrator = Mock()
    integrator = PersonalizedExperienceIntegrator(mock_orchestrator)
    
    # Update user profile
    profile_updates = {
        'cognitive_style': 'analytical',
        'work_pattern': 'intensive'
    }
    
    result = integrator.update_user_profile(profile_updates)
    
    # Check that profile was updated
    assert result['status'] == 'success'
    assert integrator.user_profile['cognitive_style'] == 'analytical'
    assert integrator.user_profile['work_pattern'] == 'intensive'


def test_personalized_experience_integrator_disabled():
    """Test PersonalizedExperienceIntegrator when disabled."""
    mock_orchestrator = Mock()
    integrator = PersonalizedExperienceIntegrator(mock_orchestrator)
    integrator.disable()
    
    # Try to create experience when disabled
    result = integrator.create_personalized_experience()
    
    # Should return disabled status
    assert result['status'] == 'disabled'


def test_adaptation_engine_initialization():
    """Test AdaptationEngine initialization."""
    engine = AdaptationEngine()
    
    assert engine.adaptation_history == []
    assert engine.performance_metrics == {}
    assert engine.learning_rate == 0.1


def test_adaptation_engine_adapt_experience():
    """Test AdaptationEngine adapt_experience method."""
    engine = AdaptationEngine()
    
    # Create sample configuration and feedback
    current_config = {
        'cognitive_profile': {'cognitive_style': 'balanced'},
        'workflow_adaptations': []
    }
    
    feedback_data = {
        'performance_metrics': {
            'task_completion_rate': 0.85,
            'average_response_time': 1.5,
            'error_rate': 0.1
        },
        'user_feedback': {
            'satisfaction': 4,
            'preferences': {'ui_theme': 'dark'}
        },
        'context_changes': {
            'time_of_day': 'day',
            'workload': 'medium'
        }
    }
    
    # Adapt experience
    adapted_config = engine.adapt_experience(current_config, feedback_data)
    
    # Check that adaptations were applied
    assert 'ui_theme' in str(adapted_config)
    assert len(engine.adaptation_history) == 1


def test_adaptation_engine_get_stats():
    """Test AdaptationEngine get_adaptation_stats method."""
    engine = AdaptationEngine()
    
    # Add some adaptation history
    current_config = {'cognitive_profile': {'cognitive_style': 'balanced'}}
    feedback_data = {
        'performance_metrics': {'task_completion_rate': 0.9},
        'user_feedback': {'satisfaction': 5},
        'context_changes': {'time_of_day': 'day'}
    }
    
    engine.adapt_experience(current_config, feedback_data)
    
    # Get stats
    stats = engine.get_adaptation_stats()
    
    # Check stats structure
    assert 'total_adaptations' in stats
    assert 'adaptation_types' in stats


def test_experience_feedback_system_initialization():
    """Test ExperienceFeedbackSystem initialization."""
    system = ExperienceFeedbackSystem()
    
    assert system.feedback_store == []
    assert system.feedback_analytics == {}
    assert system.satisfaction_history == []


def test_experience_feedback_system_record_feedback():
    """Test ExperienceFeedbackSystem record_feedback method."""
    system = ExperienceFeedbackSystem()
    
    # Record feedback
    feedback_data = {
        'feedback_type': 'ui_experience',
        'session_id': 'test_session_001',
        'satisfaction': 4,
        'category': 'usability',
        'comments': 'Great experience!'
    }
    
    result = system.record_feedback(feedback_data)
    
    # Check that feedback was recorded
    assert result['status'] == 'success'
    assert len(system.feedback_store) == 1
    assert 'ui_experience' in system.feedback_analytics


def test_experience_feedback_system_get_analytics():
    """Test ExperienceFeedbackSystem get_feedback_analytics method."""
    system = ExperienceFeedbackSystem()
    
    # Record some feedback
    system.record_feedback({
        'feedback_type': 'workflow',
        'session_id': 'test_001',
        'satisfaction': 3,
        'category': 'speed'
    })
    
    system.record_feedback({
        'feedback_type': 'workflow',
        'session_id': 'test_002',
        'satisfaction': 5,
        'category': 'speed'
    })
    
    # Get analytics
    analytics = system.get_feedback_analytics('workflow')
    
    # Check analytics
    assert 'workflow' in analytics
    assert analytics['workflow']['count'] == 2
    assert analytics['workflow']['average_satisfaction'] == 4.0


def test_experience_feedback_system_get_suggestions():
    """Test ExperienceFeedbackSystem get_feedback_suggestions method."""
    system = ExperienceFeedbackSystem()
    
    # Record feedback with different satisfaction levels
    system.record_feedback({
        'feedback_type': 'ui',
        'session_id': 'test_001',
        'satisfaction': 2,
        'category': 'layout'
    })
    
    system.record_feedback({
        'feedback_type': 'workflow',
        'session_id': 'test_002',
        'satisfaction': 4,
        'category': 'speed'
    })
    
    # Get suggestions
    suggestions = system.get_feedback_suggestions()
    
    # Check suggestions
    assert len(suggestions) == 2
    assert suggestions[0]['priority'] == 'high'  # UI has low satisfaction
    assert suggestions[1]['priority'] == 'medium'  # Workflow has medium satisfaction


@patch('orchestrator.interfaces.personalized_experience.integrator.PersonalizedExperienceIntegrator')
def test_parallel_orchestrator_personalized_experience_integration(mock_integrator_class):
    """Test ParallelOrchestrator personalized experience integration."""
    from orchestrator.parallel.orchestrator import ParallelOrchestrator
    from orchestrator.agents.registry import AgentRegistry
    
    # Create mock integrator instance
    mock_integrator_instance = Mock()
    mock_integrator_class.return_value = mock_integrator_instance
    
    # Create orchestrator with personalized experience enabled
    orchestrator = ParallelOrchestrator(
        max_workers=2, 
        agent_registry=AgentRegistry(),
        enable_personalized_experience=True
    )
    
    # Should have personalized experience integrator
    assert orchestrator.personalized_experience_integrator == mock_integrator_instance
    
    # Test personalized experience methods
    orchestrator.create_personalized_experience()
    mock_integrator_instance.create_personalized_experience.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])