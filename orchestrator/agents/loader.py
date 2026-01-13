"""Agent Loader.

This module provides functionality for loading and instantiating agents.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import Agent
from .registry import registry


class AgentLoader:
    """Loader for instantiating agents from the registry.

    This class is responsible for creating agent instances based on the agent IDs
    registered in the global agent registry.
    """

    def __init__(self) -> None:
        self._registry = registry

    def load_agent(self, agent_id: str, context: Dict[str, Any] | None = None) -> Agent:
        """Load and instantiate an agent by its ID.

        Args:
            agent_id: The ID of the agent to instantiate.
            context: Optional context to pass to the agent.

        Returns:
            An instance of the agent.

        Raises:
            KeyError: If the agent ID is not found in the registry.
        """
        agent_class = self._registry.get(agent_id)
        return agent_class()

    def list_agents(self) -> list[str]:
        """List all available agent IDs.

        Returns:
            A list of all available agent IDs.
        """
        return self._registry.list()


# Global agent loader instance
loader = AgentLoader()
