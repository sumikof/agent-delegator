"""
Action Mapper Module

Maps cognitive states to specific agent actions with configurable thresholds.
"""

from typing import Dict, Any, Optional, Callable
import numpy as np

class ActionMapper:
    """Maps cognitive states to agent actions."""
    
    def __init__(self):
        # Define action thresholds and mappings
        self.thresholds = {
            'focus_high': 0.8,
            'focus_low': 0.3,
            'stress_high': 0.7,
            'cognitive_load_high': 0.6,
            'engagement_high': 0.7,
            'confidence_high': 0.9,
            'confidence_low': 0.6
        }
        
        self.action_mappings = {
            'start_task': self._should_start_task,
            'pause_task': self._should_pause_task,
            'adjust_priority': self._should_adjust_priority,
            'suggest_break': self._should_suggest_break,
            'auto_approve': self._should_auto_approve,
            'request_review': self._should_request_review,
            'adjust_feedback': self._should_adjust_feedback
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
            return {'auto_start': True, 'reason': 'high_focus_and_engagement'}
        return None
    
    def _should_pause_task(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current task should be paused."""
        if (state.get('focus_level', 1) < self.thresholds['focus_low'] or
            state.get('stress_level', 0) > self.thresholds['stress_high']):
            return {
                'pause_reason': 'low_focus_or_high_stress',
                'focus_level': state.get('focus_level'),
                'stress_level': state.get('stress_level')
            }
        return None
    
    def _should_adjust_priority(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if task priorities should be adjusted."""
        cognitive_load = state.get('cognitive_load', 0)
        if cognitive_load > self.thresholds['cognitive_load_high']:
            return {
                'adjustment': 'reduce_load',
                'current_load': cognitive_load,
                'target_load': self.thresholds['cognitive_load_high'] * 0.8,
                'reduction_factor': 0.2
            }
        return None
    
    def _should_suggest_break(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if a break should be suggested."""
        if (state.get('stress_level', 0) > self.thresholds['stress_high'] * 1.2 and
            state.get('focus_level', 1) < self.thresholds['focus_low'] * 1.2):
            return {
                'break_type': 'stress_reduction',
                'duration_minutes': 10,
                'severity': 'high',
                'stress_level': state.get('stress_level'),
                'focus_level': state.get('focus_level')
            }
        return None
    
    def _should_auto_approve(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current work should be auto-approved."""
        if (state.get('focus_level', 0) > self.thresholds['focus_high'] * 1.1 and
            state.get('confidence', 0) > self.thresholds['confidence_high']):
            return {
                'auto_approve': True,
                'confidence': state['confidence'],
                'reason': 'high_focus_and_high_confidence'
            }
        return None
    
    def _should_request_review(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if human review should be requested."""
        if (state.get('cognitive_load', 0) > self.thresholds['cognitive_load_high'] * 1.3 or
            state.get('confidence', 1) < self.thresholds['confidence_low']):
            return {
                'review_type': 'human',
                'priority': 'high',
                'cognitive_load': state.get('cognitive_load'),
                'confidence': state.get('confidence')
            }
        return None
    
    def _should_adjust_feedback(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if feedback delivery should be adjusted."""
        stress_level = state.get('stress_level', 0)
        focus_level = state.get('focus_level', 0)
        
        if stress_level > self.thresholds['stress_high']:
            return {
                'feedback_adjustment': 'gentler',
                'stress_level': stress_level,
                'suggested_tone': 'positive_encouraging'
            }
        elif focus_level > self.thresholds['focus_high'] * 1.2:
            return {
                'feedback_adjustment': 'more_technical',
                'focus_level': focus_level,
                'suggested_tone': 'detailed_analytical'
            }
        
        return None
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """
        Update action thresholds.
        
        Args:
            new_thresholds: Dictionary of new threshold values
        """
        self.thresholds.update(new_thresholds)
    
    def add_custom_action(self, action_type: str, condition_func: Callable):
        """
        Add custom action mapping.
        
        Args:
            action_type: Name of the new action type
            condition_func: Function that takes cognitive state and returns action params or None
        """
        self.action_mappings[action_type] = condition_func
    
    def get_current_thresholds(self) -> Dict[str, float]:
        """Get current threshold values."""
        return self.thresholds.copy()
    
    def get_available_actions(self) -> list:
        """Get list of available action types."""
        return list(self.action_mappings.keys())