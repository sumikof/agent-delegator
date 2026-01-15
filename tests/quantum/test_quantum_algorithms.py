"""
量子アルゴリズムのテスト
"""

import unittest
from unittest.mock import patch, MagicMock
from orchestrator.quantum.quantum_algorithms import QuantumAlgorithms


class TestQuantumAlgorithms(unittest.TestCase):
    """量子アルゴリズムのテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        # モックバックエンドを作成
        self.mock_backend = MagicMock()
        self.mock_backend._backend = MagicMock()
        
        # 量子アルゴリズムを初期化
        self.quantum_algos = QuantumAlgorithms(self.mock_backend)
    
    def test_create_basic_circuit(self):
        """基本的な量子回路の作成テスト"""
        # Qiskitがインストールされていない場合はスキップ
        try:
            import qiskit  # noqa: F401
        except ImportError:
            self.skipTest("Qiskit is not installed")
        
        # 基本的な量子回路を作成
        circuit = self.quantum_algos.create_basic_circuit(num_qubits=2)
        
        # 回路が作成されたことを確認
        self.assertIsNotNone(circuit)
        
        # 回路のプロパティを確認
        self.assertEqual(circuit.num_qubits, 2)
    
    @patch('orchestrator.quantum.quantum_algorithms.Grover')
    def test_grover_search(self, mock_grover):
        """Groverのアルゴリズムのテスト"""
        # Qiskitがインストールされていない場合はスキップ
        try:
            import qiskit  # noqa: F401
        except ImportError:
            self.skipTest("Qiskit is not installed")
        
        # モックの設定
        mock_result = MagicMock()
        mock_result.top_measurement = '11'
        mock_result.measurements = {'11': 100}
        mock_result.circuit_results = {}
        
        mock_grover_instance = MagicMock()
        mock_grover_instance.amplify.return_value = mock_result
        mock_grover.return_value = mock_grover_instance
        
        # Groverのアルゴリズムを実行
        result = self.quantum_algos.grover_search(num_qubits=2, target='11')
        
        # 結果を確認
        self.assertTrue(result['success'])
        self.assertEqual(result['top_measurement'], '11')
    
    def test_classical_fallback_search(self):
        """クラシカルフォールバック検索のテスト"""
        # クラシカルフォールバックをテスト
        result = self.quantum_algos._classical_fallback_search(num_qubits=2, target='11')
        
        # 結果を確認
        self.assertTrue(result['success'])
        self.assertEqual(result['top_measurement'], '11')
        self.assertTrue(result['fallback'])
        
        # 存在しないターゲットのテスト
        result = self.quantum_algos._classical_fallback_search(num_qubits=2, target='000')
        self.assertFalse(result['success'])
    
    def test_execute_with_fallback(self):
        """フォールバック機能のテスト"""
        # 存在しないアルゴリズムのテスト
        result = self.quantum_algos.execute_with_fallback('nonexistent_algorithm')
        self.assertFalse(result['success'])
        
        # Groverのアルゴリズムのフォールバックテスト
        with patch.object(self.quantum_algos, 'grover_search', side_effect=Exception('Test error')):
            result = self.quantum_algos.execute_with_fallback('grover_search', num_qubits=2, target='11')
            self.assertTrue(result['fallback'])


if __name__ == '__main__':
    unittest.main()