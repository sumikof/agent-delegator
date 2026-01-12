"""Agent package for the orchestrator.

Each concrete agent implements a ``run`` method that receives a context dict and
returns a response conforming to the common response schema defined in
``response_schema.json``. For now the agents are simple placeholders that return
an ``OK`` status.
"""

from .base import Agent

__all__ = [
    "Agent",
]

