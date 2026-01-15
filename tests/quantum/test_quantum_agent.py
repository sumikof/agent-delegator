"""
量子AIエージェントのテスト
"""

import unittest
from unittest.mock import patch, MagicMock
from orchestrator.quantum.quantum_agent import QuantumAIAgent, QuantumOptimizationAgent, QuantumSearchAgent


class TestQuantumAIAgent(unittest.TestCase):
    """量子AIエージェントのテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        # モック設定を作成
        self.mock_config = {
            'quantum_backend': 'simulator',
            'quantum_backend_config': {}
        }
        
        # 量子AIエージェントを初期化
        self.agent = QuantumAIAgent(self.mock_config)
    
    def test_agent_initialization(self):
        """エージェント初期化のテスト"""
        # エージェントが初期化されたことを確認
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, 'QuantumAIAgent')
        
        # 量子モジュールが初期化されたことを確認
        self.assertIsNotNone(self.agent.quantum_backend)
        self.assertIsNotNone(self.agent.quantum_algorithms)
        self.assertIsNotNone(self.agent.hybrid_controller)
    
    def test_get_capabilities(self):
        """機能取得のテスト"""
        capabilities = self.agent.get_capabilities()
        
        # 必要な情報が含まれていることを確認
        self.assertEqual(capabilities['name'], 'QuantumAIAgent')
        self.assertEqual(capabilities['type'], 'quantum_ai_agent')
        self.assertTrue(capabilities['quantum_backend_available'])
        self.assertTrue(capabilities['quantum_algorithms_available'])
    
    @patch('orchestrator.quantum.quantum_agent.HybridLearningController.execute_task')
    def test_execute_task_success(self, mock_execute):
        """タスク実行成功のテスト"""
        # モックの設定
        mock_execute.return_value = {
            'success': True,
            'result': 'test_result',
            'algorithm_used': 'quantum_grover'
        }
        
        # タスクを実行
        task = {
            'type': 'search',
            'params': {'target': '11'}
        }
        
        response = self.agent.execute(task)
        
        # 成功応答を確認
        self.assertEqual(response.status, 'OK')
        self.assertIn('Quantum AI task completed', response.summary)
        self.assertEqual(len(response.artifacts), 1)
    
    @patch('orchestrator.quantum.quantum_agent.HybridLearningController.execute_task')
    def test_execute_task_failure(self, mock_execute):
        """タスク実行失敗のテスト"""
        # モックの設定
        mock_execute.return_value = {
            'success': False,
            'error': 'Test error',
            'algorithm_used': 'quantum_grover'
        }
        
        # タスクを実行
        task = {
            'type': 'search',
            'params': {'target': '11'}
        }
        
        response = self.agent.execute(task)
        
        # エラー応答を確認
        self.assertEqual(response.status, 'NG')
        self.assertIn('Quantum AI task failed', response.summary)
        self.assertEqual(len(response.findings), 1)
        self.assertEqual(response.findings[0]['severity'], 'ERROR')


class TestQuantumOptimizationAgent(unittest.TestCase):
    """量子最適化エージェントのテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        # モック設定を作成
        self.mock_config = {
            'quantum_backend': 'simulator',
            'quantum_backend_config': {}
        }
        
        # 量子最適化エージェントを初期化
        self.agent = QuantumOptimizationAgent(self.mock_config)
    
    def test_agent_specialization(self):
        """エージェントの専門化をテスト"""
        # エージェントが正しく初期化されたことを確認
        self.assertEqual(self.agent.name, 'QuantumOptimizationAgent')
        
        # 機能を確認
        capabilities = self.agent.get_capabilities()
        self.assertEqual(capabilities['specialization'], 'optimization_problems')
        self.assertIn('QAOA', capabilities['supported_algorithms'])
    
    @patch('orchestrator.quantum.quantum_agent.QuantumAIAgent.execute')
    def test_execute_optimization_task(self, mock_execute):
        """最適化タスク実行のテスト"""
        # モックの設定
        mock_execute.return_value = MagicMock()
        
        # 最適化タスクを実行
        task = {
            'params': {'cost_function': lambda x: x**2}
        }
        
        self.agent.execute(task)
        
        # タスクが最適化タスクとして実行されたことを確認
        mock_execute.assert_called_once()
        called_task = mock_execute.call_args[0][0]
        self.assertEqual(called_task['type'], 'optimization')


class TestQuantumSearchAgent(unittest.TestCase):
    """量子検索エージェントのテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        # モック設定を作成
        self.mock_config = {
            'quantum_backend': 'simulator',
            'quantum_backend_config': {}
        }
        
        # 量子検索エージェントを初期化
        self.agent = QuantumSearchAgent(self.mock_config)
    
    def test_agent_specialization(self):
        """エージェントの専門化をテスト"""
        # エージェントが正しく初期化されたことを確認
        self.assertEqual(self.agent.name, 'QuantumSearchAgent')
        
        # 機能を確認
        capabilities = self.agent.get_capabilities()
        self.assertEqual(capabilities['specialization'], 'search_problems')
        self.assertIn('Grover', capabilities['supported_algorithms'])
    
    @patch('orchestrator.quantum.quantum_agent.QuantumAIAgent.execute')
    def test_execute_search_task(self, mock_execute):
        """検索タスク実行のテスト"""
        # モックの設定
        mock_execute.return_value = MagicMock()
        
        # 検索タスクを実行
        task = {
            'params': {'target': '1101'}
        }
        
        self.agent.execute(task)
        
        # タスクが検索タスクとして実行されたことを確認
        mock_execute.assert_called_once()
        called_task = mock_execute.call_args[0][0]
        self.assertEqual(called_task['type'], 'search')


if __name__ == '__main__':
    unittest.main()