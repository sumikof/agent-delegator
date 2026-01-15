"""
自己組織化型AIエージェントシステムのコアモジュール

このモジュールは、エージェントシステムの自己組織化機能を提供します。
"""

from .engine import SelfOrganizingEngine
from .adaptation import AdaptationAlgorithm
from .role_assignment import RoleAssignmentSystem
from .communication import CommunicationTopology

__all__ = [
    "SelfOrganizingEngine",
    "AdaptationAlgorithm", 
    "RoleAssignmentSystem",
    "CommunicationTopology"
]