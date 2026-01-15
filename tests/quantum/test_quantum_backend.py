"""
量子バックエンドのテスト
"""

import unittest
from unittest.mock import patch, MagicMock
from orchestrator.quantum.quantum_backend import QuantumBackend, QiskitBackend, QuantumSimulatorBackend, get_quantum_backend


class TestQuantumBackend(unittest.TestCase):
    """量子バックエンドのテスト"""
    
    def test_quantum_backend_abstract(self):
        """抽象基底クラスのテスト"""
        # 抽象基底クラスは直接インスタンス化できない
        with self.assertRaises(TypeError):
            QuantumBackend()
    
    def test_quantum_simulator_backend(self):
        """量子シミュレーターバックエンドのテスト"""
        # Qiskitがインストールされていない場合はスキップ
        try:
            import qiskit  # noqa: F401
        except ImportError:
            self.skipTest("Qiskit is not installed")
        
        # シミュレーターバックエンドの作成
        backend = QuantumSimulatorBackend()
        
        # 初期化
        result = backend.initialize()
        self.assertTrue(result)
        
        # バックエンド情報の取得
        info = backend.get_backend_info()
        self.assertIn('name', info)
        self.assertIn('simulator', info['name'])
        
        # 利用可能性の確認
        self.assertTrue(backend.is_available())
        
        # コンテキストマネージャーのテスト
        with backend as b:
            self.assertIsNotNone(b)
    
    @patch('orchestrator.quantum.quantum_backend.IBMQ')
    def test_qiskit_backend_mock(self, mock_ibmq):
        """Qiskitバックエンドのモックテスト"""
        # モックの設定
        mock_provider = MagicMock()
        mock_backend = MagicMock()
        mock_backend.configuration.return_value.n_qubits = 5
        mock_backend.status.return_value.operational = True
        mock_backend.name.return_value = 'mock_quantum_computer'
        
        mock_provider.backends.return_value = [mock_backend]
        mock_ibmq.get_provider.return_value = mock_provider
        
        # Qiskitバックエンドの作成
        backend = QiskitBackend({'min_qubits': 5})
        
        # 初期化（モックが呼び出される）
        with patch('orchestrator.quantum.quantum_backend.least_busy', return_value=mock_backend):
            result = backend.initialize()
            self.assertTrue(result)
        
        # バックエンド情報の取得
        info = backend.get_backend_info()
        self.assertEqual(info['name'], 'mock_quantum_computer')
        
        # 利用可能性の確認
        self.assertTrue(backend.is_available())
    
    def test_get_quantum_backend(self):
        """量子バックエンドの取得テスト"""
        # シミュレーターバックエンドの取得
        backend = get_quantum_backend('simulator')
        self.assertIsInstance(backend, QuantumSimulatorBackend)
        
        # 存在しないバックエンドタイプ
        with self.assertRaises(ValueError):
            get_quantum_backend('unknown')


if __name__ == '__main__':
    unittest.main()