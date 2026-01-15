# ブロックチェーンAI統合の使用例

from blockchain_ai.interface.blockchain_agent_adapter import (
    BlockchainAgentAdapter, 
    MockBlockchainAIModule,
    AgentTask, 
    AgentTaskType
)

def main():
    """ブロックチェーンAI統合の使用例"""
    
    print("🚀 ブロックチェーンAI統合の使用例")
    print("=" * 50)
    
    # モックブロックチェーンAIモジュールを作成
    blockchain_ai = MockBlockchainAIModule()
    
    # アダプタを作成
    adapter = BlockchainAgentAdapter(blockchain_ai)
    
    print("1. ブロックチェーンAIモデルの訓練")
    print("-" * 50)
    
    # 訓練タスクを作成
    training_task = AgentTask(
        task_id="blockchain_train_demo",
        type=AgentTaskType.BLOCKCHAIN_TRAINING,
        data={
            "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
            "labels": [0, 1, 0],
            "blockchain_encoding": "smart_contract",
            "dataset_name": "financial_transactions"
        },
        config={"epochs": 30}
    )
    
    # 訓練タスクを実行
    training_result = adapter.execute_blockchain_task(training_task)
    print(f"訓練タスクID: {training_result.task_id}")
    print(f"ステータス: {training_result.status}")
    print(f"訓練時間: {training_result.metrics['training_time']:.4f}秒")
    print(f"精度: {training_result.metrics['accuracy']:.4f}")
    print(f"最終損失: {training_result.metrics['final_loss']:.4f}")
    print()
    
    print("2. ブロックチェーンAIモデルによる予測")
    print("-" * 50)
    
    # 予測タスクを作成
    prediction_task = AgentTask(
        task_id="blockchain_predict_demo",
        type=AgentTaskType.BLOCKCHAIN_PREDICTION,
        data={
            "features": [[0.15, 0.25, 0.35], [0.45, 0.55, 0.65]],
            "blockchain_encoding": "smart_contract",
            "request_id": "prediction_request_001"
        }
    )
    
    # 予測タスクを実行
    prediction_result = adapter.execute_blockchain_task(prediction_task)
    print(f"予測タスクID: {prediction_result.task_id}")
    print(f"ステータス: {prediction_result.status}")
    print(f"予測時間: {prediction_result.metrics['prediction_time']:.4f}秒")
    print(f"信頼度: {prediction_result.metrics['confidence']:.4f}")
    print(f"予測結果: {prediction_result.result['blockchain_result']['predictions']}")
    print()
    
    print("3. ブロックチェーンAIモデルの評価")
    print("-" * 50)
    
    # 評価タスクを作成
    evaluation_task = AgentTask(
        task_id="blockchain_evaluate_demo",
        type=AgentTaskType.BLOCKCHAIN_EVALUATION,
        data={
            "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "labels": [0, 1],
            "blockchain_encoding": "smart_contract",
            "test_set": "validation_data"
        }
    )
    
    # 評価タスクを実行
    evaluation_result = adapter.execute_blockchain_task(evaluation_task)
    print(f"評価タスクID: {evaluation_result.task_id}")
    print(f"ステータス: {evaluation_result.status}")
    print(f"評価時間: {evaluation_result.metrics['evaluation_time']:.4f}秒")
    print(f"精度: {evaluation_result.metrics['accuracy']:.4f}")
    print(f"適合率: {evaluation_result.metrics['precision']:.4f}")
    print(f"再現率: {evaluation_result.metrics['recall']:.4f}")
    print(f"F1スコア: {evaluation_result.metrics['f1_score']:.4f}")
    print()
    
    print("4. タスク履歴の表示")
    print("-" * 50)
    
    # タスク履歴を取得
    task_history = adapter.get_task_history()
    print(f"実行されたタスク数: {len(task_history)}")
    
    for i, task in enumerate(task_history, 1):
        print(f"タスク {i}:")
        print(f"  ID: {task['task_id']}")
        print(f"  タイプ: {task['task_type']}")
        print(f"  ステータス: {task['status']}")
        print(f"  タイムスタンプ: {task['timestamp']}")
        if task['error']:
            print(f"  エラー: {task['error']}")
        print()
    
    print("🎉 ブロックチェーンAI統合のデモが完了しました！")
    print("ブロックチェーン技術とAIエージェントの統合が正常に動作しています。")

if __name__ == "__main__":
    main()