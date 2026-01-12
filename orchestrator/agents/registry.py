"""Agent Registry.

This module provides a registry for managing agent classes.
"""

from __future__ import annotations

from typing import Dict, Type

from .base import Agent


class AgentRegistry:
    """Registry for agent classes.

    This class maintains a mapping of agent IDs to their corresponding agent classes.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Type[Agent]] = {}

    def register(self, agent_id: str, agent_class: Type[Agent]) -> None:
        """Register an agent class with the given ID.

        Args:
            agent_id: The ID of the agent.
            agent_class: The agent class to register.
        """
        self._agents[agent_id] = agent_class

    def get(self, agent_id: str) -> Type[Agent]:
        """Get the agent class for the given ID.

        Args:
            agent_id: The ID of the agent.

        Returns:
            The agent class corresponding to the ID.

        Raises:
            KeyError: If the agent ID is not found in the registry.
        """
        return self._agents[agent_id]

    def list(self) -> list[str]:
        """List all registered agent IDs.

        Returns:
            A list of all registered agent IDs.
        """
        return list(self._agents.keys())


# Global agent registry instance
registry = AgentRegistry()