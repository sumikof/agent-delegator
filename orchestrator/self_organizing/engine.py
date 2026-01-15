"""
自己組織化エンジン

エージェントシステムの自己組織化機能を提供するコアエンジン
"""

import time
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from ..agents.registry import AgentRegistry
from ..monitoring import PerformanceMonitor


@dataclass
class AgentProfile:
    """エージェントの能力とパフォーマンスプロファイル"""
    agent_id: str
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    current_role: str
    adaptability_score: float


@dataclass
class SystemState:
    """システムの現在の状態"""
    agent_profiles: Dict[str, AgentProfile]
    task_queue_status: Dict[str, Any]
    communication_topology: Dict[str, Any]
    performance_metrics: Dict[str, float]


class SelfOrganizingEngine:
    """自己組織化エンジンのメインコンポーネント"""
    
    def __init__(self, agent_registry: AgentRegistry, performance_monitor: PerformanceMonitor):
        """自己組織化エンジンを初期化"""
        self.agent_registry = agent_registry
        self.performance_monitor = performance_monitor
        self.current_state = self._initialize_system_state()
        self.adaptation_threshold = 0.75
        self.last_adaptation_time = 0
        self.adaptation_cooldown = 300  # 5分間のクールダウン
        
    def _initialize_system_state(self) -> SystemState:
        """システム状態を初期化"""
        agent_profiles = {}
        
        # エージェントレジストリからエージェントプロファイルを作成
        for agent_id, agent_info in self.agent_registry.get_all_agents().items():
            agent_profiles[agent_id] = AgentProfile(
                agent_id=agent_id,
                capabilities=agent_info.get("capabilities", []),
                performance_metrics=agent_info.get("performance_metrics", {}),
                current_role=agent_info.get("current_role", "idle"),
                adaptability_score=agent_info.get("adaptability_score", 0.5)
            )
        
        return SystemState(
            agent_profiles=agent_profiles,
            task_queue_status={},
            communication_topology={},
            performance_metrics={}
        )
    
    def monitor_environment(self) -> Dict[str, Any]:
        """システム環境を監視"""
        environment_data = {
            "timestamp": time.time(),
            "agents": {},
            "tasks": {},
            "performance": {}
        }
        
        # エージェントの状態を監視
        for agent_id, agent_profile in self.current_state.agent_profiles.items():
            environment_data["agents"][agent_id] = {
                "status": "active",
                "current_role": agent_profile.current_role,
                "performance": agent_profile.performance_metrics
            }
        
        # タスクキューの状態を監視
        environment_data["tasks"] = self.performance_monitor.get_task_queue_status()
        
        # パフォーマンスメトリクスを監視
        environment_data["performance"] = self.performance_monitor.get_current_metrics()
        
        return environment_data
    
    def evaluate_adaptation_needed(self) -> bool:
        """適応の必要性を評価"""
        current_time = time.time()
        
        # クールダウン期間中は適応を行わない
        if current_time - self.last_adaptation_time < self.adaptation_cooldown:
            return False
        
        # 環境データを取得
        environment_data = self.monitor_environment()
        
        # 適応スコアを計算
        adaptation_score = self._calculate_adaptation_score(environment_data)
        
        return adaptation_score > self.adaptation_threshold
    
    def _calculate_adaptation_score(self, environment_data: Dict[str, Any]) -> float:
        """適応スコアを計算"""
        # タスクキューの負荷を評価
        task_load = environment_data["tasks"].get("queue_length", 0) / max(environment_data["tasks"].get("max_capacity", 1), 1)
        
        # エージェントのパフォーマンスを評価
        avg_performance = 0
        if environment_data["agents"]:
            performances = [agent["performance"].get("success_rate", 0.5) for agent in environment_data["agents"].values()]
            avg_performance = sum(performances) / len(performances)
        
        # システムの安定性を評価
        stability = environment_data["performance"].get("stability_score", 0.8)
        
        # 適応スコアを計算（タスク負荷が高く、パフォーマンスが低く、安定性が低いほど適応スコアが高くなる）
        adaptation_score = 0.3 * task_load + 0.4 * (1 - avg_performance) + 0.3 * (1 - stability)
        
        return adaptation_score
    
    def adapt_system(self) -> Dict[str, Any]:
        """システムを適応させる"""
        if not self.evaluate_adaptation_needed():
            return {"status": "no_adaptation_needed", "reason": "adaptation_threshold_not_met"}
        
        # 環境データを取得
        environment_data = self.monitor_environment()
        
        # 現在の構造を評価
        current_structure = self._get_current_structure()
        current_performance = self._evaluate_structure(current_structure)
        
        # 近傍構造を生成
        neighbor_structures = self._generate_neighbor_structures(current_structure)
        
        # 最良の構造を見つける
        best_structure = current_structure
        best_performance = current_performance
        
        for structure in neighbor_structures:
            performance = self._evaluate_structure(structure)
            if performance > best_performance:
                best_structure = structure
                best_performance = performance
        
        # 最良の構造を適用
        if best_structure != current_structure:
            self._apply_structure(best_structure)
            self.last_adaptation_time = time.time()
            
            return {
                "status": "adapted",
                "old_structure": current_structure,
                "new_structure": best_structure,
                "performance_improvement": best_performance - current_performance
            }
        else:
            return {"status": "no_improvement", "reason": "no_better_structure_found"}
    
    def _get_current_structure(self) -> Dict[str, Any]:
        """現在の構造を取得"""
        return {
            "agent_roles": {agent_id: profile.current_role for agent_id, profile in self.current_state.agent_profiles.items()},
            "communication_topology": self.current_state.communication_topology
        }
    
    def _evaluate_structure(self, structure: Dict[str, Any]) -> float:
        """構造を評価"""
        # 構造の評価ロジック（簡略化版）
        # 実際の実装では、より複雑な評価メトリクスを使用
        
        # 役割の適合性を評価
        role_fitness = 0
        for agent_id, role in structure["agent_roles"].items():
            agent_profile = self.current_state.agent_profiles[agent_id]
            if role in agent_profile.capabilities:
                role_fitness += 0.2  # 役割が能力に合っている
            else:
                role_fitness -= 0.1  # 役割が能力に合っていない
        
        # 通信効率を評価
        comm_efficiency = 0.5  # 簡略化
        
        # 全体的な評価
        overall_score = 0.6 * role_fitness + 0.4 * comm_efficiency
        
        return overall_score
    
    def _generate_neighbor_structures(self, current_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """近傍構造を生成"""
        neighbor_structures = []
        
        # 簡単な近傍生成：役割の入れ替え
        agent_ids = list(current_structure["agent_roles"].keys())
        
        if len(agent_ids) >= 2:
            # 2つのエージェントの役割を入れ替え
            for i in range(min(3, len(agent_ids))):  # 最大3つの近傍を生成
                for j in range(i + 1, len(agent_ids)):
                    neighbor = json.loads(json.dumps(current_structure))  # ディープコピー
                    
                    # 役割を入れ替え
                    role_i = neighbor["agent_roles"][agent_ids[i]]
                    role_j = neighbor["agent_roles"][agent_ids[j]]
                    neighbor["agent_roles"][agent_ids[i]] = role_j
                    neighbor["agent_roles"][agent_ids[j]] = role_i
                    
                    neighbor_structures.append(neighbor)
        
        return neighbor_structures
    
    def _apply_structure(self, structure: Dict[str, Any]) -> None:
        """構造を適用"""
        # 役割を更新
        for agent_id, role in structure["agent_roles"].items():
            if agent_id in self.current_state.agent_profiles:
                self.current_state.agent_profiles[agent_id].current_role = role
        
        # 通信トポロジを更新
        self.current_state.communication_topology = structure["communication_topology"]
        
        # エージェントレジストリを更新
        for agent_id, profile in self.current_state.agent_profiles.items():
            self.agent_registry.update_agent_role(agent_id, profile.current_role)
    
    def get_system_state(self) -> SystemState:
        """現在のシステム状態を取得"""
        return self.current_state
    
    def update_agent_performance(self, agent_id: str, metrics: Dict[str, float]) -> None:
        """エージェントのパフォーマンスメトリクスを更新"""
        if agent_id in self.current_state.agent_profiles:
            self.current_state.agent_profiles[agent_id].performance_metrics.update(metrics)
