"""
Brainwave Agent Adapter Module

Integrates brainwave interface with the AI agent orchestration system.
"""

from typing import Dict, Any, Optional
import numpy as np
from orchestrator.main import Orchestrator
from .processor import BrainwaveProcessor

class ActionMapper:
    """Maps cognitive states to agent actions."""
    
    def __init__(self):
        # Define action thresholds and mappings
        self.thresholds = {
            'focus_high': 0.8,
            'focus_low': 0.3,
            'stress_high': 0.7,
            'cognitive_load_high': 0.6,
            'engagement_high': 0.7
        }
        
        self.action_mappings = {
            'start_task': self._should_start_task,
            'pause_task': self._should_pause_task,
            'adjust_priority': self._should_adjust_priority,
            'suggest_break': self._should_suggest_break,
            'auto_approve': self._should_auto_approve,
            'request_review': self._should_request_review
        }
    
    def map_state_to_action(self, cognitive_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Map cognitive state to appropriate agent action.
        
        Args:
            cognitive_state: Cognitive state from brainwave processor
            
        Returns:
            Action dictionary or None if no action should be taken
        """
        for action_type, condition_func in self.action_mappings.items():
            action = condition_func(cognitive_state)
            if action:
                return {'type': action_type, 'params': action}
        
        return None
    
    def _should_start_task(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if task should be started automatically."""
        if (state.get('focus_level', 0) > self.thresholds['focus_high'] and
            state.get('engagement', 0) > self.thresholds['engagement_high']):
            return {'auto_start': True}
        return None
    
    def _should_pause_task(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current task should be paused."""
        if (state.get('focus_level', 1) < self.thresholds['focus_low'] or
            state.get('stress_level', 0) > self.thresholds['stress_high']):
            return {'pause_reason': 'low_focus_or_high_stress'}
        return None
    
    def _should_adjust_priority(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if task priorities should be adjusted."""
        cognitive_load = state.get('cognitive_load', 0)
        if cognitive_load > self.thresholds['cognitive_load_high']:
            return {
                'adjustment': 'reduce_load',
                'target_load': self.thresholds['cognitive_load_high'] * 0.8
            }
        return None
    
    def _should_suggest_break(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if a break should be suggested."""
        if (state.get('stress_level', 0) > self.thresholds['stress_high'] * 1.2 and
            state.get('focus_level', 1) < self.thresholds['focus_low'] * 1.2):
            return {
                'break_type': 'stress_reduction',
                'duration_minutes': 10
            }
        return None
    
    def _should_auto_approve(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current work should be auto-approved."""
        if (state.get('focus_level', 0) > self.thresholds['focus_high'] * 1.1 and
            state.get('confidence', 0) > 0.9):
            return {'auto_approve': True, 'confidence': state['confidence']}
        return None
    
    def _should_request_review(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if human review should be requested."""
        if (state.get('cognitive_load', 0) > self.thresholds['cognitive_load_high'] * 1.3 or
            state.get('confidence', 1) < 0.6):
            return {
                'review_type': 'human',
                'priority': 'high'
            }
        return None

class BrainwaveAgentAdapter:
    """Main adapter class for integrating brainwave interface with agent orchestration."""
    
    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize brainwave agent adapter.
        
        Args:
            orchestrator: Main orchestrator instance
        """
        self.orchestrator = orchestrator
        self.brainwave_processor = BrainwaveProcessor()
        self.action_mapper = ActionMapper()
        self.enabled = True
    
    def handle_brainwave_input(self, eeg_data: np.ndarray) -> Dict[str, Any]:
        """
        Process EEG data and trigger appropriate agent actions.
        
        Args:
            eeg_data: Raw EEG data from device
            
        Returns:
            Dictionary containing processing results and actions taken
        """
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Brainwave interface is disabled'}
        
        result = {
            'eeg_processing': None,
            'action_taken': None,
            'orchestrator_response': None
        }
        
        try:
            # Process brainwave data
            cognitive_state = self.brainwave_processor.process(eeg_data)
            result['eeg_processing'] = cognitive_state
            
            # Map to action
            action = self.action_mapper.map_state_to_action(cognitive_state)
            result['action_taken'] = action
            
            # Execute action in orchestrator
            if action:
                orchestrator_response = self._execute_orchestrator_action(action)
                result['orchestrator_response'] = orchestrator_response
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to process brainwave input'
            }
    
    def _execute_orchestrator_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action in the orchestrator.
        
        Args:
            action: Action dictionary from action mapper
            
        Returns:
            Orchestrator response
        """
        action_type = action['type']
        params = action.get('params', {})
        
        # Route to appropriate orchestrator method
        if action_type == 'start_task':
            return self.orchestrator.start_next_task(**params)
            
        elif action_type == 'pause_task':
            return self.orchestrator.pause_current_task(**params)
            
        elif action_type == 'adjust_priority':
            return self.orchestrator.adjust_task_priorities(**params)
            
        elif action_type == 'suggest_break':
            return self.orchestrator.suggest_user_break(**params)
            
        elif action_type == 'auto_approve':
            return self.orchestrator.auto_approve_current_work(**params)
            
        elif action_type == 'request_review':
            return self.orchestrator.request_human_review(**params)
            
        else:
            return {'status': 'error', 'message': f'Unknown action type: {action_type}'}
    
    def enable(self):
        """Enable brainwave interface."""
        self.enabled = True
    
    def disable(self):
        """Disable brainwave interface."""
        self.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of brainwave interface."""
        return {
            'enabled': self.enabled,
            'processor_status': 'ready',  # Could be more detailed
            'action_mapper_status': 'ready'
        }