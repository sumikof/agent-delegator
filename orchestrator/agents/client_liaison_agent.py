"""Client Liaison Agent.

This agent is responsible for communicating with the client and gathering requirements.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import Agent


class ClientLiaisonAgent(Agent):
    """Client Liaison Agent implementation.

    The ``run`` method receives a context (which may be empty for the initial
    call) and returns a minimal success payload.
    """

    def run(self, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # In a full implementation this would communicate with the client.
        # For now, we provide a placeholder response.
        return {
            "status": "OK",
            "summary": "Client liaison agent executed successfully",
            "findings": [],
            "artifacts": [],
            "next_actions": [],
            "context": context or {},
            "trace_id": "placeholder-trace-id",
            "execution_time_ms": 0,
        }
