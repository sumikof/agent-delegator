#!/usr/bin/env python3
"""
量子並列処理の使用例

この例は、量子並列処理モジュールの使用方法を示します。
量子アルゴリズムを並列に実行し、リソース管理と優先度付けを行います。
"""

import time
from orchestrator.quantum.quantum_parallel import (
    QuantumParallelProcessor,
    QuantumParallelOptimizer,
    QuantumAlgorithms
)


def main():
    print("量子並列処理の使用例")
    print("=" * 50)
    
    # 量子並列処理プロセッサを作成
    print("1. 量子並列処理プロセッサの作成")
    processor = QuantumParallelProcessor(max_workers=4)
    
    # 量子並列処理最適化クラスを作成
    optimizer = QuantumParallelOptimizer(processor)
    
    # プロセッサを起動
    print("2. プロセッサの起動")
    processor.start()
    
    # タスクを定義
    print("3. タスクの定義")
    tasks = [
        {
            'algorithm': 'create_basic_circuit',
            'args': [2],
            'importance': 'high',
            'description': '基本的な量子回路の作成（高優先度）'
        },
        {
            'algorithm': 'create_basic_circuit', 
            'args': [3],
            'importance': 'normal',
            'description': '基本的な量子回路の作成（通常優先度）'
        },
        {
            'algorithm': 'create_basic_circuit',
            'args': [4], 
            'importance': 'low',
            'description': '基本的な量子回路の作成（低優先度）'
        }
    ]
    
    # タスクを表示
    print("\n定義されたタスク:")
    for i, task in enumerate(tasks, 1):
        print(f"  タスク {i}: {task['description']} (優先度: {task['importance']})")
    
    # タスクを最適化して配布
    print("\n4. タスクの最適化と配布")
    task_ids = optimizer.optimize_task_distribution(tasks)
    
    print(f"配布されたタスクID: {task_ids}")
    
    # プロセッサのステータスを表示
    print("\n5. プロセッサのステータス")
    status = processor.get_status()
    print(f"実行中: {status['running']}")
    print(f"ワーカー数: {status['workers']}")
    print(f"キューにあるタスク数: {status['tasks_queued']}")
    print(f"保留中の結果数: {status['results_pending']}")
    
    # リソースステータスを表示
    resource_status = status['resource_status']
    print(f"\nリソースステータス:")
    print(f"  現在のタスク数: {resource_status['current_tasks']}")
    print(f"  最大同時タスク数: {resource_status['max_concurrent_tasks']}")
    print(f"  利用可能スロット数: {resource_status['available_slots']}")
    print(f"  利用率: {resource_status['utilization_rate']:.2%}")
    
    # 結果を取得
    print("\n6. 結果の取得")
    results = []
    
    # 全ての結果を取得
    while len(results) < len(tasks):
        result = processor.get_result(timeout=2.0)
        if result:
            results.append(result)
            print(f"  タスク {result['task_id']} 完了 (ワーカー {result['worker_id']}, 実行時間: {result['execution_time']:.3f}s)")
        else:
            print("  結果待機中...")
            time.sleep(0.5)
    
    # 結果を表示
    print("\n7. 結果の詳細")
    for result in results:
        print(f"  タスク {result['task_id']}:")
        print(f"    ワーカーID: {result['worker_id']}")
        print(f"    実行時間: {result['execution_time']:.3f}s")
        print(f"    優先度: {result['priority']}")
        if 'error' in result:
            print(f"    エラー: {result['error']}")
        else:
            print(f"    成功: {result.get('success', False)}")
    
    # 動的リソース割り当てのデモンストレーション
    print("\n8. 動的リソース割り当てのデモンストレーション")
    print("リソース使用率に基づいてワーカー数を動的に調整します...")
    
    # リソース使用率が高い場合のシミュレーション
    print("\nリソース使用率が高い場合 (80%):")
    # 実際の動作をシミュレートするために、リソースモニターの状態を変更
    # ここでは単純化のために直接スケールアップを呼び出す
    initial_workers = len(processor.worker_pool)
    print(f"  現在のワーカー数: {initial_workers}")
    
    # スケールアップ
    optimizer._scale_workers('up')
    new_workers = len(processor.worker_pool)
    print(f"  スケールアップ後: {new_workers}")
    
    # リソース使用率が低い場合のシミュレーション
    print("\nリソース使用率が低い場合 (30%):")
    # スケールダウン
    optimizer._scale_workers('down')
    final_workers = len(processor.worker_pool)
    print(f"  スケールダウン後: {final_workers}")
    
    # プロセッサを停止
    print("\n9. プロセッサの停止")
    processor.stop()
    
    print("\n量子並列処理の使用例が完了しました！")
    print("\n主な機能:")
    print("✓ 量子アルゴリズムの並列実行")
    print("✓ タスクの優先度付け")
    print("✓ 動的リソース割り当て")
    print("✓ リソースモニタリング")
    print("✓ エラーハンドリング")


if __name__ == "__main__":
    main()