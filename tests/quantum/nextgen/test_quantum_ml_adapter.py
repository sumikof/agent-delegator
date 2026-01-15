#!/usr/bin/env python3
"""
次世代量子機械学習アダプタのテスト

量子機械学習アダプタの機能をテストします。
"""

import unittest
import json
import logging
from orchestrator.quantum.nextgen.quantum_ml_adapter import QuantumMLAdapter, QuantumMLConfig

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestQuantumMLAdapter(unittest.TestCase):
    """量子機械学習アダプタのテストクラス"""
    
    def setUp(self):
        """テストのセットアップ"""
        self.config = QuantumMLConfig(
            quantum_backend="qiskit",
            classical_backend="scikit-learn",
            hybrid_algorithm="vqc",
            num_qubits=4,
            num_layers=3,
            shots=1024,
            max_iterations=100,
            learning_rate=0.01,
            tolerance=1e-6
        )
        self.adapter = QuantumMLAdapter(self.config)
    
    def test_initialization(self):
        """量子機械学習アダプタの初期化テスト"""
        # 初期化前のステータス確認
        status = self.adapter.get_status()
        self.assertEqual(status["status"], "inactive")
        
        # 初期化
        result = self.adapter.initialize()
        self.assertTrue(result)
        
        # 初期化後のステータス確認
        status = self.adapter.get_status()
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["quantum_backend"], "qiskit")
        self.assertEqual(status["classical_backend"], "scikit-learn")
        self.assertEqual(status["hybrid_algorithm"], "vqc")
        self.assertEqual(status["num_qubits"], 4)
        self.assertEqual(status["num_layers"], 3)
        self.assertEqual(status["shots"], 1024)
        self.assertEqual(status["max_iterations"], 100)
        self.assertEqual(status["learning_rate"], 0.01)
        self.assertEqual(status["tolerance"], 1e-6)
    
    def test_train(self):
        """量子機械学習モデルの訓練テスト"""
        # 初期化
        self.adapter.initialize()
        
        # モックデータで訓練
        X_train = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        y_train = [0, 1, 1]
        
        result = self.adapter.train(X_train, y_train)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "量子機械学習モデルの訓練に成功")
        self.assertGreater(result["accuracy"], 0.9)
        self.assertLess(result["loss"], 0.1)
        self.assertEqual(result["iterations"], 100)
    
    def test_predict(self):
        """量子機械学習モデルの予測テスト"""
        # 初期化
        self.adapter.initialize()
        
        # モックデータで予測
        X_test = [[0.2, 0.3, 0.4], [0.5, 0.6, 0.7]]
        
        result = self.adapter.predict(X_test)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "量子機械学習モデルの予測に成功")
        self.assertEqual(len(result["predictions"]), 2)
        self.assertGreater(result["confidence"], 0.9)
    
    def test_evaluate(self):
        """量子機械学習モデルの評価テスト"""
        # 初期化
        self.adapter.initialize()
        
        # モックデータで評価
        X_test = [[0.2, 0.3, 0.4], [0.5, 0.6, 0.7]]
        y_test = [0, 1]
        
        result = self.adapter.evaluate(X_test, y_test)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "量子機械学習モデルの評価に成功")
        self.assertGreater(result["accuracy"], 0.9)
        self.assertGreater(result["precision"], 0.9)
        self.assertGreater(result["recall"], 0.9)
        self.assertGreater(result["f1_score"], 0.9)
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 初期化されていない状態で訓練を試みる
        X_train = [[0.1, 0.2, 0.3]]
        y_train = [0]
        
        # 初期化されていない場合、自動的に初期化される
        result = self.adapter.train(X_train, y_train)
        self.assertEqual(result["status"], "success")
    
    def test_config_validation(self):
        """設定の検証テスト"""
        # 無効な量子バックエンドの設定
        invalid_config = QuantumMLConfig(quantum_backend="invalid_backend")
        invalid_adapter = QuantumMLAdapter(invalid_config)
        
        # 初期化に失敗することを確認
        result = invalid_adapter.initialize()
        self.assertFalse(result)


if __name__ == "__main__":
    # テストの実行
    unittest.main(verbosity=2)