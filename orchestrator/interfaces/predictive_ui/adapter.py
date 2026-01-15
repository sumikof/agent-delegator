"""
Predictive UI Adapter Module

Integrates predictive UI capabilities with the AI agent orchestration system.
"""

from typing import Dict, Any, Optional
from orchestrator.parallel.orchestrator import ParallelOrchestrator
from .predictor import UIPredictor
from .personalization import UserProfileManager

class PredictiveUIAdapter:
    """Main adapter class for integrating predictive UI with agent orchestration."""
    
    def __init__(self, orchestrator: ParallelOrchestrator):
        """
        Initialize predictive UI adapter.
        
        Args:
            orchestrator: Main orchestrator instance
        """
        self.orchestrator = orchestrator
        self.ui_predictor = UIPredictor()
        self.profile_manager = UserProfileManager()
        self.enabled = True
        self.current_ui_state = {}
    
    def get_optimal_ui_configuration(self) -> Dict[str, Any]:
        """
        Get optimal UI configuration based on current context.
        
        Returns:
            Dictionary containing optimal UI configuration
        """
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Predictive UI is disabled'}
        
        try:
            # Get current cognitive state (if brainwave interface is available)
            cognitive_state = self._get_cognitive_state()
            
            # Get current workflow context
            workflow_context = self._get_workflow_context()
            
            # Get user preferences
            user_preferences = self.profile_manager.get_user_preferences()
            
            # Predict optimal UI
            ui_config = self.ui_predictor.predict_optimal_ui(
                cognitive_state, workflow_context, user_preferences
            )
            
            # Store current UI state
            self.current_ui_state = ui_config
            
            return {
                'status': 'success',
                'ui_configuration': ui_config,
                'cognitive_state': cognitive_state,
                'workflow_context': workflow_context
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to determine optimal UI configuration'
            }
    
    def _get_cognitive_state(self) -> Dict[str, Any]:
        """
        Get current cognitive state from brainwave interface.
        
        Returns:
            Dictionary containing cognitive state information
        """
        # Check if brainwave interface is available
        if (hasattr(self.orchestrator, 'brainwave_adapter') and 
            self.orchestrator.brainwave_adapter is not None):
            
            # Get brainwave status
            brainwave_status = self.orchestrator.get_brainwave_status()
            
            if brainwave_status.get('enabled', False):
                # Use the most recent cognitive state from brainwave processing
                # In a real implementation, this would come from actual EEG data
                return {
                    'focus_level': 0.75,  # Default values
                    'stress_level': 0.3,
                    'cognitive_load': 0.5,
                    'engagement': 0.8,
                    'source': 'brainwave'
                }
        
        # Fallback to default cognitive state
        return {
            'focus_level': 0.6,
            'stress_level': 0.4,
            'cognitive_load': 0.5,
            'engagement': 0.7,
            'source': 'default'
        }
    
    def _get_workflow_context(self) -> Dict[str, Any]:
        """
        Get current workflow context from orchestrator.
        
        Returns:
            Dictionary containing workflow context information
        """
        # Get task information
        all_tasks = self.orchestrator.task_queue.get_all_tasks()
        
        pending_tasks = [t for t in all_tasks if t.status.name == 'PENDING']
        running_tasks = [t for t in all_tasks if t.status.name == 'RUNNING']
        completed_tasks = [t for t in all_tasks if t.status.name == 'COMPLETED']
        
        # Determine current stage (simplified)
        current_stage = 'execution'
        if len(completed_tasks) == len(all_tasks):
            current_stage = 'completed'
        elif len(pending_tasks) == len(all_tasks):
            current_stage = 'initial'
        
        return {
            'total_tasks': len(all_tasks),
            'pending_tasks': [t.task_id for t in pending_tasks],
            'running_tasks': [t.task_id for t in running_tasks],
            'completed_tasks': [t.task_id for t in completed_tasks],
            'current_stage': current_stage,
            'task_load': len(pending_tasks) + len(running_tasks)
        }
    
    def record_user_interaction(self, interaction_data: Dict[str, Any]):
        """
        Record user interaction for pattern analysis.
        
        Args:
            interaction_data: Dictionary containing interaction details
        """
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Predictive UI is disabled'}
        
        try:
            # Record interaction with UI predictor
            self.ui_predictor.record_interaction(interaction_data)
            
            # Update user profile
            self.profile_manager.update_user_profile(interaction_data)
            
            return {'status': 'success', 'message': 'Interaction recorded'}
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to record interaction'
            }
    
    def get_user_insights(self) -> Dict[str, Any]:
        """
        Get insights about user patterns and preferences.
        
        Returns:
            Dictionary of user insights
        """
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Predictive UI is disabled'}
        
        try:
            # Get insights from UI predictor
            predictor_insights = self.ui_predictor.get_insights()
            
            # Get user profile information
            user_profile = self.profile_manager.get_user_profile()
            
            return {
                'status': 'success',
                'interaction_insights': predictor_insights,
                'user_profile': user_profile
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to get user insights'
            }
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """
        Update user preferences.
        
        Args:
            preferences: Dictionary of user preferences
        """
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Predictive UI is disabled'}
        
        try:
            # Update preferences in profile manager
            self.profile_manager.update_preferences(preferences)
            
            return {'status': 'success', 'message': 'Preferences updated'}
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to update preferences'
            }
    
    def enable(self):
        """Enable predictive UI interface."""
        self.enabled = True
    
    def disable(self):
        """Disable predictive UI interface."""
        self.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of predictive UI interface."""
        return {
            'enabled': self.enabled,
            'ui_predictor_status': 'ready',
            'profile_manager_status': 'ready',
            'current_ui_state': self.current_ui_state,
            'interaction_count': len(self.ui_predictor.pattern_analyzer.interaction_history)
        }