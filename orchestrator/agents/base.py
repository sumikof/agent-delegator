"""Base class for all agents used by the orchestrator.

Each concrete agent should inherit from :class:`Agent` and implement the
``run`` method, which receives a ``context`` dictionary and returns a response
dictionary that conforms to the common response schema defined in
``response_schema.json``.
"""

from __future__ import annotations

from typing import Any, Dict


class Agent:
    """Abstract base class for agents.

    Subclasses must implement :meth:`run`.
    """

    def __init__(self, agent_id: str, name: str | None = None) -> None:
        self.id = agent_id
        self.name = name or agent_id

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's logic.

        Args:
            context: Arbitrary data passed from previous agents or the
                orchestrator.

        Returns:
            A dictionary matching the common response schema.
        """
        raise NotImplementedError("Agent subclasses must implement the run method")
