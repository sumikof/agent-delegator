"""
UI Predictor Module

Predicts user interface needs and optimal interactions based on
cognitive state, historical patterns, and contextual analysis.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

class InteractionPatternAnalyzer:
    """Analyzes user interaction patterns and historical data."""
    
    def __init__(self):
        self.interaction_history = []
        self.pattern_cache = {}
        self.learning_rate = 0.1
    
    def record_interaction(self, interaction_data: Dict[str, Any]):
        """
        Record a user interaction for pattern analysis.
        
        Args:
            interaction_data: Dictionary containing interaction details
        """
        self.interaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'data': interaction_data
        })
        
        # Keep history size manageable
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-1000:]
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze interaction patterns and identify trends.
        
        Returns:
            Dictionary of identified patterns and trends
        """
        if not self.interaction_history:
            return {'patterns': [], 'trends': {}}
        
        patterns = {
            'frequent_actions': self._find_frequent_actions(),
            'time_patterns': self._find_time_patterns(),
            'sequence_patterns': self._find_sequence_patterns(),
            'preference_trends': self._find_preference_trends()
        }
        
        return patterns
    
    def _find_frequent_actions(self) -> List[Dict[str, Any]]:
        """Find most frequent user actions."""
        action_counts = defaultdict(int)
        
        for interaction in self.interaction_history:
            action_type = interaction['data'].get('action_type')
            if action_type:
                action_counts[action_type] += 1
        
        # Sort by frequency
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{'action': action, 'count': count} for action, count in sorted_actions[:5]]
    
    def _find_time_patterns(self) -> Dict[str, Any]:
        """Find time-based interaction patterns."""
        time_patterns = {
            'peak_hours': [],
            'weekday_trends': {}
        }
        
        # Simple implementation - analyze time patterns
        return time_patterns
    
    def _find_sequence_patterns(self) -> List[List[str]]:
        """Find common action sequences."""
        sequences = []
        
        # Simple implementation - find common sequences
        if len(self.interaction_history) >= 2:
            for i in range(len(self.interaction_history) - 1):
                current_action = self.interaction_history[i]['data'].get('action_type')
                next_action = self.interaction_history[i+1]['data'].get('action_type')
                
                if current_action and next_action:
                    sequences.append([current_action, next_action])
        
        return sequences[:3]  # Return top 3 sequences
    
    def _find_preference_trends(self) -> Dict[str, Any]:
        """Find user preference trends over time."""
        preferences = {
            'ui_themes': self._analyze_theme_preferences(),
            'layout_preferences': self._analyze_layout_preferences(),
            'feature_usage': self._analyze_feature_usage()
        }
        
        return preferences
    
    def _analyze_theme_preferences(self) -> Dict[str, Any]:
        """Analyze UI theme preferences."""
        theme_counts = defaultdict(int)
        
        for interaction in self.interaction_history:
            theme = interaction['data'].get('ui_theme')
            if theme:
                theme_counts[theme] += 1
        
        if theme_counts:
            most_common = max(theme_counts.items(), key=lambda x: x[1])
            return {
                'preferred_theme': most_common[0],
                'usage_percentage': most_common[1] / len(self.interaction_history)
            }
        
        return {'preferred_theme': 'default', 'usage_percentage': 1.0}
    
    def _analyze_layout_preferences(self) -> Dict[str, Any]:
        """Analyze layout preferences."""
        layout_counts = defaultdict(int)
        
        for interaction in self.interaction_history:
            layout = interaction['data'].get('layout_type')
            if layout:
                layout_counts[layout] += 1
        
        if layout_counts:
            most_common = max(layout_counts.items(), key=lambda x: x[1])
            return {
                'preferred_layout': most_common[0],
                'usage_percentage': most_common[1] / len(self.interaction_history)
            }
        
        return {'preferred_layout': 'default', 'usage_percentage': 1.0}
    
    def _analyze_feature_usage(self) -> Dict[str, Any]:
        """Analyze feature usage patterns."""
        feature_counts = defaultdict(int)
        
        for interaction in self.interaction_history:
            features = interaction['data'].get('features_used', [])
            for feature in features:
                feature_counts[feature] += 1
        
        # Sort by usage
        sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_used_features': [f[0] for f in sorted_features[:3]],
            'feature_usage_distribution': dict(sorted_features)
        }

class ContextAnalyzer:
    """Analyzes current context to predict UI needs."""
    
    def __init__(self):
        self.context_rules = {
            'high_stress': {
                'ui_adjustments': {
                    'color_scheme': 'calm',
                    'animation_speed': 'slow',
                    'information_density': 'low'
                }
            },
            'high_focus': {
                'ui_adjustments': {
                    'color_scheme': 'neutral',
                    'animation_speed': 'normal',
                    'information_density': 'high'
                }
            },
            'low_engagement': {
                'ui_adjustments': {
                    'color_scheme': 'vibrant',
                    'animation_speed': 'fast',
                    'information_density': 'medium'
                }
            }
        }
    
    def analyze_context(self, cognitive_state: Dict[str, Any], 
                       workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current context and predict optimal UI settings.
        
        Args:
            cognitive_state: Current cognitive state from brainwave interface
            workflow_context: Current workflow context
            
        Returns:
            Dictionary of recommended UI adjustments
        """
        context_analysis = {
            'cognitive_context': self._analyze_cognitive_context(cognitive_state),
            'workflow_context': self._analyze_workflow_context(workflow_context),
            'time_context': self._analyze_time_context()
        }
        
        # Generate UI recommendations
        recommendations = self._generate_ui_recommendations(context_analysis)
        
        return recommendations
    
    def _analyze_cognitive_context(self, cognitive_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cognitive context."""
        focus_level = cognitive_state.get('focus_level', 0.5)
        stress_level = cognitive_state.get('stress_level', 0.3)
        engagement = cognitive_state.get('engagement', 0.6)
        
        cognitive_context = {
            'focus_level': focus_level,
            'stress_level': stress_level,
            'engagement': engagement,
            'cognitive_state': self._classify_cognitive_state(focus_level, stress_level, engagement)
        }
        
        return cognitive_context
    
    def _classify_cognitive_state(self, focus: float, stress: float, engagement: float) -> str:
        """Classify cognitive state into categories."""
        if stress > 0.7:
            return 'high_stress'
        elif focus > 0.8 and engagement > 0.8:
            return 'high_focus'
        elif focus < 0.4 and engagement < 0.5:
            return 'low_engagement'
        elif focus > 0.6 and stress < 0.4:
            return 'optimal_productivity'
        else:
            return 'normal'
    
    def _analyze_workflow_context(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow context."""
        task_count = len(workflow_context.get('pending_tasks', []))
        current_stage = workflow_context.get('current_stage', 'unknown')
        
        workflow_context = {
            'task_load': self._classify_task_load(task_count),
            'stage_type': current_stage,
            'urgency': self._determine_urgency(task_count, current_stage)
        }
        
        return workflow_context
    
    def _classify_task_load(self, task_count: int) -> str:
        """Classify task load."""
        if task_count > 10:
            return 'high'
        elif task_count > 5:
            return 'medium'
        else:
            return 'low'
    
    def _determine_urgency(self, task_count: int, stage: str) -> str:
        """Determine workflow urgency."""
        urgent_stages = ['review', 'approval', 'deployment']
        
        if stage in urgent_stages or task_count > 8:
            return 'high'
        elif task_count > 4:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_time_context(self) -> Dict[str, Any]:
        """Analyze time-based context."""
        now = datetime.now()
        hour = now.hour
        
        time_context = {
            'time_of_day': self._classify_time_of_day(hour),
            'day_of_week': now.strftime('%A'),
            'is_work_hours': 9 <= hour < 17
        }
        
        return time_context
    
    def _classify_time_of_day(self, hour: int) -> str:
        """Classify time of day."""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _generate_ui_recommendations(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI recommendations based on context analysis."""
        cognitive_state = context_analysis['cognitive_context']['cognitive_state']
        task_load = context_analysis['workflow_context']['task_load']
        time_of_day = context_analysis['time_context']['time_of_day']
        
        # Base recommendations on cognitive state
        recommendations = self.context_rules.get(cognitive_state, 
            self.context_rules['normal']).get('ui_adjustments', {})
        
        # Adjust based on task load
        if task_load == 'high':
            recommendations['information_density'] = 'high'
            recommendations['layout_compactness'] = 'compact'
        elif task_load == 'low':
            recommendations['information_density'] = 'medium'
            recommendations['layout_compactness'] = 'spacious'
        
        # Adjust based on time of day
        if time_of_day in ['evening', 'night']:
            recommendations['color_scheme'] = 'dark'
            recommendations['brightness'] = 'low'
        else:
            recommendations['color_scheme'] = 'light'
            recommendations['brightness'] = 'medium'
        
        return recommendations

class UIPredictor:
    """Main UI prediction engine."""
    
    def __init__(self):
        self.pattern_analyzer = InteractionPatternAnalyzer()
        self.context_analyzer = ContextAnalyzer()
        self.prediction_cache = {}
    
    def predict_optimal_ui(self, cognitive_state: Dict[str, Any], 
                           workflow_context: Dict[str, Any],
                           user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predict optimal UI configuration based on multiple factors.
        
        Args:
            cognitive_state: Current cognitive state
            workflow_context: Current workflow context
            user_preferences: User preference overrides
            
        Returns:
            Dictionary of predicted optimal UI configuration
        """
        # Generate cache key
        cache_key = self._generate_cache_key(cognitive_state, workflow_context)
        
        # Check cache
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]
        
        # Analyze context
        context_recommendations = self.context_analyzer.analyze_context(
            cognitive_state, workflow_context
        )
        
        # Get historical patterns
        historical_patterns = self.pattern_analyzer.analyze_patterns()
        
        # Combine recommendations
        final_recommendations = self._combine_recommendations(
            context_recommendations, historical_patterns, user_preferences
        )
        
        # Cache result
        self.prediction_cache[cache_key] = final_recommendations
        
        return final_recommendations
    
    def _generate_cache_key(self, cognitive_state: Dict[str, Any], 
                           workflow_context: Dict[str, Any]) -> str:
        """Generate cache key for prediction caching."""
        key_data = {
            'focus': round(cognitive_state.get('focus_level', 0.5), 1),
            'stress': round(cognitive_state.get('stress_level', 0.3), 1),
            'task_count': len(workflow_context.get('pending_tasks', [])),
            'stage': workflow_context.get('current_stage', 'unknown')
        }
        
        return json.dumps(key_data, sort_keys=True)
    
    def _combine_recommendations(self, context_recs: Dict[str, Any], 
                                historical_patterns: Dict[str, Any],
                                user_prefs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine recommendations from different sources."""
        final_recs = context_recs.copy()
        
        # Apply historical pattern overrides
        if historical_patterns.get('preference_trends'):
            preferences = historical_patterns['preference_trends']
            
            # Override with user's preferred theme if available
            if 'ui_themes' in preferences:
                final_recs['color_scheme'] = preferences['ui_themes'].get('preferred_theme', 
                    final_recs.get('color_scheme', 'default'))
            
            # Override with user's preferred layout if available
            if 'layout_preferences' in preferences:
                final_recs['layout_compactness'] = preferences['layout_preferences'].get('preferred_layout',
                    final_recs.get('layout_compactness', 'default'))
        
        # Apply user preference overrides
        if user_preferences:
            for key, value in user_preferences.items():
                final_recs[key] = value
        
        # Ensure all required fields are present
        self._ensure_required_fields(final_recs)
        
        return final_recs
    
    def _ensure_required_fields(self, recommendations: Dict[str, Any]):
        """Ensure all required UI fields are present."""
        required_fields = {
            'color_scheme': 'default',
            'information_density': 'medium',
            'layout_compactness': 'default',
            'animation_speed': 'normal',
            'brightness': 'medium'
        }
        
        for field, default_value in required_fields.items():
            if field not in recommendations:
                recommendations[field] = default_value
    
    def record_interaction(self, interaction_data: Dict[str, Any]):
        """
        Record a user interaction for future predictions.
        
        Args:
            interaction_data: Dictionary containing interaction details
        """
        self.pattern_analyzer.record_interaction(interaction_data)
        
        # Clear cache periodically to adapt to new patterns
        if len(self.prediction_cache) > 100:
            self.prediction_cache = {}
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get insights about user patterns and preferences.
        
        Returns:
            Dictionary of user insights and patterns
        """
        patterns = self.pattern_analyzer.analyze_patterns()
        
        insights = {
            'interaction_count': len(self.pattern_analyzer.interaction_history),
            'frequent_actions': patterns.get('frequent_actions', []),
            'preference_trends': patterns.get('preference_trends', {}),
            'feature_usage': patterns.get('feature_usage', {})
        }
        
        return insights