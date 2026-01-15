"""
ハイブリッドコントローラーのテスト
"""

import unittest
from unittest.mock import patch, MagicMock
from orchestrator.quantum.hybrid_controller import HybridLearningController, AlgorithmPerformance


class TestHybridController(unittest.TestCase):
    """ハイブリッドコントローラーのテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        # モックバックエンドを作成
        self.mock_backend = MagicMock()
        
        # ハイブリッドコントローラーを初期化
        self.controller = HybridLearningController(self.mock_backend)
    
    def test_algorithm_performance(self):
        """アルゴリズムパフォーマンスのテスト"""
        # パフォーマンスメトリクスを作成
        perf = AlgorithmPerformance(
            algorithm_name='test_algo',
            execution_time=1.5,
            success_rate=0.9,
            quality_score=0.8,
            resource_usage={'cpu': 0.5, 'memory': 0.3}
        )
        
        # 総合スコアを計算
        score = perf.get_overall_score()
        self.assertGreater(score, 0)
        self.assertLess(score, 1)
    
    def test_register_algorithm(self):
        """アルゴリズム登録のテスト"""
        # 新しいアルゴリズムを登録
        def test_function(**kwargs):
            return {'success': True, 'result': 'test'}
        
        result = self.controller.register_algorithm('quantum', 'test_algo', test_function)
        self.assertTrue(result)
        
        # 登録されたアルゴリズムを確認
        self.assertIn('quantum_test_algo', self.controller.algorithm_registry)
        
        # 無効なアルゴリズムタイプのテスト
        result = self.controller.register_algorithm('invalid', 'test_algo', test_function)
        self.assertFalse(result)
    
    def test_select_best_algorithm(self):
        """最適なアルゴリズム選択のテスト"""
        # 検索タスクの場合
        algo_type, algo_name = self.controller.select_best_algorithm('search', {})
        self.assertEqual(algo_type, 'quantum')
        self.assertEqual(algo_name, 'grover_search')
        
        # 最適化タスクの場合
        algo_type, algo_name = self.controller.select_best_algorithm('optimization', {})
        self.assertEqual(algo_type, 'quantum')
        self.assertEqual(algo_name, 'qaoa_optimizer')
        
        # 存在しないタスクの場合
        algo_type, algo_name = self.controller.select_best_algorithm('unknown', {})
        self.assertEqual(algo_type, 'classical')
        self.assertEqual(algo_name, 'random_search')
    
    @patch('orchestrator.quantum.hybrid_controller.time.time', return_value=1000.0)
    def test_execute_task(self, mock_time):
        """タスク実行のテスト"""
        # モック関数を登録
        def mock_function(**kwargs):
            return {'success': True, 'result': 'mock_result'}
        
        self.controller.register_algorithm('classical', 'mock_algo', mock_function)
        
        # タスクを実行
        result = self.controller.execute_task('unknown', {'param': 'value'})
        
        # 結果を確認
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 'mock_result')
        self.assertEqual(result['algorithm_used'], 'classical_mock_algo')
    
    def test_performance_report(self):
        """パフォーマンスレポートのテスト"""
        # パフォーマンスデータが空の場合
        report = self.controller.get_performance_report()
        self.assertEqual(report['message'], 'No performance data available')
        
        # パフォーマンスデータを追加
        perf = AlgorithmPerformance(
            algorithm_name='test_algo',
            execution_time=1.0,
            success_rate=1.0,
            quality_score=1.0,
            resource_usage={'cpu': 0.5}
        )
        self.controller.performance_history.append(perf)
        
        # パフォーマンスレポートを取得
        report = self.controller.get_performance_report()
        self.assertEqual(report['total_executions'], 1)
        self.assertIn('test_algo', report['algorithm_stats'])


if __name__ == '__main__':
    unittest.main()