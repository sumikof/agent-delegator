"""
Personalized Experience Integrator Module

Integrates brainwave interface, predictive UI, and user preferences
to create a unified personalized experience system.
"""

from typing import Dict, Any, Optional, List
from orchestrator.parallel.orchestrator import ParallelOrchestrator

class PersonalizedExperienceIntegrator:
    """Main integrator for personalized agent experiences."""
    
    def __init__(self, orchestrator: ParallelOrchestrator):
        """
        Initialize personalized experience integrator.
        
        Args:
            orchestrator: Main orchestrator instance
        """
        self.orchestrator = orchestrator
        self.enabled = True
        self.user_profile = {
            'cognitive_style': 'balanced',
            'work_pattern': 'steady',
            'preferred_interaction': 'mixed',
            'adaptation_history': []
        }
    
    def create_personalized_experience(self) -> Dict[str, Any]:
        """
        Create a comprehensive personalized experience configuration.
        
        Returns:
            Dictionary containing personalized experience configuration
        """
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Personalized experience is disabled'}
        
        try:
            # Get components from orchestrator
            brainwave_data = self._get_brainwave_data()
            ui_config = self._get_ui_configuration()
            user_insights = self._get_user_insights()
            
            # Integrate all components
            personalized_config = self._integrate_components(
                brainwave_data, ui_config, user_insights
            )
            
            # Apply adaptation rules
            adapted_config = self._apply_adaptation_rules(personalized_config)
            
            return {
                'status': 'success',
                'personalized_experience': adapted_config,
                'components': {
                    'brainwave': brainwave_data,
                    'ui': ui_config,
                    'user_insights': user_insights
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to create personalized experience'
            }
    
    def _get_brainwave_data(self) -> Dict[str, Any]:
        """
        Get brainwave data from orchestrator.
        
        Returns:
            Dictionary containing brainwave data
        """
        if (hasattr(self.orchestrator, 'brainwave_adapter') and 
            self.orchestrator.brainwave_adapter is not None):
            
            # Get brainwave status
            brainwave_status = self.orchestrator.get_brainwave_status()
            
            if brainwave_status.get('enabled', False):
                # Generate mock EEG data for demonstration
                # In a real implementation, this would come from actual EEG processing
                return {
                    'cognitive_state': {
                        'focus_level': 0.75,
                        'stress_level': 0.3,
                        'cognitive_load': 0.5,
                        'engagement': 0.8,
                        'confidence': 0.9
                    },
                    'recommendations': {
                        'workflow_adjustments': ['auto_start_tasks', 'optimize_priority'],
                        'break_suggestions': ['none'],
                        'feedback_style': 'detailed'
                    },
                    'source': 'brainwave'
                }
        
        # Fallback to default cognitive state
        return {
            'cognitive_state': {
                'focus_level': 0.6,
                'stress_level': 0.4,
                'cognitive_load': 0.5,
                'engagement': 0.7,
                'confidence': 0.8
            },
            'recommendations': {
                'workflow_adjustments': ['normal_operation'],
                'break_suggestions': ['standard'],
                'feedback_style': 'balanced'
            },
            'source': 'default'
        }
    
    def _get_ui_configuration(self) -> Dict[str, Any]:
        """
        Get UI configuration from orchestrator.
        
        Returns:
            Dictionary containing UI configuration
        """
        if (hasattr(self.orchestrator, 'predictive_ui_adapter') and 
            self.orchestrator.predictive_ui_adapter is not None):
            
            # Get optimal UI configuration
            ui_result = self.orchestrator.get_optimal_ui_configuration()
            
            if ui_result.get('status') == 'success':
                return ui_result.get('ui_configuration', {})
        
        # Fallback to default UI configuration
        return {
            'color_scheme': 'default',
            'information_density': 'medium',
            'layout_compactness': 'default',
            'animation_speed': 'normal',
            'brightness': 'medium'
        }
    
    def _get_user_insights(self) -> Dict[str, Any]:
        """
        Get user insights from orchestrator.
        
        Returns:
            Dictionary containing user insights
        """
        if (hasattr(self.orchestrator, 'predictive_ui_adapter') and 
            self.orchestrator.predictive_ui_adapter is not None):
            
            # Get user insights
            insights_result = self.orchestrator.get_user_insights()
            
            if insights_result.get('status') == 'success':
                return insights_result.get('interaction_insights', {})
        
        # Fallback to default user insights
        return {
            'interaction_count': 0,
            'frequent_actions': [],
            'preference_trends': {},
            'feature_usage': {}
        }
    
    def _integrate_components(self, brainwave_data: Dict[str, Any], 
                             ui_config: Dict[str, Any], 
                             user_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate components into a unified personalized experience.
        
        Args:
            brainwave_data: Brainwave data
            ui_config: UI configuration
            user_insights: User insights
            
        Returns:
            Dictionary containing integrated personalized experience
        """
        cognitive_state = brainwave_data.get('cognitive_state', {})
        brainwave_recs = brainwave_data.get('recommendations', {})
        
        # Determine cognitive style based on brainwave data
        cognitive_style = self._determine_cognitive_style(cognitive_state)
        
        # Determine work pattern based on user insights
        work_pattern = self._determine_work_pattern(user_insights)
        
        # Create integrated experience configuration
        integrated_config = {
            'cognitive_profile': {
                'cognitive_style': cognitive_style,
                'focus_level': cognitive_state.get('focus_level', 0.6),
                'stress_level': cognitive_state.get('stress_level', 0.4),
                'work_pattern': work_pattern,
                'preferred_interaction': self._determine_preferred_interaction(cognitive_style, work_pattern)
            },
            'ui_settings': ui_config,
            'workflow_adaptations': brainwave_recs.get('workflow_adjustments', []),
            'feedback_strategy': brainwave_recs.get('feedback_style', 'balanced'),
            'break_strategy': brainwave_recs.get('break_suggestions', ['standard']),
            'personalization_level': self._determine_personalization_level(cognitive_style, user_insights)
        }
        
        return integrated_config
    
    def _determine_cognitive_style(self, cognitive_state: Dict[str, Any]) -> str:
        """Determine cognitive style based on cognitive state."""
        focus = cognitive_state.get('focus_level', 0.6)
        stress = cognitive_state.get('stress_level', 0.4)
        engagement = cognitive_state.get('engagement', 0.7)
        
        if focus > 0.8 and stress < 0.3:
            return 'analytical'
        elif focus > 0.7 and engagement > 0.8:
            return 'focused'
        elif stress > 0.6:
            return 'stressed'
        elif engagement < 0.5:
            return 'distracted'
        elif focus < 0.5 and stress < 0.4:
            return 'relaxed'
        else:
            return 'balanced'
    
    def _determine_work_pattern(self, user_insights: Dict[str, Any]) -> str:
        """Determine work pattern based on user insights."""
        interaction_count = user_insights.get('interaction_count', 0)
        frequent_actions = user_insights.get('frequent_actions', [])
        
        if interaction_count > 50:
            return 'intensive'
        elif interaction_count > 20:
            return 'active'
        elif len(frequent_actions) > 3:
            return 'varied'
        else:
            return 'steady'
    
    def _determine_preferred_interaction(self, cognitive_style: str, work_pattern: str) -> str:
        """Determine preferred interaction style."""
        if cognitive_style == 'analytical' and work_pattern == 'intensive':
            return 'detailed_control'
        elif cognitive_style == 'focused' and work_pattern in ['active', 'intensive']:
            return 'efficient_control'
        elif cognitive_style == 'stressed':
            return 'simplified_control'
        elif cognitive_style == 'distracted':
            return 'guided_control'
        elif cognitive_style == 'relaxed':
            return 'exploratory_control'
        else:
            return 'balanced_control'
    
    def _determine_personalization_level(self, cognitive_style: str, user_insights: Dict[str, Any]) -> str:
        """Determine personalization level."""
        interaction_count = user_insights.get('interaction_count', 0)
        
        if interaction_count > 100:
            return 'high'
        elif interaction_count > 50:
            return 'medium'
        elif cognitive_style in ['analytical', 'focused']:
            return 'medium'
        else:
            return 'basic'
    
    def _apply_adaptation_rules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adaptation rules to the personalized configuration."""
        adapted_config = config.copy()
        cognitive_profile = config.get('cognitive_profile', {})
        
        # Apply UI adaptations based on cognitive style
        ui_adaptations = self._get_ui_adaptations(cognitive_profile.get('cognitive_style', 'balanced'))
        adapted_config['ui_adaptations'] = ui_adaptations
        
        # Apply workflow adaptations based on work pattern
        workflow_adaptations = self._get_workflow_adaptations(
            cognitive_profile.get('work_pattern', 'steady'),
            cognitive_profile.get('cognitive_style', 'balanced')
        )
        adapted_config['workflow_adaptations'].extend(workflow_adaptations)
        
        # Apply interaction adaptations based on preferred interaction
        interaction_adaptations = self._get_interaction_adaptations(
            cognitive_profile.get('preferred_interaction', 'balanced_control')
        )
        adapted_config['interaction_adaptations'] = interaction_adaptations
        
        return adapted_config
    
    def _get_ui_adaptations(self, cognitive_style: str) -> Dict[str, Any]:
        """Get UI adaptations based on cognitive style."""
        adaptations = {
            'analytical': {
                'information_density': 'high',
                'color_scheme': 'neutral',
                'layout_compactness': 'compact',
                'animation_speed': 'normal',
                'data_visualization': 'detailed'
            },
            'focused': {
                'information_density': 'medium',
                'color_scheme': 'focused',
                'layout_compactness': 'compact',
                'animation_speed': 'minimal',
                'distraction_reduction': 'high'
            },
            'stressed': {
                'information_density': 'low',
                'color_scheme': 'calm',
                'layout_compactness': 'spacious',
                'animation_speed': 'slow',
                'stress_reduction': 'high'
            },
            'distracted': {
                'information_density': 'low',
                'color_scheme': 'vibrant',
                'layout_compactness': 'spacious',
                'animation_speed': 'normal',
                'attention_guidance': 'high'
            },
            'relaxed': {
                'information_density': 'medium',
                'color_scheme': 'warm',
                'layout_compactness': 'spacious',
                'animation_speed': 'normal',
                'exploration_encouragement': 'high'
            },
            'balanced': {
                'information_density': 'medium',
                'color_scheme': 'default',
                'layout_compactness': 'default',
                'animation_speed': 'normal',
                'adaptation_balance': 'neutral'
            }
        }
        
        return adaptations.get(cognitive_style, adaptations['balanced'])
    
    def _get_workflow_adaptations(self, work_pattern: str, cognitive_style: str) -> List[str]:
        """Get workflow adaptations based on work pattern and cognitive style."""
        adaptations = []
        
        if work_pattern == 'intensive' and cognitive_style in ['analytical', 'focused']:
            adaptations.extend(['auto_prioritize_tasks', 'batch_processing', 'optimize_resource_allocation'])
        elif work_pattern == 'active':
            adaptations.extend(['balanced_task_distribution', 'adaptive_prioritization'])
        elif work_pattern == 'varied':
            adaptations.extend(['flexible_workflow', 'adaptive_scheduling'])
        else:  # steady
            adaptations.extend(['standard_workflow', 'normal_prioritization'])
        
        # Cognitive style specific adaptations
        if cognitive_style == 'stressed':
            adaptations.append('stress_aware_scheduling')
        elif cognitive_style == 'distracted':
            adaptations.append('focus_assistance')
        elif cognitive_style == 'relaxed':
            adaptations.append('exploratory_mode')
        
        return adaptations
    
    def _get_interaction_adaptations(self, preferred_interaction: str) -> Dict[str, Any]:
        """Get interaction adaptations based on preferred interaction style."""
        adaptations = {
            'detailed_control': {
                'interaction_style': 'expert',
                'feedback_detail': 'high',
                'control_granularity': 'fine',
                'shortcut_availability': 'full'
            },
            'efficient_control': {
                'interaction_style': 'efficient',
                'feedback_detail': 'medium',
                'control_granularity': 'medium',
                'shortcut_availability': 'common'
            },
            'simplified_control': {
                'interaction_style': 'simplified',
                'feedback_detail': 'low',
                'control_granularity': 'coarse',
                'shortcut_availability': 'basic'
            },
            'guided_control': {
                'interaction_style': 'guided',
                'feedback_detail': 'high',
                'control_granularity': 'coarse',
                'assistance_level': 'high'
            },
            'exploratory_control': {
                'interaction_style': 'exploratory',
                'feedback_detail': 'medium',
                'control_granularity': 'fine',
                'discovery_features': 'enabled'
            },
            'balanced_control': {
                'interaction_style': 'balanced',
                'feedback_detail': 'medium',
                'control_granularity': 'medium',
                'adaptation_level': 'moderate'
            }
        }
        
        return adaptations.get(preferred_interaction, adaptations['balanced_control'])
    
    def update_user_profile(self, profile_updates: Dict[str, Any]):
        """
        Update user profile with new information.
        
        Args:
            profile_updates: Dictionary of profile updates
        """
        self.user_profile.update(profile_updates)
        
        # Record adaptation event
        adaptation_event = {
            'timestamp': datetime.now().isoformat(),
            'updates': list(profile_updates.keys()),
            'source': 'explicit_update'
        }
        
        self.user_profile['adaptation_history'].append(adaptation_event)
        
        # Keep history size manageable
        if len(self.user_profile['adaptation_history']) > 50:
            self.user_profile['adaptation_history'] = self.user_profile['adaptation_history'][-50:]
        
        return {'status': 'success', 'message': 'User profile updated'}
    
    def get_personalization_status(self) -> Dict[str, Any]:
        """
        Get current personalization status.
        
        Returns:
            Dictionary containing personalization status
        """
        return {
            'enabled': self.enabled,
            'user_profile': self.user_profile.copy(),
            'adaptation_count': len(self.user_profile.get('adaptation_history', [])),
            'cognitive_style': self.user_profile.get('cognitive_style', 'unknown'),
            'work_pattern': self.user_profile.get('work_pattern', 'unknown')
        }
    
    def enable(self):
        """Enable personalized experience system."""
        self.enabled = True
    
    def disable(self):
        """Disable personalized experience system."""
        self.enabled = False