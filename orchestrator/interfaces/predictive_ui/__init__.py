"""
Predictive UI/UX Module

This module provides predictive and adaptive user interface capabilities
that anticipate user needs and optimize the interaction experience
based on cognitive state, historical patterns, and contextual analysis.
"""

from .predictor import UIPredictor
from .adapter import PredictiveUIAdapter
from .personalization import UserProfileManager

__all__ = ['UIPredictor', 'PredictiveUIAdapter', 'UserProfileManager']