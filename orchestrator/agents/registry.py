"""Agent Registry.

This module provides a registry for managing agent classes.
"""

from __future__ import annotations

from typing import Dict, Type, Any, List

from .base import Agent


class AgentRegistry:
    """Registry for agent classes.

    This class maintains a mapping of agent IDs to their corresponding agent classes.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Type[Agent]] = {}
        self._agent_info: Dict[str, Dict[str, Any]] = {}

    def register(self, agent_id: str, agent_class: Type[Agent], 
                 capabilities: List[str] = None, 
                 current_role: str = "idle",
                 performance_score: float = 0.5,
                 adaptability_score: float = 0.5) -> None:
        """Register an agent class with the given ID.

        Args:
            agent_id: The ID of the agent.
            agent_class: The agent class to register.
            capabilities: List of agent capabilities.
            current_role: Current role of the agent.
            performance_score: Performance score of the agent.
            adaptability_score: Adaptability score of the agent.
        """
        self._agents[agent_id] = agent_class
        self._agent_info[agent_id] = {
            "capabilities": capabilities or [],
            "current_role": current_role,
            "performance_score": performance_score,
            "adaptability_score": adaptability_score
        }

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
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered agents.

        Returns:
            A dictionary containing information about all registered agents.
        """
        return self._agent_info.copy()
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get information about a specific agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            A dictionary containing information about the agent.
        """
        return self._agent_info.get(agent_id, {})
    
    def update_agent_role(self, agent_id: str, new_role: str) -> None:
        """Update the role of an agent.

        Args:
            agent_id: The ID of the agent.
            new_role: The new role to assign to the agent.
        """
        if agent_id in self._agent_info:
            self._agent_info[agent_id]["current_role"] = new_role
    
    def update_agent_performance(self, agent_id: str, performance_score: float) -> None:
        """Update the performance score of an agent.

        Args:
            agent_id: The ID of the agent.
            performance_score: The new performance score.
        """
        if agent_id in self._agent_info:
            self._agent_info[agent_id]["performance_score"] = performance_score


# Global agent registry instance
registry = AgentRegistry()
