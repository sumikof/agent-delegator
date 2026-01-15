"""
適応アルゴリズム

自己組織化システムのための適応アルゴリズムを提供
"""

import random
import math
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class AdaptationStrategy:
    """適応戦略の定義"""
    name: str
    description: str
    parameters: Dict[str, Any]


class AdaptationAlgorithm:
    """適応アルゴリズムの実装"""
    
    def __init__(self):
        self.strategies = self._initialize_strategies()
        self.performance_history = []
        self.max_history_length = 100
        
    def _initialize_strategies(self) -> List[AdaptationStrategy]:
        """適応戦略を初期化"""
        return [
            AdaptationStrategy(
                name="role_swap",
                description="エージェント間で役割を入れ替える",
                parameters={"swap_probability": 0.3, "max_swaps": 3}
            ),
            AdaptationStrategy(
                name="load_balancing",
                description="作業負荷を均等化する",
                parameters={"balance_threshold": 0.2, "max_transfers": 2}
            ),
            AdaptationStrategy(
                name="capability_matching",
                description="エージェントの能力に基づいて役割を割り当てる",
                parameters={"matching_weight": 0.8, "exploration_rate": 0.1}
            ),
            AdaptationStrategy(
                name="performance_based",
                description="パフォーマンスに基づいて役割を割り当てる",
                parameters={"performance_weight": 0.9, "stability_weight": 0.1}
            )
        ]
    
    def select_strategy(self, system_state: Dict[str, Any]) -> AdaptationStrategy:
        """適応戦略を選択"""
        # 簡略化版：ランダムに戦略を選択
        # 実際の実装では、システム状態に基づいて戦略を選択
        return random.choice(self.strategies)
    
    def apply_strategy(self, strategy: AdaptationStrategy, current_structure: Dict[str, Any]) -> Dict[str, Any]:
        """適応戦略を適用"""
        if strategy.name == "role_swap":
            return self._apply_role_swap(strategy, current_structure)
        elif strategy.name == "load_balancing":
            return self._apply_load_balancing(strategy, current_structure)
        elif strategy.name == "capability_matching":
            return self._apply_capability_matching(strategy, current_structure)
        elif strategy.name == "performance_based":
            return self._apply_performance_based(strategy, current_structure)
        else:
            return current_structure
    
    def _apply_role_swap(self, strategy: AdaptationStrategy, structure: Dict[str, Any]) -> Dict[str, Any]:
        """役割入れ替え戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        agent_ids = list(agent_roles.keys())
        num_swaps = min(strategy.parameters["max_swaps"], len(agent_ids) - 1)
        
        for _ in range(num_swaps):
            if random.random() < strategy.parameters["swap_probability"]:
                i, j = random.sample(range(len(agent_ids)), 2)
                agent_i, agent_j = agent_ids[i], agent_ids[j]
                
                # 役割を入れ替え
                agent_roles[agent_i], agent_roles[agent_j] = agent_roles[agent_j], agent_roles[agent_i]
        
        return new_structure
    
    def _apply_load_balancing(self, strategy: AdaptationStrategy, structure: Dict[str, Any]) -> Dict[str, Any]:
        """負荷均等化戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        # 簡略化版：役割の均等化
        # 実際の実装では、作業負荷のデータに基づいてバランシング
        role_counts = {}
        for role in agent_roles.values():
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # 役割の分布を均等化
        avg_count = len(agent_roles) / len(role_counts) if role_counts else 1
        
        for role, count in role_counts.items():
            if count > avg_count * (1 + strategy.parameters["balance_threshold"]):
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
    
    def _apply_capability_matching(self, strategy: AdaptationStrategy, structure: Dict[str, Any]) -> Dict[str, Any]:
        """能力マッチング戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        # 簡略化版：エージェントの能力に基づいて役割を割り当て
        # 実際の実装では、エージェントプロファイルのデータを使用
        
        # ランダムに役割を割り当て（簡略化）
        all_roles = list(set(agent_roles.values()))
        if all_roles:
            for agent_id in agent_roles:
                if random.random() < strategy.parameters["exploration_rate"]:
                    # 探索：ランダムな役割を割り当て
                    new_role = random.choice(all_roles)
                    agent_roles[agent_id] = new_role
                else:
                    # 利用：現在の役割を維持
                    pass
        
        return new_structure
    
    def _apply_performance_based(self, strategy: AdaptationStrategy, structure: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンスベース戦略を適用"""
        import copy
        new_structure = copy.deepcopy(structure)
        agent_roles = new_structure["agent_roles"]
        
        # 簡略化版：パフォーマンスに基づいて役割を割り当て
        # 実際の実装では、エージェントのパフォーマンスメトリクスを使用
        
        # ランダムに役割を割り当て（簡略化）
        all_roles = list(set(agent_roles.values()))
        if all_roles:
            for agent_id in agent_roles:
                if random.random() < strategy.parameters["performance_weight"]:
                    # パフォーマンスに基づいて役割を割り当て
                    new_role = random.choice(all_roles)
                    agent_roles[agent_id] = new_role
        
        return new_structure
    
    def learn_from_performance(self, strategy: AdaptationStrategy, performance_improvement: float) -> None:
        """パフォーマンスから学習"""
        # パフォーマンス履歴を記録
        self.performance_history.append({
            "strategy": strategy.name,
            "improvement": performance_improvement,
            "timestamp": time.time()
        })
        
        # 履歴の長さを制限
        if len(self.performance_history) > self.max_history_length:
            self.performance_history.pop(0)
    
    def get_best_strategy(self) -> AdaptationStrategy:
        """最良の戦略を取得"""
        if not self.performance_history:
            return random.choice(self.strategies)
        
        # 過去のパフォーマンスに基づいて最良の戦略を選択
        strategy_performance = {}
        for entry in self.performance_history:
            strategy = entry["strategy"]
            improvement = entry["improvement"]
            strategy_performance[strategy] = strategy_performance.get(strategy, 0) + improvement
        
        best_strategy_name = max(strategy_performance.items(), key=lambda x: x[1])[0]
        
        for strategy in self.strategies:
            if strategy.name == best_strategy_name:
                return strategy
        
        return random.choice(self.strategies)


# 簡略化のためにtimeモジュールをインポート
import time