"""
Plugin system for dynamic agent loading and management.

This module provides the core functionality for loading agents dynamically
as plugins, managing their lifecycle, and integrating them into the
orchestration system.
"""

from .loader import PluginLoader
from .manager import PluginManager
from .registry import PluginRegistry

__all__ = ["PluginLoader", "PluginManager", "PluginRegistry"]