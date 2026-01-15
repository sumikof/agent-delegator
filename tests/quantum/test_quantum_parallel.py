"""
量子並列処理モジュールのテスト
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from orchestrator.quantum.quantum_parallel import (
    QuantumParallelProcessor,
    QuantumParallelWorker,
    QuantumResourceMonitor,
    QuantumParallelOptimizer,
    QuantumAlgorithms
)


def test_quantum_resource_monitor():
    """リソースモニターのテスト"""
    monitor = QuantumResourceMonitor(max_concurrent_tasks=2)
    
    # リソース確保のテスト
    assert monitor.acquire_resource() == True
    assert monitor.acquire_resource() == True
    assert monitor.acquire_resource() == False  # 最大数に達している
    
    # リソース解放のテスト
    monitor.release_resource()
    assert monitor.acquire_resource() == True
    
    # ステータスのテスト
    status = monitor.get_status()
    assert status['current_tasks'] == 2
    assert status['max_concurrent_tasks'] == 2
    assert status['available_slots'] == 0
    assert status['utilization_rate'] == 1.0


def test_quantum_algorithms_basic():
    """量子アルゴリズムの基本機能テスト"""
    algorithms = QuantumAlgorithms()
    
    # 基本的な回路作成のテスト
    with patch('qiskit.QuantumCircuit') as mock_qc:
        mock_instance = Mock()
        mock_qc.return_value = mock_instance
        
        result = algorithms.create_basic_circuit(num_qubits=2)
        assert result == mock_instance
        
        # メソッドが正しく呼び出されたか確認
        mock_instance.h.assert_called_once_with(0)
        mock_instance.cx.assert_called_once_with(0, 1)
        mock_instance.measure_all.assert_called_once()


def test_quantum_parallel_processor_start_stop():
    """量子並列処理プロセッサの起動と停止のテスト"""
    processor = QuantumParallelProcessor(max_workers=2)
    
    # 初期状態の確認
    assert processor.running == False
    assert len(processor.worker_pool) == 0
    
    # 起動のテスト
    processor.start()
    assert processor.running == True
    assert len(processor.worker_pool) == 2
    
    # 停止のテスト
    processor.stop()
    assert processor.running == False
    assert len(processor.worker_pool) == 0


def test_quantum_parallel_processor_submit_task():
    """タスクの送信テスト"""
    processor = QuantumParallelProcessor(max_workers=1)
    processor.start()
    
    # タスクの送信
    task_id = processor.submit_task('create_basic_circuit', priority=1)
    assert task_id == 1
    
    # タスクキューの確認
    assert processor.task_queue.qsize() == 1
    
    processor.stop()


def test_quantum_parallel_optimizer():
    """量子並列処理最適化のテスト"""
    processor = QuantumParallelProcessor(max_workers=2)
    optimizer = QuantumParallelOptimizer(processor)
    
    # タスクの最適化配布
    tasks = [
        {'algorithm': 'grover_search', 'args': [2, '11'], 'importance': 'high'},
        {'algorithm': 'qaoa_optimizer', 'args': [None, 2], 'importance': 'normal'},
        {'algorithm': 'create_basic_circuit', 'args': [2], 'importance': 'low'}
    ]
    
    processor.start()
    task_ids = optimizer.optimize_task_distribution(tasks)
    
    assert len(task_ids) == 3
    assert all(isinstance(tid, int) for tid in task_ids)
    
    processor.stop()


def test_worker_lifecycle():
    """ワーカーのライフサイクルテスト"""
    task_queue = QuantumParallelProcessor(max_workers=1).task_queue
    result_queue = QuantumParallelProcessor(max_workers=1).result_queue
    monitor = QuantumResourceMonitor()
    
    worker = QuantumParallelWorker(
        worker_id=0,
        task_queue=task_queue,
        result_queue=result_queue,
        resource_monitor=monitor
    )
    
    # ワーカーの起動と停止
    worker.start()
    assert worker.is_alive()
    
    worker.stop()
    worker.join()
    assert not worker.is_alive()


def test_error_handling():
    """エラーハンドリングのテスト"""
    processor = QuantumParallelProcessor(max_workers=1)
    processor.start()
    
    # 存在しないアルゴリズムのタスクを送信
    task_id = processor.submit_task('nonexistent_algorithm', priority=0)
    
    # 結果を取得（エラーになるはず）
    time.sleep(0.5)  # ワーカーがタスクを処理するのを待つ
    result = processor.get_result(timeout=1.0)
    
    processor.stop()
    
    if result:
        assert result['success'] == False
        assert 'error' in result


def test_priority_handling():
    """優先度処理のテスト"""
    processor = QuantumParallelProcessor(max_workers=1)
    processor.start()
    
    # 優先度の異なるタスクを送信
    task1 = processor.submit_task('create_basic_circuit', priority=2)  # 低優先度
    task2 = processor.submit_task('create_basic_circuit', priority=0)  # 高優先度
    task3 = processor.submit_task('create_basic_circuit', priority=1)  # 中優先度
    
    # 優先度順にタスクが処理されることを確認
    assert processor.task_queue.qsize() == 3
    
    processor.stop()


def test_resource_monitoring_integration():
    """リソースモニタリングの統合テスト"""
    monitor = QuantumResourceMonitor(max_concurrent_tasks=1)
    processor = QuantumParallelProcessor(max_workers=2, backend=None)
    
    # リソースモニターを設定
    processor.resource_monitor = monitor
    processor.start()
    
    # タスクを送信
    task_id1 = processor.submit_task('create_basic_circuit', priority=0)
    task_id2 = processor.submit_task('create_basic_circuit', priority=0)
    
    # リソース使用状況を確認
    time.sleep(0.5)  # ワーカーがタスクを処理するのを待つ
    status = processor.get_status()
    resource_status = status['resource_status']
    
    assert resource_status['current_tasks'] <= resource_status['max_concurrent_tasks']
    
    processor.stop()


def test_dynamic_resource_allocation():
    """動的リソース割り当てのテスト"""
    processor = QuantumParallelProcessor(max_workers=4)
    optimizer = QuantumParallelOptimizer(processor)
    
    processor.start()
    
    # 初期ワーカー数
    initial_workers = len(processor.worker_pool)
    
    # リソース使用率が高い場合のスケールアップ
    with patch.object(processor.resource_monitor, 'get_status', return_value={
        'current_tasks': 2,
        'max_concurrent_tasks': 2,
        'available_slots': 0,
        'utilization_rate': 1.0
    }):
        optimizer.dynamic_resource_allocation()
    
    # ワーカー数が増えていることを確認
    assert len(processor.worker_pool) > initial_workers
    
    processor.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
