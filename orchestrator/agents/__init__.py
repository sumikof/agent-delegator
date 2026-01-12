"""Agent package for the orchestrator.

Each concrete agent implements a ``run`` method that receives a context dict and
returns a response conforming to the common response schema defined in
``response_schema.json``. For now the agents are simple placeholders that return
an ``OK`` status.
"""

from .base import Agent
from .orchestrator_agent import OrchestratorAgent
from .client_liaison_agent import ClientLiaisonAgent
from .planner_agent import PlannerAgent
from .progress_agent import ProgressAgent
from .integrator_agent import IntegratorAgent
from .requirements_auditor_agent import RequirementsAuditorAgent
from .quality_auditor_agent import QualityAuditorAgent
from .tester_agent import TesterAgent
from .api_designer_agent import APIDesignerAgent
from .backend_dev_agent import BackendDevAgent
from .frontend_dev_agent import FrontendDevAgent
from .reviewer_be_agent import ReviewerBEAgent
from .reviewer_fe_agent import ReviewerFEAgent

__all__ = [
    "Agent",
    "OrchestratorAgent",
    "ClientLiaisonAgent",
    "PlannerAgent",
    "ProgressAgent",
    "IntegratorAgent",
    "RequirementsAuditorAgent",
    "QualityAuditorAgent",
    "TesterAgent",
    "APIDesignerAgent",
    "BackendDevAgent",
    "FrontendDevAgent",
    "ReviewerBEAgent",
    "ReviewerFEAgent",
]

