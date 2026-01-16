"""Tester Agent.

This agent is responsible for testing the deliverables.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import Agent


class TesterAgent(Agent):
    """Tester Agent implementation.

    The ``run`` method receives a context (which may be empty for the initial
    call) and returns a minimal success payload.
    """

    def run(self, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # In a full implementation this would test the deliverables.
        # For now, we provide a placeholder response.
        return {
            "status": "OK",
            "summary": "Tester agent executed successfully",
            "findings": [],
            "artifacts": [],
            "next_actions": [],
            "context": context or {},
            "trace_id": "placeholder-trace-id",
            "execution_time_ms": 0,
        }
