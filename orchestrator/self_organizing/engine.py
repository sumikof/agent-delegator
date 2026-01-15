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
from .evolutionary import EvolutionaryLearningSystem, AdaptationExperience


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
        
        # 進化的学習システムを初期化
        self.evolutionary_system = EvolutionaryLearningSystem()
        self.adaptation_history = []
        self.max_history_length = 1000
        
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
            
            # 適応経験を記録
            performance_improvement = best_performance - current_performance
            adaptation_experience = AdaptationExperience(
                strategy={
                    "name": "structure_optimization",
                    "parameters": {
                        "optimization_type": "neighbor_search",
                        "neighbor_count": len(neighbor_structures)
                    }
                },
                context={
                    "agent_count": len(current_structure["agent_roles"]),
                    "task_load": environment_data["tasks"].get("queue_length", 0),
                    "avg_performance": avg_performance
                },
                result={
                    "status": "success",
                    "performance_improvement": performance_improvement
                },
                timestamp=time.time(),
                performance_improvement=performance_improvement
            )
            
            # 進化的学習システムに経験を記録
            self.evolutionary_system.record_adaptation_experience(
                strategy=adaptation_experience.strategy,
                context=adaptation_experience.context,
                result=adaptation_experience.result,
                performance_improvement=adaptation_experience.performance_improvement
            )
            
            # 適応履歴を記録
            self.adaptation_history.append(adaptation_experience)
            if len(self.adaptation_history) > self.max_history_length:
                self.adaptation_history.pop(0)
            
            # 定期的に戦略を進化させる
            if len(self.adaptation_history) % 10 == 0:  # 10回の適応ごとに進化
                self.evolutionary_system.evolve_strategies()
            
            return {
                "status": "adapted",
                "old_structure": current_structure,
                "new_structure": best_structure,
                "performance_improvement": performance_improvement,
                "evolutionary_data": {
                    "generation": self.evolutionary_system.get_generation(),
                    "strategy_count": len(self.evolutionary_system.get_strategy_population()),
                    "knowledge_base_size": len(self.evolutionary_system.get_knowledge_base())
                }
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
    
    def adapt_system_with_evolutionary_learning(self) -> Dict[str, Any]:
        """進化的学習を使用してシステムを適応"""
        if not self.evaluate_adaptation_needed():
            return {"status": "no_adaptation_needed", "reason": "adaptation_threshold_not_met"}
        
        # 環境データを取得
        environment_data = self.monitor_environment()
        
        # 進化的学習システムから最良の戦略を取得
        best_strategy = self.evolutionary_system.get_best_strategy(environment_data)
        
        if best_strategy:
            # 戦略に基づいて適応を実行
            adaptation_result = self._apply_evolutionary_strategy(best_strategy, environment_data)
            
            return {
                **adaptation_result,
                "evolutionary_strategy": {
                    "strategy_id": best_strategy.strategy_id,
                    "strategy_name": best_strategy.strategy_data["name"],
                    "generation": best_strategy.generation,
                    "fitness_score": best_strategy.fitness_score
                }
            }
        else:
            # 進化的戦略が利用できない場合は標準的な適応を使用
            return self.adapt_system()
    
    def _apply_evolutionary_strategy(self, strategy: EvolvedStrategy, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """進化的戦略を適用"""
        current_structure = self._get_current_structure()
        current_performance = self._evaluate_structure(current_structure)
        
        strategy_name = strategy.strategy_data["name"]
        strategy_params = strategy.strategy_data["parameters"]
        
        if strategy_name == "role_swap":
            # 役割入れ替え戦略
            new_structure = self._apply_role_swap_strategy(current_structure, strategy_params)
        elif strategy_name == "load_balancing":
            # 負荷均等化戦略
            new_structure = self._apply_load_balancing_strategy(current_structure, strategy_params)
        elif strategy_name == "capability_matching":
            # 能力マッチング戦略
            new_structure = self._apply_capability_matching_strategy(current_structure, strategy_params)
        elif strategy_name == "performance_based":
            # パフォーマンスベース戦略
            new_structure = self._apply_performance_based_strategy(current_structure, strategy_params)
        else:
            # 未知の戦略の場合は標準的な適応を使用
            return self.adapt_system()
        
        # 新しい構造を評価
        new_performance = self._evaluate_structure(new_structure)
        performance_improvement = new_performance - current_performance
        
        # 構造を適用
        self._apply_structure(new_structure)
        self.last_adaptation_time = time.time()
        
        # 適応経験を記録
        adaptation_experience = AdaptationExperience(
            strategy=strategy.strategy_data,
            context=environment_data,
            result={
                "status": "success" if performance_improvement > 0 else "neutral",
                "performance_improvement": performance_improvement
            },
            timestamp=time.time(),
            performance_improvement=performance_improvement
        )
        
        # 進化的学習システムに経験を記録
        self.evolutionary_system.record_adaptation_experience(
            strategy=adaptation_experience.strategy,
            context=adaptation_experience.context,
            result=adaptation_experience.result,
            performance_improvement=adaptation_experience.performance_improvement
        )
        
        # 適応履歴を記録
        self.adaptation_history.append(adaptation_experience)
        if len(self.adaptation_history) > self.max_history_length:
            self.adaptation_history.pop(0)
        
        # 定期的に戦略を進化させる
        if len(self.adaptation_history) % 10 == 0:
            self.evolutionary_system.evolve_strategies()
        
        return {
            "status": "adapted_with_evolutionary",
            "old_structure": current_structure,
            "new_structure": new_structure,
            "performance_improvement": performance_improvement,
            "evolutionary_data": {
                "generation": self.evolutionary_system.get_generation(),
                "strategy_count": len(self.evolutionary_system.get_strategy_population()),
                "knowledge_base_size": len(self.evolutionary_system.get_knowledge_base())
            }
        }
    
    def _apply_role_swap_strategy(self, structure: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """役割入れ替え戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        agent_ids = list(agent_roles.keys())
        num_swaps = min(params.get("max_swaps", 3), len(agent_ids) - 1)
        
        for _ in range(num_swaps):
            if random.random() < params.get("swap_probability", 0.3):
                i, j = random.sample(range(len(agent_ids)), 2)
                agent_i, agent_j = agent_ids[i], agent_ids[j]
                
                # 役割を入れ替え
                agent_roles[agent_i], agent_roles[agent_j] = agent_roles[agent_j], agent_roles[agent_i]
        
        return new_structure
    
    def _apply_load_balancing_strategy(self, structure: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """負荷均等化戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        # 役割の分布を均等化
        role_counts = {}
        for role in agent_roles.values():
            role_counts[role] = role_counts.get(role, 0) + 1
        
        avg_count = len(agent_roles) / len(role_counts) if role_counts else 1
        
        for role, count in role_counts.items():
            if count > avg_count * (1 + params.get("balance_threshold", 0.2)):
                # 役割を持つエージェントを減らす
                agents_with_role = [agent_id for agent_id, r in agent_roles.items() if r == role]
                excess = int(count - avg_count)
                
                for agent_id in agents_with_role[:excess]:
                    # 他の役割に割り当て
                    other_roles = [r for r in role_counts.keys() if r != role]
                    if other_roles:
                        new_role = random.choice(other_roles)
                        agent_roles[agent_id] = new_role
        
        return new_structure
    
    def _apply_capability_matching_strategy(self, structure: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """能力マッチング戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        # エージェントの能力に基づいて役割を割り当て
        all_roles = list(set(agent_roles.values()))
        if all_roles:
            for agent_id in agent_roles:
                if random.random() < params.get("exploration_rate", 0.1):
                    # 探索：ランダムな役割を割り当て
                    new_role = random.choice(all_roles)
                    agent_roles[agent_id] = new_role
                # 利用：現在の役割を維持
        
        return new_structure
    
    def _apply_performance_based_strategy(self, structure: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンスベース戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        # パフォーマンスに基づいて役割を割り当て
        all_roles = list(set(agent_roles.values()))
        if all_roles:
            for agent_id in agent_roles:
                if random.random() < params.get("performance_weight", 0.9):
                    # パフォーマンスに基づいて役割を割り当て
                    new_role = random.choice(all_roles)
                    agent_roles[agent_id] = new_role
        
        return new_structure
    
    def get_evolutionary_system(self) -> EvolutionaryLearningSystem:
        """進化的学習システムを取得"""
        return self.evolutionary_system
    
    def get_adaptation_history(self) -> List[AdaptationExperience]:
        """適応履歴を取得"""
        return list(self.adaptation_history)
