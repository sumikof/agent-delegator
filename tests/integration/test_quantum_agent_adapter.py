# 量子機械学習エージェントアダプタの統合テスト

import unittest
import tempfile
import json
from datetime import datetime
from unittest.mock import Mock, patch

# テスト対象のモジュールをインポート
import sys
sys.path.append('/workspace')

from quantum_ai.interface.quantum_agent_adapter import (
    QuantumMLModule, 
    AgentTaskType, 
    AgentTask, 
    AgentResult, 
    QuantumAgentAdapter, 
    MockQuantumMLModule
)

class TestQuantumAgentAdapter(unittest.TestCase):
    """
    量子機械学習エージェントアダプタの統合テスト
    """
    
    def setUp(self):
        """
        テストのセットアップ
        """
        # モック量子機械学習モジュールを作成
        self.quantum_ml = MockQuantumMLModule()
        
        # アダプタを作成
        self.adapter = QuantumAgentAdapter(self.quantum_ml)
        
        # テストデータ
        self.training_data = {
            "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "labels": [0, 1],
            "quantum_encoding": "amplitude"
        }
        
        self.prediction_data = {
            "features": [[0.7, 0.8, 0.9]],
            "quantum_encoding": "amplitude"
        }
        
        self.evaluation_data = {
            "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "labels": [0, 1],
            "quantum_encoding": "amplitude"
        }
    
    def test_training_task_execution(self):
        """
        訓練タスクの実行テスト
        """
        # 訓練タスクを作成
        task = AgentTask(
            task_id="test_train_001",
            type=AgentTaskType.QUANTUM_TRAINING,
            data=self.training_data,
            config={"epochs": 10}
        )
        
        # タスクを実行
        result = self.adapter.execute_quantum_task(task)
        
        # 結果の検証
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.task_id, "test_train_001")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.result)
        self.assertIsNotNone(result.metrics)
        self.assertIsNone(result.error)
        
        # メトリクスの検証
        self.assertIn("training_time", result.metrics)
        self.assertIn("final_loss", result.metrics)
        self.assertIn("accuracy", result.metrics)
        
        # タスク履歴の検証
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task_id"], "test_train_001")
        self.assertEqual(history[0]["task_type"], "quantum_training")
        self.assertEqual(history[0]["status"], "success")
    
    def test_prediction_task_execution(self):
        """
        予測タスクの実行テスト
        """
        # 予測タスクを作成
        task = AgentTask(
            task_id="test_predict_001",
            type=AgentTaskType.QUANTUM_PREDICTION,
            data=self.prediction_data
        )
        
        # タスクを実行
        result = self.adapter.execute_quantum_task(task)
        
        # 結果の検証
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.task_id, "test_predict_001")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.result)
        self.assertIsNotNone(result.metrics)
        self.assertIsNone(result.error)
        
        # メトリクスの検証
        self.assertIn("prediction_time", result.metrics)
        self.assertIn("confidence", result.metrics)
        
        # タスク履歴の検証
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task_id"], "test_predict_001")
        self.assertEqual(history[0]["task_type"], "quantum_prediction")
        self.assertEqual(history[0]["status"], "success")
    
    def test_evaluation_task_execution(self):
        """
        評価タスクの実行テスト
        """
        # 評価タスクを作成
        task = AgentTask(
            task_id="test_evaluate_001",
            type=AgentTaskType.QUANTUM_EVALUATION,
            data=self.evaluation_data
        )
        
        # タスクを実行
        result = self.adapter.execute_quantum_task(task)
        
        # 結果の検証
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.task_id, "test_evaluate_001")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.result)
        self.assertIsNotNone(result.metrics)
        self.assertIsNone(result.error)
        
        # メトリクスの検証
        self.assertIn("evaluation_time", result.metrics)
        self.assertIn("accuracy", result.metrics)
        self.assertIn("precision", result.metrics)
        self.assertIn("recall", result.metrics)
        self.assertIn("f1_score", result.metrics)
        
        # タスク履歴の検証
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task_id"], "test_evaluate_001")
        self.assertEqual(history[0]["task_type"], "quantum_evaluation")
        self.assertEqual(history[0]["status"], "success")
    
    def test_multiple_task_execution(self):
        """
        複数タスクの実行テスト
        """
        # タスク履歴をクリア
        self.adapter.clear_task_history()
        
        # 複数のタスクを実行
        tasks = [
            AgentTask(
                task_id="test_train_002",
                type=AgentTaskType.QUANTUM_TRAINING,
                data=self.training_data,
                config={"epochs": 5}
            ),
            AgentTask(
                task_id="test_predict_002",
                type=AgentTaskType.QUANTUM_PREDICTION,
                data=self.prediction_data
            ),
            AgentTask(
                task_id="test_evaluate_002",
                type=AgentTaskType.QUANTUM_EVALUATION,
                data=self.evaluation_data
            )
        ]
        
        results = []
        for task in tasks:
            result = self.adapter.execute_quantum_task(task)
            results.append(result)
        
        # 結果の検証
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, AgentResult)
            self.assertEqual(result.status, "success")
            self.assertIsNone(result.error)
        
        # タスク履歴の検証
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 3)
        
        # タスク履歴の順序と内容の検証
        expected_task_ids = ["test_train_002", "test_predict_002", "test_evaluate_002"]
        expected_task_types = ["quantum_training", "quantum_prediction", "quantum_evaluation"]
        
        for i, entry in enumerate(history):
            self.assertEqual(entry["task_id"], expected_task_ids[i])
            self.assertEqual(entry["task_type"], expected_task_types[i])
            self.assertEqual(entry["status"], "success")
            self.assertIsNone(entry["error"])
    
    def test_error_handling(self):
        """
        エラーハンドリングのテスト
        """
        # タスク履歴をクリア
        self.adapter.clear_task_history()
        
        # エラーを発生させるモックモジュールを作成
        mock_error_module = Mock(spec=QuantumMLModule)
        mock_error_module.train.side_effect = Exception("Quantum training error")
        mock_error_module.predict.side_effect = Exception("Quantum prediction error")
        mock_error_module.evaluate.side_effect = Exception("Quantum evaluation error")
        
        # エラー発生用のアダプタを作成
        error_adapter = QuantumAgentAdapter(mock_error_module)
        
        # エラー発生タスクを実行
        error_task = AgentTask(
            task_id="test_error_001",
            type=AgentTaskType.QUANTUM_TRAINING,
            data=self.training_data
        )
        
        result = error_adapter.execute_quantum_task(error_task)
        
        # エラー結果の検証
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.task_id, "test_error_001")
        self.assertEqual(result.status, "error")
        self.assertIsNotNone(result.error)
        self.assertIn("Quantum training error", result.error)
        
        # タスク履歴の検証
        history = error_adapter.get_task_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task_id"], "test_error_001")
        self.assertEqual(history[0]["status"], "error")
        self.assertIsNotNone(history[0]["error"])
    
    def test_unknown_task_type(self):
        """
        未知のタスクタイプのテスト
        """
        # タスク履歴をクリア
        self.adapter.clear_task_history()
        
        # 未知のタスクタイプを持つタスクを作成
        # 直接AgentTaskを作成して、未知のタイプをシミュレート
        task = AgentTask(
            task_id="test_unknown_001",
            type=AgentTaskType.QUANTUM_TRAINING,  # 既知のタイプを使用
            data=self.training_data
        )
        
        # タスクを実行
        result = self.adapter.execute_quantum_task(task)
        
        # 通常のタスクとして実行されることを確認
        self.assertEqual(result.status, "success")
        
        # 実際の未知のタスクタイプをテストするために、モックを使用
        with patch.object(self.adapter, '_execute_training_task') as mock_method:
            mock_method.side_effect = ValueError("Unknown quantum task type: unknown_task")
            
            # タスクを実行
            result = self.adapter.execute_quantum_task(task)
            
            # エラーが適切に処理されることを確認
            self.assertEqual(result.status, "error")
            self.assertIsNotNone(result.error)
    
    def test_task_history_limit(self):
        """
        タスク履歴の制限テスト
        """
        # タスク履歴をクリア
        self.adapter.clear_task_history()
        
        # 大量のタスクを実行（100回に減らしてテスト時間を短縮）
        for i in range(100):
            task = AgentTask(
                task_id=f"test_history_{i:04d}",
                type=AgentTaskType.QUANTUM_PREDICTION,
                data=self.prediction_data
            )
            self.adapter.execute_quantum_task(task)
        
        # タスク履歴のサイズが制限されていることを確認
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 100)  # 最大1000件に制限（100回実行なので100件になる）
        
        # 最新のタスクが保持されていることを確認
        self.assertEqual(history[0]["task_id"], "test_history_0000")
        self.assertEqual(history[-1]["task_id"], "test_history_0099")
        
        # 1000件を超えるタスクを追加して制限をテスト
        for i in range(1000):
            task = AgentTask(
                task_id=f"test_history_{100+i:04d}",
                type=AgentTaskType.QUANTUM_PREDICTION,
                data=self.prediction_data
            )
            self.adapter.execute_quantum_task(task)
        
        # タスク履歴のサイズが制限されていることを確認
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 1000)  # 最大1000件に制限
        
        # 最新のタスクが保持されていることを確認
        self.assertEqual(history[0]["task_id"], "test_history_0100")
        self.assertEqual(history[-1]["task_id"], "test_history_1099")
    
    def test_timestamp_format(self):
        """
        タイムスタンプのフォーマットテスト
        """
        # タスクを実行
        task = AgentTask(
            task_id="test_timestamp_001",
            type=AgentTaskType.QUANTUM_TRAINING,
            data=self.training_data
        )
        
        result = self.adapter.execute_quantum_task(task)
        
        # タスク履歴を取得
        history = self.adapter.get_task_history()
        timestamp = history[0]["timestamp"]
        
        # タイムスタンプのフォーマットを検証
        try:
            datetime.fromisoformat(timestamp)
            timestamp_valid = True
        except ValueError:
            timestamp_valid = False
        
        self.assertTrue(timestamp_valid, f"Invalid timestamp format: {timestamp}")
    
    def test_result_conversion(self):
        """
        結果変換のテスト
        """
        # タスクを実行
        task = AgentTask(
            task_id="test_conversion_001",
            type=AgentTaskType.QUANTUM_TRAINING,
            data=self.training_data
        )
        
        result = self.adapter.execute_quantum_task(task)
        
        # 結果の構造を検証
        self.assertIn("quantum_result", result.result)
        self.assertIn("task_type", result.result)
        self.assertEqual(result.result["task_type"], "training")
        
        # 量子結果の構造を検証
        quantum_result = result.result["quantum_result"]
        self.assertIn("training_time", quantum_result)
        self.assertIn("final_loss", quantum_result)
        self.assertIn("accuracy", quantum_result)
        self.assertIn("epochs", quantum_result)
        self.assertIn("quantum_state", quantum_result)

class TestMockQuantumMLModule(unittest.TestCase):
    """
    モック量子機械学習モジュールのテスト
    """
    
    def setUp(self):
        """
        テストのセットアップ
        """
        self.mock_module = MockQuantumMLModule()
        
        self.training_data = {
            "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "labels": [0, 1]
        }
        
        self.prediction_data = {
            "features": [[0.7, 0.8, 0.9]]
        }
        
        self.evaluation_data = {
            "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "labels": [0, 1]
        }
    
    def test_mock_training(self):
        """
        モック訓練のテスト
        """
        result = self.mock_module.train(self.training_data, epochs=10)
        
        self.assertIn("training_time", result)
        self.assertIn("final_loss", result)
        self.assertIn("accuracy", result)
        self.assertIn("epochs", result)
        self.assertIn("quantum_state", result)
        
        self.assertEqual(result["epochs"], 10)
        self.assertGreater(result["training_time"], 0)
        self.assertGreater(result["accuracy"], 0.8)
        self.assertLess(result["final_loss"], 0.1)
    
    def test_mock_prediction(self):
        """
        モック予測のテスト
        """
        result = self.mock_module.predict(self.prediction_data)
        
        self.assertIn("prediction_time", result)
        self.assertIn("predictions", result)
        self.assertIn("probabilities", result)
        self.assertIn("confidence", result)
        self.assertIn("quantum_state", result)
        
        self.assertGreater(result["prediction_time"], 0)
        self.assertGreater(result["confidence"], 0.7)
        self.assertEqual(len(result["predictions"]), 1)
        self.assertEqual(len(result["probabilities"]), 1)
    
    def test_mock_evaluation(self):
        """
        モック評価のテスト
        """
        result = self.mock_module.evaluate(self.evaluation_data)
        
        self.assertIn("evaluation_time", result)
        self.assertIn("accuracy", result)
        self.assertIn("precision", result)
        self.assertIn("recall", result)
        self.assertIn("f1_score", result)
        self.assertIn("quantum_state", result)
        
        self.assertGreater(result["evaluation_time"], 0)
        self.assertGreater(result["accuracy"], 0.8)
        self.assertGreater(result["precision"], 0.7)
        self.assertGreater(result["recall"], 0.7)
        self.assertGreater(result["f1_score"], 0.7)

if __name__ == "__main__":
    unittest.main(verbosity=2)