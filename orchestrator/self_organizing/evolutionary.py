"""
進化的学習システム

適応戦略を進化させるシステム
"""

import random
import time
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import deque


@dataclass
class AdaptationExperience:
    """適応経験の記録"""
    strategy: Dict[str, Any]
    context: Dict[str, Any]
    result: Dict[str, Any]
    timestamp: float
    performance_improvement: float


@dataclass
class EvolvedStrategy:
    """進化した適応戦略"""
    strategy_id: str
    strategy_data: Dict[str, Any]
    fitness_score: float
    generation: int
    parent_ids: List[str]


class EvolutionaryLearningSystem:
    """進化的学習システム"""
    
    def __init__(self, max_experiences: int = 1000, population_size: int = 50):
        """進化的学習システムを初期化"""
        self.experience_history = deque(maxlen=max_experiences)
        self.strategy_population = []
        self.population_size = population_size
        self.generation = 0
        self.knowledge_base = {}
        
        # 初期人口を生成
        self._initialize_population()
        
    def _initialize_population(self) -> None:
        """初期人口を生成"""
        # 基本的な適応戦略を生成
        base_strategies = [
            {
                "name": "role_swap",
                "parameters": {
                    "swap_probability": 0.3,
                    "max_swaps": 3,
                    "target_roles": ["developer", "reviewer"]
                }
            },
            {
                "name": "load_balancing",
                "parameters": {
                    "balance_threshold": 0.2,
                    "max_transfers": 2,
                    "priority_roles": ["orchestrator", "planner"]
                }
            },
            {
                "name": "capability_matching",
                "parameters": {
                    "matching_weight": 0.8,
                    "exploration_rate": 0.1,
                    "required_capabilities": ["coding", "testing"]
                }
            },
            {
                "name": "performance_based",
                "parameters": {
                    "performance_weight": 0.9,
                    "stability_weight": 0.1,
                    "min_performance": 0.7
                }
            }
        ]
        
        # 初期人口を生成
        for i in range(self.population_size):
            base_strategy = random.choice(base_strategies)
            
            # 戦略を少し変化させる
            mutated_strategy = self._mutate_strategy(base_strategy)
            
            self.strategy_population.append(EvolvedStrategy(
                strategy_id=f"gen0_strategy_{i}",
                strategy_data=mutated_strategy,
                fitness_score=0.5,  # 初期フィットネススコア
                generation=0,
                parent_ids=[]
            ))
        
    def record_adaptation_experience(self, strategy: Dict[str, Any], 
                                    context: Dict[str, Any], 
                                    result: Dict[str, Any], 
                                    performance_improvement: float) -> None:
        """適応経験を記録"""
        experience = AdaptationExperience(
            strategy=strategy,
            context=context,
            result=result,
            timestamp=time.time(),
            performance_improvement=performance_improvement
        )
        
        self.experience_history.append(experience)
        
        # 知識ベースを更新
        self._update_knowledge_base(experience)
        
    def _update_knowledge_base(self, experience: AdaptationExperience) -> None:
        """知識ベースを更新"""
        strategy_key = experience.strategy["name"]
        
        if strategy_key not in self.knowledge_base:
            self.knowledge_base[strategy_key] = {
                "total_experiences": 0,
                "success_count": 0,
                "total_improvement": 0.0,
                "context_patterns": {}
            }
        
        knowledge = self.knowledge_base[strategy_key]
        knowledge["total_experiences"] += 1
        
        if experience.result["status"] == "success":
            knowledge["success_count"] += 1
        
        knowledge["total_improvement"] += experience.performance_improvement
        
        # コンテキストパターンを記録
        for key, value in experience.context.items():
            if key not in knowledge["context_patterns"]:
                knowledge["context_patterns"][key] = {}
            
            if value not in knowledge["context_patterns"][key]:
                knowledge["context_patterns"][key][value] = {"count": 0, "success_rate": 0.0}
            
            pattern = knowledge["context_patterns"][key][value]
            pattern["count"] += 1
            
            if experience.result["status"] == "success":
                # 簡略化：成功率を更新
                pattern["success_rate"] = pattern["count"] / (pattern["count"] + 1) * pattern["success_rate"] + 1.0 / (pattern["count"] + 1)
        
    def evolve_strategies(self) -> List[EvolvedStrategy]:
        """適応戦略を進化させる"""
        # 現在の人口を評価
        self._evaluate_population_fitness()
        
        # 新しい世代を生成
        new_population = []
        
        # エリート選択：上位個体を保持
        elite_size = max(2, int(self.population_size * 0.1))
        elite_strategies = sorted(self.strategy_population, key=lambda x: x.fitness_score, reverse=True)[:elite_size]
        
        for strategy in elite_strategies:
            new_population.append(EvolvedStrategy(
                strategy_id=f"gen{self.generation+1}_elite_{strategy.strategy_id}",
                strategy_data=strategy.strategy_data.copy(),
                fitness_score=strategy.fitness_score,
                generation=self.generation + 1,
                parent_ids=[strategy.strategy_id]
            ))
        
        # 交叉と突然変異
        while len(new_population) < self.population_size:
            # 親を選択
            parent1, parent2 = self._select_parents()
            
            # 交叉
            child_strategy = self._crossover_strategies(parent1, parent2)
            
            # 突然変異
            child_strategy = self._mutate_strategy(child_strategy)
            
            new_population.append(EvolvedStrategy(
                strategy_id=f"gen{self.generation+1}_child_{len(new_population)}",
                strategy_data=child_strategy,
                fitness_score=0.5,  # 初期フィットネススコア
                generation=self.generation + 1,
                parent_ids=[parent1.strategy_id, parent2.strategy_id]
            ))
        
        # 人口を更新
        self.strategy_population = new_population
        self.generation += 1
        
        return self.strategy_population
        
    def _evaluate_population_fitness(self) -> None:
        """人口のフィットネスを評価"""
        for strategy in self.strategy_population:
            # 知識ベースからフィットネススコアを計算
            strategy_name = strategy.strategy_data["name"]
            
            if strategy_name in self.knowledge_base:
                knowledge = self.knowledge_base[strategy_name]
                
                if knowledge["total_experiences"] > 0:
                    # 成功率と平均改善率に基づいてフィットネスを計算
                    success_rate = knowledge["success_count"] / knowledge["total_experiences"]
                    avg_improvement = knowledge["total_improvement"] / knowledge["total_experiences"]
                    
                    # フィットネススコア = 成功率 * (1 + 平均改善率)
                    fitness = success_rate * (1 + avg_improvement)
                    strategy.fitness_score = min(max(fitness, 0.1), 1.0)
            else:
                # 知識ベースにない場合はデフォルトのフィットネス
                strategy.fitness_score = 0.5
        
    def _select_parents(self) -> Tuple[EvolvedStrategy, EvolvedStrategy]:
        """親を選択（トーナメント選択）"""
        tournament_size = 5
        
        # トーナメント1
        tournament1 = random.sample(self.strategy_population, tournament_size)
        parent1 = max(tournament1, key=lambda x: x.fitness_score)
        
        # トーナメント2
        tournament2 = random.sample(self.strategy_population, tournament_size)
        parent2 = max(tournament2, key=lambda x: x.fitness_score)
        
        return parent1, parent2
        
    def _crossover_strategies(self, parent1: EvolvedStrategy, parent2: EvolvedStrategy) -> Dict[str, Any]:
        """戦略を交叉"""
        # 同じ戦略タイプの場合はパラメータを交叉
        if parent1.strategy_data["name"] == parent2.strategy_data["name"]:
            child_strategy = parent1.strategy_data.copy()
            
            # パラメータをランダムに交叉
            for param in parent1.strategy_data["parameters"].keys():
                if param in parent2.strategy_data["parameters"]:
                    if random.random() < 0.5:
                        # 親2のパラメータを継承
                        child_strategy["parameters"][param] = parent2.strategy_data["parameters"][param]
            
            return child_strategy
        else:
            # 異なる戦略タイプの場合はランダムに選択
            return random.choice([parent1.strategy_data, parent2.strategy_data])
        
    def _mutate_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """戦略を突然変異"""
        mutated_strategy = json.loads(json.dumps(strategy))  # ディープコピー
        
        # パラメータを突然変異
        for param, value in strategy["parameters"].items():
            if random.random() < 0.2:  # 20%の確率で突然変異
                if isinstance(value, float):
                    # 数値パラメータを変化
                    mutation_factor = 1 + (random.random() - 0.5) * 0.4  # ±20%
                    mutated_strategy["parameters"][param] = max(0.1, min(1.0, value * mutation_factor))
                elif isinstance(value, int):
                    # 整数パラメータを変化
                    mutation = max(-2, min(2, int((random.random() - 0.5) * 4)))
                    mutated_strategy["parameters"][param] = max(1, value + mutation)
                elif isinstance(value, list):
                    # リストパラメータを変化
                    if len(value) > 0 and random.random() < 0.5:
                        # アイテムを追加または削除
                        if random.random() < 0.5 and len(value) > 1:
                            # アイテムを削除
                            mutated_strategy["parameters"][param] = value[:-1]
                        else:
                            # アイテムを追加（簡略化：ランダムなアイテムを追加）
                            if value:  # リストが空でない場合
                                mutated_strategy["parameters"][param] = value + [value[0]]
        
        return mutated_strategy
        
    def get_best_strategy(self, context: Dict[str, Any] = None) -> EvolvedStrategy:
        """最良の戦略を取得"""
        if not self.strategy_population:
            return None
        
        # コンテキストに基づいて戦略を選択
        if context:
            return self._select_context_aware_strategy(context)
        else:
            # フィットネスに基づいて戦略を選択
            return max(self.strategy_population, key=lambda x: x.fitness_score)
        
    def _select_context_aware_strategy(self, context: Dict[str, Any]) -> EvolvedStrategy:
        """コンテキスト認識戦略を選択"""
        best_strategy = None
        best_score = -1
        
        for strategy in self.strategy_population:
            strategy_name = strategy.strategy_data["name"]
            
            if strategy_name in self.knowledge_base:
                knowledge = self.knowledge_base[strategy_name]
                score = strategy.fitness_score
                
                # コンテキストに基づいてスコアを調整
                for key, value in context.items():
                    if key in knowledge["context_patterns"] and value in knowledge["context_patterns"][key]:
                        pattern = knowledge["context_patterns"][key][value]
                        # コンテキストパターンの成功率に基づいてスコアを調整
                        score *= (1 + pattern["success_rate"])
                
                if score > best_score:
                    best_strategy = strategy
                    best_score = score
        
        return best_strategy if best_strategy else max(self.strategy_population, key=lambda x: x.fitness_score)
        
    def get_strategy_population(self) -> List[EvolvedStrategy]:
        """現在の戦略人口を取得"""
        return self.strategy_population.copy()
        
    def get_knowledge_base(self) -> Dict[str, Any]:
        """知識ベースを取得"""
        return json.loads(json.dumps(self.knowledge_base))  # ディープコピー
        
    def get_generation(self) -> int:
        """現在の世代を取得"""
        return self.generation
        
    def get_experience_history(self) -> List[AdaptationExperience]:
        """適応経験履歴を取得"""
        return list(self.experience_history)