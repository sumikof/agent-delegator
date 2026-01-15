#!/usr/bin/env python3
"""
量子機械学習アダプタの簡易テスト

量子機械学習アダプタの基本機能をテストします。
"""

import sys
import os

# 現在のディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'orchestrator', 'quantum', 'nextgen'))

from quantum_ml_adapter import QuantumMLAdapter, QuantumMLConfig


def test_quantum_ml_adapter():
    """量子機械学習アダプタのテスト"""
    
    print("量子機械学習アダプタのテスト")
    print("=" * 50)
    
    # 1. 量子機械学習アダプタの設定
    print("\n1. 量子機械学習アダプタの設定")
    print("-" * 50)
    
    config = QuantumMLConfig(
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
    
    print(f"設定: quantum_backend={config.quantum_backend}, num_qubits={config.num_qubits}")
    
    # 2. 量子機械学習アダプタの作成
    print("\n2. 量子機械学習アダプタの作成")
    print("-" * 50)
    
    adapter = QuantumMLAdapter(config)
    print("量子機械学習アダプタの作成に成功")
    
    # 3. ステータスの確認
    print("\n3. ステータスの確認")
    print("-" * 50)
    
    status = adapter.get_status()
    print(f"ステータス: {status['status']}")
    print(f"量子バックエンド: {status['quantum_backend']}")
    print(f"量子ビット数: {status['num_qubits']}")
    
    # 4. 初期化
    print("\n4. 初期化")
    print("-" * 50)
    
    if adapter.initialize():
        print("量子機械学習アダプタの初期化に成功")
        
        # 初期化後のステータス確認
        status = adapter.get_status()
        print(f"初期化後のステータス: {status['status']}")
    else:
        print("量子機械学習アダプタの初期化に失敗")
        return False
    
    # 5. モデルの訓練
    print("\n5. モデルの訓練")
    print("-" * 50)
    
    # モックデータの準備
    X_train = [
        [0.1, 0.2, 0.3, 0.4],
        [0.2, 0.3, 0.4, 0.5],
        [0.3, 0.4, 0.5, 0.6],
        [0.4, 0.5, 0.6, 0.7]
    ]
    y_train = [0, 0, 1, 1]  # バイナリ分類
    
    print(f"訓練データ: {len(X_train)} サンプル")
    
    train_result = adapter.train(X_train, y_train)
    print(f"訓練結果: status={train_result['status']}, accuracy={train_result['accuracy']:.2f}")
    
    # 6. モデルの評価
    print("\n6. モデルの評価")
    print("-" * 50)
    
    # モックデータの準備
    X_test = [
        [0.15, 0.25, 0.35, 0.45],
        [0.45, 0.55, 0.65, 0.75]
    ]
    y_test = [0, 1]
    
    evaluate_result = adapter.evaluate(X_test, y_test)
    print(f"評価結果: status={evaluate_result['status']}, accuracy={evaluate_result['accuracy']:.2f}")
    
    # 7. モデルの予測
    print("\n7. モデルの予測")
    print("-" * 50)
    
    predict_result = adapter.predict(X_test)
    print(f"予測結果: status={predict_result['status']}, predictions={predict_result['predictions']}")
    
    print("\n量子機械学習アダプタのテストを完了しました！")
    return True


if __name__ == "__main__":
    success = test_quantum_ml_adapter()
    if success:
        print("\n全てのテストが成功しました！")
    else:
        print("\nテストに失敗しました。")
        sys.exit(1)