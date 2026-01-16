"""
Agent-Delegate Orchestration System

Multi-agent orchestration system using OpenHands SDK for virtual development organizations.
"""

__version__ = "0.1.0"
__author__ = "Agent-Delegate Project"

# Export main classes for public API (will be populated as we implement)
from .logging import setup_logging, get_logger, DEFAULT_LOGGING_CONFIG
from .context import ContextManager, context_manager

__all__ = [
    "__version__",
    "setup_logging",
    "get_logger",
    "DEFAULT_LOGGING_CONFIG",
    "ContextManager",
    "context_manager",
]
