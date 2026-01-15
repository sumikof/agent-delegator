# ブロックチェーンAI統合テスト

import unittest
from blockchain_ai.interface.blockchain_agent_adapter import (
    BlockchainAgentAdapter, 
    MockBlockchainAIModule,
    AgentTask, 
    AgentTaskType
)

class TestBlockchainAIAdapter(unittest.TestCase):
    """ブロックチェーンAIアダプタのテスト"""
    
    def setUp(self):
        """テストのセットアップ"""
        self.blockchain_ai = MockBlockchainAIModule()
        self.adapter = BlockchainAgentAdapter(self.blockchain_ai)
    
    def test_training_task(self):
        """訓練タスクのテスト"""
        training_task = AgentTask(
            task_id="test_train_001",
            type=AgentTaskType.BLOCKCHAIN_TRAINING,
            data={
                "features": [[0.1, 0.2], [0.3, 0.4]],
                "labels": [0, 1],
                "blockchain_encoding": "smart_contract"
            },
            config={"epochs": 10}
        )
        
        result = self.adapter.execute_blockchain_task(training_task)
        
        # 結果の検証
        self.assertEqual(result.task_id, "test_train_001")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.result)
        self.assertIsNotNone(result.metrics)
        self.assertIn("training_time", result.metrics)
        self.assertIn("accuracy", result.metrics)
    
    def test_prediction_task(self):
        """予測タスクのテスト"""
        prediction_task = AgentTask(
            task_id="test_predict_001",
            type=AgentTaskType.BLOCKCHAIN_PREDICTION,
            data={
                "features": [[0.5, 0.6]],
                "blockchain_encoding": "smart_contract"
            }
        )
        
        result = self.adapter.execute_blockchain_task(prediction_task)
        
        # 結果の検証
        self.assertEqual(result.task_id, "test_predict_001")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.result)
        self.assertIsNotNone(result.metrics)
        self.assertIn("prediction_time", result.metrics)
        self.assertIn("confidence", result.metrics)
    
    def test_evaluation_task(self):
        """評価タスクのテスト"""
        evaluation_task = AgentTask(
            task_id="test_evaluate_001",
            type=AgentTaskType.BLOCKCHAIN_EVALUATION,
            data={
                "features": [[0.1, 0.2], [0.3, 0.4]],
                "labels": [0, 1],
                "blockchain_encoding": "smart_contract"
            }
        )
        
        result = self.adapter.execute_blockchain_task(evaluation_task)
        
        # 結果の検証
        self.assertEqual(result.task_id, "test_evaluate_001")
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.result)
        self.assertIsNotNone(result.metrics)
        self.assertIn("evaluation_time", result.metrics)
        self.assertIn("accuracy", result.metrics)
        self.assertIn("precision", result.metrics)
        self.assertIn("recall", result.metrics)
        self.assertIn("f1_score", result.metrics)
    
    def test_task_history(self):
        """タスク履歴のテスト"""
        # 複数のタスクを実行
        training_task = AgentTask(
            task_id="history_train_001",
            type=AgentTaskType.BLOCKCHAIN_TRAINING,
            data={"features": [[0.1]], "labels": [0], "blockchain_encoding": "test"},
            config={"epochs": 5}
        )
        
        prediction_task = AgentTask(
            task_id="history_predict_001",
            type=AgentTaskType.BLOCKCHAIN_PREDICTION,
            data={"features": [[0.2]], "blockchain_encoding": "test"}
        )
        
        self.adapter.execute_blockchain_task(training_task)
        self.adapter.execute_blockchain_task(prediction_task)
        
        # タスク履歴の検証
        history = self.adapter.get_task_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["task_id"], "history_train_001")
        self.assertEqual(history[1]["task_id"], "history_predict_001")
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なタスクタイプのテスト
        invalid_task = AgentTask(
            task_id="invalid_task_001",
            type="INVALID_TYPE",  # 無効なタスクタイプ
            data={"features": [[0.1]]}
        )
        
        # このタスクはエラーになるはず
        result = self.adapter.execute_blockchain_task(invalid_task)
        self.assertEqual(result.status, "error")
        self.assertIsNotNone(result.error)

if __name__ == "__main__":
    unittest.main()