"""
Brainwave Interface Module

This module provides integration between EEG brainwave data and the AI agent orchestration system.
It enables real-time cognitive state analysis and adaptive workflow control based on user brainwave patterns.
"""

from .processor import BrainwaveProcessor
from .adapter import BrainwaveAgentAdapter
from .mapper import ActionMapper

__all__ = ['BrainwaveProcessor', 'BrainwaveAgentAdapter', 'ActionMapper']