"""Context management for the orchestrator.

This module provides context management utilities for the orchestrator.
"""

from __future__ import annotations

from typing import Any, Dict


class ContextManager:
    """Context manager for the orchestrator.

    This class manages the context that is passed between agents during workflow execution.
    """

    def __init__(self) -> None:
        self._context: Dict[str, Any] = {}

    def get(self, key: str, default: Any | None = None) -> Any:
        """Get a value from the context.

        Args:
            key: The key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The value associated with the key, or the default value if the key is not found.
        """
        return self._context.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the context.

        Args:
            key: The key to set.
            value: The value to associate with the key.
        """
        self._context[key] = value

    def update(self, context: Dict[str, Any]) -> None:
        """Update the context with the given dictionary.

        Args:
            context: A dictionary of key-value pairs to update the context with.
        """
        self._context.update(context)

    def get_all(self) -> Dict[str, Any]:
        """Get the entire context.

        Returns:
            The entire context dictionary.
        """
        return self._context.copy()

    def clear(self) -> None:
        """Clear the context."""
        self._context.clear()


# Global context manager instance
context_manager = ContextManager()
