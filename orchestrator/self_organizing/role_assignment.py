"""
役割割り当てシステム

エージェントに役割を動的に割り当てるシステム
"""

import random
from typing import Dict, List, Any, Set
from dataclasses import dataclass


@dataclass
class RoleRequirement:
    """役割の要求仕様"""
    role_name: str
    required_capabilities: List[str]
    priority: int
    min_agents: int = 1
    max_agents: int = 1


@dataclass
class AgentCapability:
    """エージェントの能力"""
    agent_id: str
    capabilities: List[str]
    current_role: str
    performance_score: float


class RoleAssignmentSystem:
    """役割割り当てシステム"""
    
    def __init__(self):
        self.role_requirements = self._initialize_role_requirements()
        self.agent_capabilities = {}  # agent_id -> AgentCapability
        
    def _initialize_role_requirements(self) -> List[RoleRequirement]:
        """役割要求を初期化"""
        return [
            RoleRequirement(
                role_name="orchestrator",
                required_capabilities=["task_planning", "coordination"],
                priority=5,
                min_agents=1,
                max_agents=2
            ),
            RoleRequirement(
                role_name="planner",
                required_capabilities=["task_planning", "requirements_analysis"],
                priority=4,
                min_agents=1,
                max_agents=3
            ),
            RoleRequirement(
                role_name="developer",
                required_capabilities=["coding", "problem_solving"],
                priority=3,
                min_agents=2,
                max_agents=5
            ),
            RoleRequirement(
                role_name="reviewer",
                required_capabilities=["code_review", "quality_assurance"],
                priority=3,
                min_agents=1,
                max_agents=3
            ),
            RoleRequirement(
                role_name="tester",
                required_capabilities=["testing", "quality_assurance"],
                priority=2,
                min_agents=1,
                max_agents=2
            )
        ]
    
    def register_agent(self, agent_id: str, capabilities: List[str], current_role: str = "idle", performance_score: float = 0.5) -> None:
        """エージェントを登録"""
        self.agent_capabilities[agent_id] = AgentCapability(
            agent_id=agent_id,
            capabilities=capabilities,
            current_role=current_role,
            performance_score=performance_score
        )
    
    def unregister_agent(self, agent_id: str) -> None:
        """エージェントを登録解除"""
        if agent_id in self.agent_capabilities:
            del self.agent_capabilities[agent_id]
    
    def update_agent_performance(self, agent_id: str, performance_score: float) -> None:
        """エージェントのパフォーマンスを更新"""
        if agent_id in self.agent_capabilities:
            self.agent_capabilities[agent_id].performance_score = performance_score
    
    def update_agent_capabilities(self, agent_id: str, capabilities: List[str]) -> None:
        """エージェントの能力を更新"""
        if agent_id in self.agent_capabilities:
            self.agent_capabilities[agent_id].capabilities = capabilities
    
    def assign_roles(self) -> Dict[str, str]:
        """エージェントに役割を割り当て"""
        role_assignment = {}
        
        # 現在の役割割り当てを初期化
        for agent_id, agent in self.agent_capabilities.items():
            role_assignment[agent_id] = agent.current_role
        
        # 役割要求に基づいて割り当て
        for requirement in sorted(self.role_requirements, key=lambda x: x.priority, reverse=True):
            self._assign_role_for_requirement(requirement, role_assignment)
        
        return role_assignment
    
    def _assign_role_for_requirement(self, requirement: RoleRequirement, role_assignment: Dict[str, str]) -> None:
        """特定の役割要求に基づいて役割を割り当て"""
        # 現在の役割割り当て状況を確認
        current_count = sum(1 for role in role_assignment.values() if role == requirement.role_name)
        
        # 最小数を満たしていない場合は割り当てを追加
        if current_count < requirement.min_agents:
            self._assign_additional_agents(requirement, role_assignment, requirement.min_agents - current_count)
        
        # 最大数を超えている場合は割り当てを削減
        elif current_count > requirement.max_agents:
            self._reduce_agent_assignments(requirement, role_assignment, current_count - requirement.max_agents)
        
        # 最適化：より適切なエージェントに役割を再割り当て
        self._optimize_role_assignments(requirement, role_assignment)
    
    def _assign_additional_agents(self, requirement: RoleRequirement, role_assignment: Dict[str, str], num_needed: int) -> None:
        """追加のエージェントを役割に割り当て"""
        # 役割に適したエージェントを探す
        suitable_agents = []
        
        for agent_id, agent in self.agent_capabilities.items():
            # 現在の役割が優先度の低い役割であるか、アイドル状態である
            current_role_priority = self._get_role_priority(agent.current_role)
            
            if (current_role_priority < requirement.priority or 
                agent.current_role == "idle" or
                role_assignment[agent_id] == "idle"):
                
                # エージェントが役割の要求を満たしているか確認
                has_capabilities = all(cap in agent.capabilities for cap in requirement.required_capabilities)
                
                if has_capabilities:
                    suitable_agents.append((agent_id, agent))
        
        # パフォーマンススコアに基づいてソート
        suitable_agents.sort(key=lambda x: x[1].performance_score, reverse=True)
        
        # 必要な数のエージェントを割り当て
        for agent_id, _ in suitable_agents[:num_needed]:
            role_assignment[agent_id] = requirement.role_name
    
    def _reduce_agent_assignments(self, requirement: RoleRequirement, role_assignment: Dict[str, str], num_to_reduce: int) -> None:
        """役割からエージェントの割り当てを削減"""
        # 役割を持つエージェントを探す
        agents_with_role = [(agent_id, agent) for agent_id, agent in self.agent_capabilities.items() 
                           if role_assignment[agent_id] == requirement.role_name]
        
        # パフォーマンススコアに基づいてソート（低いスコアのエージェントから削減）
        agents_with_role.sort(key=lambda x: x[1].performance_score)
        
        # 削減する数のエージェントをアイドル状態にする
        for agent_id, _ in agents_with_role[:num_to_reduce]:
            role_assignment[agent_id] = "idle"
    
    def _optimize_role_assignments(self, requirement: RoleRequirement, role_assignment: Dict[str, str]) -> None:
        """役割割り当てを最適化"""
        # 役割を持つエージェントを探す
        agents_with_role = [(agent_id, agent) for agent_id, agent in self.agent_capabilities.items() 
                           if role_assignment[agent_id] == requirement.role_name]
        
        # 役割に適していないエージェントを探す
        for agent_id, agent in agents_with_role:
            # エージェントが役割の要求を満たしているか確認
            has_capabilities = all(cap in agent.capabilities for cap in requirement.required_capabilities)
            
            if not has_capabilities:
                # より適切なエージェントを探す
                better_agent = self._find_better_agent_for_role(requirement, role_assignment, agent_id)
                
                if better_agent:
                    # 役割を入れ替え
                    role_assignment[agent_id] = "idle"
                    role_assignment[better_agent] = requirement.role_name
    
    def _find_better_agent_for_role(self, requirement: RoleRequirement, role_assignment: Dict[str, str], exclude_agent_id: str) -> str:
        """役割に適したエージェントを探す"""
        best_agent_id = None
        best_score = -1
        
        for agent_id, agent in self.agent_capabilities.items():
            if agent_id == exclude_agent_id:
                continue
            
            # 現在の役割が優先度の低い役割であるか、アイドル状態である
            current_role_priority = self._get_role_priority(agent.current_role)
            
            if (current_role_priority < requirement.priority or 
                agent.current_role == "idle" or
                role_assignment[agent_id] == "idle"):
                
                # エージェントが役割の要求を満たしているか確認
                has_capabilities = all(cap in agent.capabilities for cap in requirement.required_capabilities)
                
                if has_capabilities and agent.performance_score > best_score:
                    best_agent_id = agent_id
                    best_score = agent.performance_score
        
        return best_agent_id
    
    def _get_role_priority(self, role_name: str) -> int:
        """役割の優先度を取得"""
        for requirement in self.role_requirements:
            if requirement.role_name == role_name:
                return requirement.priority
        return 0  # 未知の役割は最低優先度
    
    def get_role_requirements(self) -> List[RoleRequirement]:
        """役割要求を取得"""
        return self.role_requirements
    
    def get_agent_capabilities(self) -> Dict[str, AgentCapability]:
        """エージェントの能力を取得"""
        return self.agent_capabilities
    
    def get_current_role_distribution(self) -> Dict[str, int]:
        """現在の役割分布を取得"""
        role_distribution = {}
        
        for agent in self.agent_capabilities.values():
            role = agent.current_role
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        return role_distribution
