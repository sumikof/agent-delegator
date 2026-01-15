"""
Adaptation Engine Module

Provides dynamic adaptation capabilities for personalized experiences
based on real-time feedback and performance monitoring.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import time

class AdaptationEngine:
    """Engine for dynamic adaptation of personalized experiences."""
    
    def __init__(self):
        self.adaptation_rules = {
            'performance': self._apply_performance_adaptations,
            'feedback': self._apply_feedback_adaptations,
            'context': self._apply_context_adaptations,
            'learning': self._apply_learning_adaptations
        }
        self.adaptation_history = []
        self.performance_metrics = {}
        self.learning_rate = 0.1
    
    def adapt_experience(self, current_config: Dict[str, Any], 
                        feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt personalized experience based on feedback.
        
        Args:
            current_config: Current personalized experience configuration
            feedback_data: Feedback data for adaptation
            
        Returns:
            Dictionary containing adapted configuration
        """
        # Record adaptation event
        adaptation_event = {
            'timestamp': datetime.now().isoformat(),
            'original_config': current_config.copy(),
            'feedback_data': feedback_data.copy(),
            'adaptations_applied': []
        }
        
        # Apply different types of adaptations
        adapted_config = current_config.copy()
        
        # Performance-based adaptations
        if 'performance_metrics' in feedback_data:
            perf_adaptations = self.adaptation_rules['performance'](
                adapted_config, feedback_data['performance_metrics']
            )
            adaptation_event['adaptations_applied'].extend(perf_adaptations)
        
        # Feedback-based adaptations
        if 'user_feedback' in feedback_data:
            fb_adaptations = self.adaptation_rules['feedback'](
                adapted_config, feedback_data['user_feedback']
            )
            adaptation_event['adaptations_applied'].extend(fb_adaptations)
        
        # Context-based adaptations
        if 'context_changes' in feedback_data:
            ctx_adaptations = self.adaptation_rules['context'](
                adapted_config, feedback_data['context_changes']
            )
            adaptation_event['adaptations_applied'].extend(ctx_adaptations)
        
        # Learning-based adaptations
        learning_adaptations = self.adaptation_rules['learning'](adapted_config)
        adaptation_event['adaptations_applied'].extend(learning_adaptations)
        
        # Record adaptation event
        self.adaptation_history.append(adaptation_event)
        
        # Keep history size manageable
        if len(self.adaptation_history) > 100:
            self.adaptation_history = self.adaptation_history[-100:]
        
        return adapted_config
    
    def _apply_performance_adaptations(self, config: Dict[str, Any], 
                                     metrics: Dict[str, Any]) -> List[str]:
        """Apply performance-based adaptations."""
        adaptations = []
        
        # Update performance metrics
        self.performance_metrics.update(metrics)
        
        # Task completion rate adaptations
        completion_rate = metrics.get('task_completion_rate', 0.8)
        if completion_rate > 0.9:
            adaptations.append('increase_task_complexity')
            config['workflow_adaptations'].append('challenge_mode')
        elif completion_rate < 0.7:
            adaptations.append('reduce_task_complexity')
            config['workflow_adaptations'].append('assisted_mode')
        
        # Response time adaptations
        response_time = metrics.get('average_response_time', 2.0)
        if response_time > 3.0:
            adaptations.append('simplify_ui')
            if 'ui_adaptations' in config:
                config['ui_adaptations']['information_density'] = 'low'
        elif response_time < 1.0:
            adaptations.append('enrich_ui')
            if 'ui_adaptations' in config:
                config['ui_adaptations']['information_density'] = 'high'
        
        # Error rate adaptations
        error_rate = metrics.get('error_rate', 0.1)
        if error_rate > 0.2:
            adaptations.append('add_safety_checks')
            config['interaction_adaptations']['assistance_level'] = 'high'
        elif error_rate < 0.05:
            adaptations.append('reduce_safety_checks')
            config['interaction_adaptations']['assistance_level'] = 'low'
        
        return adaptations
    
    def _apply_feedback_adaptations(self, config: Dict[str, Any], 
                                   feedback: Dict[str, Any]) -> List[str]:
        """Apply user feedback-based adaptations."""
        adaptations = []
        
        # Satisfaction adaptations
        satisfaction = feedback.get('satisfaction', 3)
        if satisfaction >= 4:
            adaptations.append('maintain_current_approach')
        elif satisfaction <= 2:
            adaptations.append('adjust_approach')
            # Try a different cognitive style
            current_style = config.get('cognitive_profile', {}).get('cognitive_style', 'balanced')
            if current_style == 'analytical':
                config['cognitive_profile']['cognitive_style'] = 'focused'
            else:
                config['cognitive_profile']['cognitive_style'] = 'balanced'
        
        # Preference adaptations
        preferences = feedback.get('preferences', {})
        if 'ui_theme' in preferences:
            adaptations.append('update_ui_theme')
            if 'ui_settings' in config:
                config['ui_settings']['color_scheme'] = preferences['ui_theme']
        
        if 'workflow_speed' in preferences:
            adaptations.append('adjust_workflow_speed')
            speed_pref = preferences['workflow_speed']
            if speed_pref == 'faster':
                config['workflow_adaptations'].append('accelerate_workflow')
            elif speed_pref == 'slower':
                config['workflow_adaptations'].append('decelerate_workflow')
        
        return adaptations
    
    def _apply_context_adaptations(self, config: Dict[str, Any], 
                                  context: Dict[str, Any]) -> List[str]:
        """Apply context-based adaptations."""
        adaptations = []
        
        # Time-based adaptations
        time_of_day = context.get('time_of_day', 'day')
        if time_of_day in ['evening', 'night']:
            adaptations.append('night_mode')
            if 'ui_adaptations' in config:
                config['ui_adaptations']['color_scheme'] = 'dark'
                config['ui_adaptations']['brightness'] = 'low'
        else:
            adaptations.append('day_mode')
            if 'ui_adaptations' in config:
                config['ui_adaptations']['color_scheme'] = 'light'
                config['ui_adaptations']['brightness'] = 'medium'
        
        # Workload adaptations
        workload = context.get('workload', 'medium')
        if workload == 'high':
            adaptations.append('high_workload_mode')
            config['workflow_adaptations'].append('prioritize_critical_tasks')
        elif workload == 'low':
            adaptations.append('low_workload_mode')
            config['workflow_adaptations'].append('allow_exploration')
        
        # Environment adaptations
        environment = context.get('environment', 'office')
        if environment == 'mobile':
            adaptations.append('mobile_optimization')
            if 'ui_adaptations' in config:
                config['ui_adaptations']['layout_compactness'] = 'compact'
                config['ui_adaptations']['information_density'] = 'medium'
        
        return adaptations
    
    def _apply_learning_adaptations(self, config: Dict[str, Any]) -> List[str]:
        """Apply learning-based adaptations from adaptation history."""
        adaptations = []
        
        if not self.adaptation_history:
            return adaptations
        
        # Analyze recent adaptations
        recent_adaptations = self.adaptation_history[-10:]
        
        # Count adaptation types
        adaptation_counts = {}
        for event in recent_adaptations:
            for adaptation in event['adaptations_applied']:
                adaptation_counts[adaptation] = adaptation_counts.get(adaptation, 0) + 1
        
        # Apply learning based on frequent adaptations
        if adaptation_counts.get('simplify_ui', 0) > 3:
            adaptations.append('persistent_simplification')
            config['cognitive_profile']['cognitive_style'] = 'simplified'
        
        if adaptation_counts.get('increase_task_complexity', 0) > 2:
            adaptations.append('persistent_challenge')
            config['personalization_level'] = 'high'
        
        # Gradual learning adaptations
        if len(self.adaptation_history) % 5 == 0:  # Every 5 adaptations
            adaptations.append('gradual_optimization')
            # Fine-tune based on most successful adaptations
            successful_adaptations = [
                adapt for adapt, count in adaptation_counts.items() 
                if count >= 2 and adapt not in ['maintain_current_approach', 'adjust_approach']
            ]
            
            if successful_adaptations:
                # Apply the most successful adaptation pattern
                most_successful = max(successful_adaptations, key=lambda x: adaptation_counts[x])
                config['adaptation_strategy'] = f'favor_{most_successful}'
        
        return adaptations
    
    def get_adaptation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent adaptation history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of adaptation events
        """
        return self.adaptation_history[-limit:]
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """
        Get adaptation statistics.
        
        Returns:
            Dictionary containing adaptation statistics
        """
        if not self.adaptation_history:
            return {'total_adaptations': 0, 'adaptation_types': {}}
        
        # Count adaptation types
        adaptation_types = {}
        for event in self.adaptation_history:
            for adaptation in event['adaptations_applied']:
                adaptation_types[adaptation] = adaptation_types.get(adaptation, 0) + 1
        
        return {
            'total_adaptations': len(self.adaptation_history),
            'adaptation_types': adaptation_types,
            'most_common_adaptations': sorted(adaptation_types.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
        }
    
    def reset_adaptation_history(self):
        """Reset adaptation history."""
        self.adaptation_history = []
        self.performance_metrics = {}
    
    def set_learning_rate(self, rate: float):
        """
        Set learning rate for adaptations.
        
        Args:
            rate: Learning rate (0.0 to 1.0)
        """
        self.learning_rate = max(0.0, min(1.0, rate))