"""
ハイブリッド学習コントローラー

量子アルゴリズムとクラシカルアルゴリズムの協調制御を提供
"""

from typing import Optional, Dict, Any, List, Tuple
import logging
import time
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AlgorithmPerformance:
    """アルゴリズムのパフォーマンスメトリクス"""
    algorithm_name: str
    execution_time: float
    success_rate: float
    quality_score: float
    resource_usage: Dict[str, float]
    
    def get_overall_score(self) -> float:
        """総合スコアを計算"""
        # パフォーマンス、品質、リソース使用のバランスを考慮
        return (0.4 * (1.0 / (1.0 + self.execution_time)) + 
                0.3 * self.success_rate + 
                0.2 * self.quality_score + 
                0.1 * (1.0 / (1.0 + sum(self.resource_usage.values()))))


class HybridLearningController:
    """
    ハイブリッド学習コントローラー
    
    量子アルゴリズムとクラシカルアルゴリズムの協調制御を提供
    """
    
    def __init__(self, quantum_backend: Optional[Any] = None, 
                 classical_models: Optional[Dict[str, Any]] = None):
        """
        ハイブリッド学習コントローラーを初期化
        
        Args:
            quantum_backend: 量子バックエンド
            classical_models: クラシカルモデルの辞書
        """
        self.quantum_backend = quantum_backend
        self.classical_models = classical_models or {}
        self.performance_history = []
        self.algorithm_registry = {}
        
        # デフォルトのアルゴリズムを登録
        self._register_default_algorithms()
        
    def _register_default_algorithms(self):
        """デフォルトのアルゴリズムを登録"""
        # 量子アルゴリズム
        self.register_algorithm('quantum', 'grover_search', self._execute_grover)
        self.register_algorithm('quantum', 'qaoa_optimizer', self._execute_qaoa)
        
        # クラシカルアルゴリズム
        self.register_algorithm('classical', 'exhaustive_search', self._execute_exhaustive_search)
        self.register_algorithm('classical', 'random_search', self._execute_random_search)
        self.register_algorithm('classical', 'gradient_descent', self._execute_gradient_descent)
        
    def register_algorithm(self, algorithm_type: str, algorithm_name: str, 
                          execution_function: callable) -> bool:
        """
        新しいアルゴリズムを登録
        
        Args:
            algorithm_type: アルゴリズムのタイプ ('quantum' or 'classical')
            algorithm_name: アルゴリズム名
            execution_function: 実行関数
            
        Returns:
            登録が成功したかどうか
        """
        if algorithm_type not in ['quantum', 'classical']:
            logger.error(f"Invalid algorithm type: {algorithm_type}")
            return False
            
        if not callable(execution_function):
            logger.error(f"Execution function is not callable")
            return False
            
        key = f"{algorithm_type}_{algorithm_name}"
        self.algorithm_registry[key] = {
            'type': algorithm_type,
            'name': algorithm_name,
            'function': execution_function,
            'performance': []
        }
        
        logger.info(f"Registered algorithm: {key}")
        return True
        
    def select_best_algorithm(self, task_type: str, task_params: Dict[str, Any]) -> Tuple[str, str]:
        """
        タスクに最適なアルゴリズムを選択
        
        Args:
            task_type: タスクのタイプ
            task_params: タスクのパラメータ
            
        Returns:
            (algorithm_type, algorithm_name) のタプル
        """
        # タスクタイプに基づいてアルゴリズムを選択
        if task_type == 'search':
            # 検索タスクの場合
            if 'quantum_grover_search' in self.algorithm_registry:
                return 'quantum', 'grover_search'
            else:
                return 'classical', 'exhaustive_search'
                
        elif task_type == 'optimization':
            # 最適化タスクの場合
            if 'quantum_qaoa_optimizer' in self.algorithm_registry:
                return 'quantum', 'qaoa_optimizer'
            else:
                return 'classical', 'gradient_descent'
                
        elif task_type == 'classification':
            # 分類タスクの場合
            if self.quantum_backend and 'quantum_quantum_neural_network' in self.algorithm_registry:
                return 'quantum', 'quantum_neural_network'
            else:
                return 'classical', 'logistic_regression'
                
        else:
            # デフォルト: クラシカルアルゴリズム
            return 'classical', 'random_search'
            
    def execute_task(self, task_type: str, task_params: Dict[str, Any], 
                    max_attempts: int = 3) -> Dict[str, Any]:
        """
        タスクを実行
        
        Args:
            task_type: タスクのタイプ
            task_params: タスクのパラメータ
            max_attempts: 最大試行回数
            
        Returns:
            実行結果
        """
        algorithm_type, algorithm_name = self.select_best_algorithm(task_type, task_params)
        key = f"{algorithm_type}_{algorithm_name}"
        
        if key not in self.algorithm_registry:
            return {
                'success': False,
                'error': f'Algorithm {key} not found',
                'task_type': task_type
            }
            
        algorithm_info = self.algorithm_registry[key]
        execution_function = algorithm_info['function']
        
        # 実行を試みる
        for attempt in range(max_attempts):
            start_time = time.time()
            
            try:
                result = execution_function(**task_params)
                execution_time = time.time() - start_time
                
                # パフォーマンスを記録
                performance = AlgorithmPerformance(
                    algorithm_name=key,
                    execution_time=execution_time,
                    success_rate=1.0 if result.get('success', False) else 0.0,
                    quality_score=self._calculate_quality_score(result),
                    resource_usage=self._estimate_resource_usage(algorithm_type, execution_time)
                )
                
                algorithm_info['performance'].append(performance)
                self.performance_history.append(performance)
                
                # 結果を返す
                result['algorithm_used'] = key
                result['execution_time'] = execution_time
                result['attempt'] = attempt + 1
                
                return result
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for algorithm {key}: {e}")
                
                if attempt == max_attempts - 1:
                    # 最後の試行でも失敗した場合
                    return {
                        'success': False,
                        'error': str(e),
                        'algorithm_used': key,
                        'attempt': attempt + 1,
                        'max_attempts_reached': True
                    }
                    
                # リトライ前に少し待機
                time.sleep(0.1 * (attempt + 1))
                
        return {
            'success': False,
            'error': 'Max attempts reached',
            'algorithm_used': key
        }
        
    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """
        結果の品質スコアを計算
        """
        if not result.get('success', False):
            return 0.0
            
        # 結果に基づいて品質スコアを計算
        quality = 0.5  # 基本スコア
        
        # 特定のメトリクスに基づいてスコアを調整
        if 'eigenvalue' in result:
            # 最適化タスクの場合、低い固有値ほど良い
            quality += 0.3 * (1.0 / (1.0 + abs(result['eigenvalue'])))
        
        if 'top_measurement' in result:
            # 検索タスクの場合、正解率に基づいてスコアを調整
            quality += 0.2 * (1.0 if result['top_measurement'] == result.get('target', '') else 0.0)
            
        return min(max(quality, 0.0), 1.0)
        
    def _estimate_resource_usage(self, algorithm_type: str, execution_time: float) -> Dict[str, float]:
        """
        リソース使用量を推定
        """
        if algorithm_type == 'quantum':
            # 量子アルゴリズムの場合、より多くのリソースを使用すると仮定
            return {
                'cpu': 0.3,
                'memory': 0.5,
                'quantum_credits': 0.8,
                'network': 0.2
            }
        else:
            # クラシカルアルゴリズムの場合
            return {
                'cpu': 0.5,
                'memory': 0.3,
                'quantum_credits': 0.0,
                'network': 0.1
            }
            
    def get_performance_report(self) -> Dict[str, Any]:
        """
        パフォーマンスレポートを取得
        """
        if not self.performance_history:
            return {'message': 'No performance data available'}
            
        # アルゴリズムごとのパフォーマンスを集計
        algorithm_stats = {}
        for perf in self.performance_history:
            if perf.algorithm_name not in algorithm_stats:
                algorithm_stats[perf.algorithm_name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'avg_quality': 0.0,
                    'success_rate': 0.0
                }
                
            stats = algorithm_stats[perf.algorithm_name]
            stats['count'] += 1
            stats['total_time'] += perf.execution_time
            stats['avg_quality'] += perf.quality_score
            stats['success_rate'] += perf.success_rate
            
        # 平均を計算
        for algo, stats in algorithm_stats.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['avg_quality'] /= stats['count']
            stats['success_rate'] /= stats['count']
            
        return {
            'total_executions': len(self.performance_history),
            'algorithm_stats': algorithm_stats,
            'best_performing': self._get_best_performing_algorithm()
        }
        
    def _get_best_performing_algorithm(self) -> Dict[str, Any]:
        """
        最もパフォーマンスの良いアルゴリズムを取得
        """
        if not self.performance_history:
            return {'message': 'No performance data available'}
            
        # アルゴリズムごとの総合スコアを計算
        algo_scores = {}
        for perf in self.performance_history:
            if perf.algorithm_name not in algo_scores:
                algo_scores[perf.algorithm_name] = []
            algo_scores[perf.algorithm_name].append(perf.get_overall_score())
            
        # 平均スコアを計算
        best_algo = None
        best_score = -1.0
        
        for algo, scores in algo_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_algo = algo
                
        return {
            'algorithm': best_algo,
            'average_score': best_score,
            'performance_metrics': self._get_algorithm_performance(best_algo)
        }
        
    def _get_algorithm_performance(self, algorithm_name: str) -> Dict[str, Any]:
        """
        特定のアルゴリズムのパフォーマンスメトリクスを取得
        """
        if algorithm_name not in self.algorithm_registry:
            return {'error': 'Algorithm not found'}
            
        perf_data = self.algorithm_registry[algorithm_name]['performance']
        if not perf_data:
            return {'message': 'No performance data for this algorithm'}
            
        # メトリクスを集計
        total_time = sum(p.execution_time for p in perf_data)
        avg_time = total_time / len(perf_data)
        avg_quality = sum(p.quality_score for p in perf_data) / len(perf_data)
        success_rate = sum(p.success_rate for p in perf_data) / len(perf_data)
        
        return {
            'executions': len(perf_data),
            'average_execution_time': avg_time,
            'average_quality_score': avg_quality,
            'success_rate': success_rate,
            'total_execution_time': total_time
        }
        
    # アルゴリズム実行関数
    def _execute_grover(self, **kwargs) -> Dict[str, Any]:
        """Groverのアルゴリズムを実行"""
        if not self.quantum_backend:
            return {'success': False, 'error': 'Quantum backend not available'}
            
        from .quantum_algorithms import QuantumAlgorithms
        quantum_algos = QuantumAlgorithms(self.quantum_backend)
        return quantum_algos.grover_search(**kwargs)
        
    def _execute_qaoa(self, **kwargs) -> Dict[str, Any]:
        """QAOAを実行"""
        if not self.quantum_backend:
            return {'success': False, 'error': 'Quantum backend not available'}
            
        from .quantum_algorithms import QuantumAlgorithms
        quantum_algos = QuantumAlgorithms(self.quantum_backend)
        return quantum_algos.qaoa_optimizer(**kwargs)
        
    def _execute_exhaustive_search(self, **kwargs) -> Dict[str, Any]:
        """全探索を実行"""
        from .quantum_algorithms import QuantumAlgorithms
        quantum_algos = QuantumAlgorithms()
        return quantum_algos._classical_fallback_search(**kwargs)
        
    def _execute_random_search(self, **kwargs) -> Dict[str, Any]:
        """ランダム探索を実行"""
        from .quantum_algorithms import QuantumAlgorithms
        quantum_algos = QuantumAlgorithms()
        return quantum_algos._classical_fallback_optimizer(**kwargs)
        
    def _execute_gradient_descent(self, **kwargs) -> Dict[str, Any]:
        """勾配降下法を実行"""
        # 単純な勾配降下法の実装
        cost_function = kwargs.get('cost_function')
        initial_params = kwargs.get('initial_params', np.random.rand(10))
        learning_rate = kwargs.get('learning_rate', 0.01)
        max_iterations = kwargs.get('max_iterations', 100)
        
        if not cost_function:
            return {'success': False, 'error': 'Cost function not provided'}
            
        params = initial_params.copy()
        best_params = params.copy()
        best_cost = float('inf')
        
        for iteration in range(max_iterations):
            try:
                cost, gradient = cost_function(params)
                
                if cost < best_cost:
                    best_cost = cost
                    best_params = params.copy()
                    
                # 勾配降下法の更新
                params -= learning_rate * gradient
                
            except Exception as e:
                logger.error(f"Gradient descent iteration {iteration} failed: {e}")
                break
                
        return {
            'success': True,
            'best_cost': best_cost,
            'best_params': best_params,
            'iterations': iteration + 1,
            'algorithm': 'gradient_descent'
        }


def create_hybrid_controller(quantum_backend: Optional[Any] = None, 
                           classical_models: Optional[Dict[str, Any]] = None) -> HybridLearningController:
    """
    ハイブリッド学習コントローラーを作成
    
    Args:
        quantum_backend: 量子バックエンド
        classical_models: クラシカルモデルの辞書
        
    Returns:
        ハイブリッド学習コントローラーのインスタンス
    """
    return HybridLearningController(quantum_backend, classical_models)