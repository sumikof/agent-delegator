"""
User Profile Management Module

Manages user profiles, preferences, and personalization data for predictive UI.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class UserProfileManager:
    """Manages user profiles and preferences."""
    
    def __init__(self, profile_dir: str = ".predictive_ui_profiles"):
        """
        Initialize user profile manager.
        
        Args:
            profile_dir: Directory to store user profiles
        """
        self.profile_dir = Path(profile_dir)
        self.current_user_id = "default_user"
        self._ensure_profile_directory()
        self._load_or_create_profile()
    
    def _ensure_profile_directory(self):
        """Ensure profile directory exists."""
        if not self.profile_dir.exists():
            self.profile_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_profile_path(self) -> Path:
        """Get path to current user's profile file."""
        return self.profile_dir / f"{self.current_user_id}.json"
    
    def _load_or_create_profile(self):
        """Load existing profile or create a new one."""
        profile_path = self._get_profile_path()
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    self.user_profile = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.user_profile = self._create_default_profile()
        else:
            self.user_profile = self._create_default_profile()
            self._save_profile()
    
    def _create_default_profile(self) -> Dict[str, Any]:
        """Create default user profile."""
        return {
            'user_id': self.current_user_id,
            'preferences': {
                'ui_theme': 'light',
                'color_scheme': 'default',
                'layout_compactness': 'default',
                'animation_speed': 'normal',
                'information_density': 'medium',
                'font_size': 'medium',
                'language': 'en'
            },
            'usage_statistics': {
                'total_sessions': 0,
                'total_interactions': 0,
                'last_active': None
            },
            'feature_preferences': {},
            'behavioral_patterns': {}
        }
    
    def _save_profile(self):
        """Save current user profile to file."""
        profile_path = self._get_profile_path()
        
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profile, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Failed to save user profile: {e}")
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get current user profile.
        
        Returns:
            Dictionary containing user profile
        """
        return self.user_profile.copy()
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Returns:
            Dictionary containing user preferences
        """
        return self.user_profile.get('preferences', {}).copy()
    
    def update_preferences(self, new_preferences: Dict[str, Any]):
        """
        Update user preferences.
        
        Args:
            new_preferences: Dictionary of preferences to update
        """
        current_prefs = self.user_profile.get('preferences', {})
        current_prefs.update(new_preferences)
        self.user_profile['preferences'] = current_prefs
        self._save_profile()
    
    def update_user_profile(self, interaction_data: Dict[str, Any]):
        """
        Update user profile based on interaction data.
        
        Args:
            interaction_data: Dictionary containing interaction details
        """
        # Update usage statistics
        usage_stats = self.user_profile.get('usage_statistics', {})
        usage_stats['total_interactions'] = usage_stats.get('total_interactions', 0) + 1
        usage_stats['last_active'] = interaction_data.get('timestamp')
        self.user_profile['usage_statistics'] = usage_stats
        
        # Update feature preferences
        features_used = interaction_data.get('features_used', [])
        if features_used:
            feature_prefs = self.user_profile.get('feature_preferences', {})
            for feature in features_used:
                feature_prefs[feature] = feature_prefs.get(feature, 0) + 1
            self.user_profile['feature_preferences'] = feature_prefs
        
        # Update behavioral patterns
        action_type = interaction_data.get('action_type')
        if action_type:
            patterns = self.user_profile.get('behavioral_patterns', {})
            patterns[action_type] = patterns.get(action_type, 0) + 1
            self.user_profile['behavioral_patterns'] = patterns
        
        self._save_profile()
    
    def set_user_id(self, user_id: str):
        """
        Set current user ID and load corresponding profile.
        
        Args:
            user_id: User ID to switch to
        """
        if user_id != self.current_user_id:
            # Save current profile
            self._save_profile()
            
            # Switch user
            self.current_user_id = user_id
            self._load_or_create_profile()
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user usage statistics.
        
        Returns:
            Dictionary containing usage statistics
        """
        return self.user_profile.get('usage_statistics', {}).copy()
    
    def get_feature_preferences(self) -> Dict[str, Any]:
        """
        Get user feature preferences.
        
        Returns:
            Dictionary containing feature preferences
        """
        return self.user_profile.get('feature_preferences', {}).copy()
    
    def get_behavioral_patterns(self) -> Dict[str, Any]:
        """
        Get user behavioral patterns.
        
        Returns:
            Dictionary containing behavioral patterns
        """
        return self.user_profile.get('behavioral_patterns', {}).copy()
    
    def reset_profile(self):
        """Reset current user profile to defaults."""
        self.user_profile = self._create_default_profile()
        self._save_profile()
    
    def export_profile(self) -> str:
        """
        Export user profile as JSON string.
        
        Returns:
            JSON string containing user profile
        """
        return json.dumps(self.user_profile, indent=2, ensure_ascii=False)
    
    def import_profile(self, profile_json: str):
        """
        Import user profile from JSON string.
        
        Args:
            profile_json: JSON string containing user profile
        """
        try:
            new_profile = json.loads(profile_json)
            if 'user_id' in new_profile:
                self.user_profile = new_profile
                self._save_profile()
                return True
            return False
        except json.JSONDecodeError:
            return False