"""
Experience Feedback System Module

Collects and processes user feedback for personalized experience improvements.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class ExperienceFeedbackSystem:
    """System for collecting and processing user feedback."""
    
    def __init__(self):
        self.feedback_store = []
        self.feedback_analytics = {}
        self.satisfaction_history = []
    
    def record_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record user feedback.
        
        Args:
            feedback_data: Dictionary containing feedback information
            
        Returns:
            Result of feedback recording
        """
        # Validate feedback data
        if not self._validate_feedback(feedback_data):
            return {'status': 'error', 'message': 'Invalid feedback data'}
        
        # Add timestamp
        feedback_data['timestamp'] = datetime.now().isoformat()
        
        # Store feedback
        self.feedback_store.append(feedback_data)
        
        # Update analytics
        self._update_analytics(feedback_data)
        
        # Update satisfaction history
        if 'satisfaction' in feedback_data:
            self.satisfaction_history.append({
                'score': feedback_data['satisfaction'],
                'timestamp': feedback_data['timestamp']
            })
        
        # Keep store size manageable
        if len(self.feedback_store) > 1000:
            self.feedback_store = self.feedback_store[-1000:]
        
        if len(self.satisfaction_history) > 100:
            self.satisfaction_history = self.satisfaction_history[-100:]
        
        return {'status': 'success', 'message': 'Feedback recorded'}
    
    def _validate_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Validate feedback data structure."""
        required_fields = ['feedback_type', 'session_id']
        
        for field in required_fields:
            if field not in feedback_data:
                return False
        
        return True
    
    def _update_analytics(self, feedback_data: Dict[str, Any]):
        """Update feedback analytics."""
        feedback_type = feedback_data['feedback_type']
        
        # Initialize analytics for this feedback type if not exists
        if feedback_type not in self.feedback_analytics:
            self.feedback_analytics[feedback_type] = {
                'count': 0,
                'satisfaction_sum': 0,
                'satisfaction_count': 0,
                'feedback_categories': {}
            }
        
        # Update counts
        self.feedback_analytics[feedback_type]['count'] += 1
        
        # Update satisfaction metrics
        if 'satisfaction' in feedback_data:
            self.feedback_analytics[feedback_type]['satisfaction_sum'] += feedback_data['satisfaction']
            self.feedback_analytics[feedback_type]['satisfaction_count'] += 1
        
        # Update feedback categories
        if 'category' in feedback_data:
            category = feedback_data['category']
            if category not in self.feedback_analytics[feedback_type]['feedback_categories']:
                self.feedback_analytics[feedback_type]['feedback_categories'][category] = 0
            self.feedback_analytics[feedback_type]['feedback_categories'][category] += 1
    
    def get_feedback_analytics(self, feedback_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback analytics.
        
        Args:
            feedback_type: Specific feedback type to get analytics for (optional)
            
        Returns:
            Dictionary containing feedback analytics
        """
        if feedback_type:
            if feedback_type in self.feedback_analytics:
                analytics = self.feedback_analytics[feedback_type].copy()
                
                # Calculate average satisfaction
                if analytics['satisfaction_count'] > 0:
                    analytics['average_satisfaction'] = (
                        analytics['satisfaction_sum'] / analytics['satisfaction_count']
                    )
                else:
                    analytics['average_satisfaction'] = 0
                
                return {feedback_type: analytics}
            else:
                return {'status': 'error', 'message': f'No analytics for feedback type: {feedback_type}'}
        else:
            # Return analytics for all feedback types
            result = {}
            for fb_type, data in self.feedback_analytics.items():
                analytics = data.copy()
                if analytics['satisfaction_count'] > 0:
                    analytics['average_satisfaction'] = (
                        analytics['satisfaction_sum'] / analytics['satisfaction_count']
                    )
                else:
                    analytics['average_satisfaction'] = 0
                result[fb_type] = analytics
            
            return result
    
    def get_satisfaction_trends(self) -> Dict[str, Any]:
        """
        Get satisfaction trends over time.
        
        Returns:
            Dictionary containing satisfaction trends
        """
        if not self.satisfaction_history:
            return {'status': 'no_data', 'message': 'No satisfaction data available'}
        
        # Calculate trends
        total_scores = sum(item['score'] for item in self.satisfaction_history)
        average_score = total_scores / len(self.satisfaction_history)
        
        # Calculate recent trend (last 10 entries)
        recent_scores = self.satisfaction_history[-10:]
        if recent_scores:
            recent_avg = sum(item['score'] for item in recent_scores) / len(recent_scores)
            trend_direction = 'improving' if recent_avg > average_score else 'declining'
            trend_magnitude = abs(recent_avg - average_score)
        else:
            trend_direction = 'stable'
            trend_magnitude = 0
        
        return {
            'overall_average': average_score,
            'recent_average': recent_avg,
            'trend_direction': trend_direction,
            'trend_magnitude': trend_magnitude,
            'total_feedback_count': len(self.satisfaction_history),
            'recent_feedback_count': len(recent_scores)
        }
    
    def get_feedback_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get suggestions for experience improvements based on feedback.
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if not self.feedback_analytics:
            return suggestions
        
        # Analyze each feedback type
        for fb_type, analytics in self.feedback_analytics.items():
            avg_satisfaction = analytics.get('average_satisfaction', 0)
            
            if avg_satisfaction is None:
                avg_satisfaction = 0
            
            if avg_satisfaction < 2.5:
                suggestions.append({
                    'area': fb_type,
                    'issue': 'Low satisfaction',
                    'priority': 'high',
                    'suggestion': f'Significant improvements needed in {fb_type} area',
                    'current_score': avg_satisfaction
                })
            elif avg_satisfaction < 3.5:
                suggestions.append({
                    'area': fb_type,
                    'issue': 'Moderate satisfaction',
                    'priority': 'medium',
                    'suggestion': f'Consider enhancements for {fb_type} area',
                    'current_score': avg_satisfaction
                })
            else:
                suggestions.append({
                    'area': fb_type,
                    'issue': 'High satisfaction',
                    'priority': 'low',
                    'suggestion': f'Maintain current approach for {fb_type} area',
                    'current_score': avg_satisfaction
                })
        
        # Sort by priority
        suggestions.sort(key=lambda x: ['low', 'medium', 'high'].index(x['priority']))
        
        return suggestions
    
    def export_feedback_data(self) -> str:
        """
        Export feedback data as JSON string.
        
        Returns:
            JSON string containing feedback data
        """
        export_data = {
            'feedback_store': self.feedback_store,
            'feedback_analytics': self.feedback_analytics,
            'satisfaction_history': self.satisfaction_history
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def import_feedback_data(self, feedback_json: str) -> Dict[str, Any]:
        """
        Import feedback data from JSON string.
        
        Args:
            feedback_json: JSON string containing feedback data
            
        Returns:
            Result of import operation
        """
        try:
            import_data = json.loads(feedback_json)
            
            # Merge imported data with existing data
            if 'feedback_store' in import_data:
                self.feedback_store.extend(import_data['feedback_store'])
            
            if 'feedback_analytics' in import_data:
                for fb_type, data in import_data['feedback_analytics'].items():
                    if fb_type in self.feedback_analytics:
                        # Merge analytics
                        self.feedback_analytics[fb_type]['count'] += data['count']
                        self.feedback_analytics[fb_type]['satisfaction_sum'] += data['satisfaction_sum']
                        self.feedback_analytics[fb_type]['satisfaction_count'] += data['satisfaction_count']
                        
                        # Merge categories
                        for cat, count in data['feedback_categories'].items():
                            if cat in self.feedback_analytics[fb_type]['feedback_categories']:
                                self.feedback_analytics[fb_type]['feedback_categories'][cat] += count
                            else:
                                self.feedback_analytics[fb_type]['feedback_categories'][cat] = count
                    else:
                        self.feedback_analytics[fb_type] = data
            
            if 'satisfaction_history' in import_data:
                self.satisfaction_history.extend(import_data['satisfaction_history'])
            
            return {'status': 'success', 'message': 'Feedback data imported successfully'}
            
        except json.JSONDecodeError:
            return {'status': 'error', 'message': 'Invalid JSON data'}
    
    def clear_feedback_data(self):
        """Clear all feedback data."""
        self.feedback_store = []
        self.feedback_analytics = {}
        self.satisfaction_history = []
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get summary of feedback data.
        
        Returns:
            Dictionary containing feedback summary
        """
        return {
            'total_feedback_count': len(self.feedback_store),
            'feedback_types': list(self.feedback_analytics.keys()),
            'satisfaction_history_count': len(self.satisfaction_history),
            'average_satisfaction': self._calculate_overall_satisfaction()
        }
    
    def _calculate_overall_satisfaction(self) -> float:
        """Calculate overall satisfaction score."""
        if not self.satisfaction_history:
            return 0.0
        
        total = sum(item['score'] for item in self.satisfaction_history)
        return total / len(self.satisfaction_history)