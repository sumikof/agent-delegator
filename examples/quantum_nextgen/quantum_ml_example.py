#!/usr/bin/env python3
"""
次世代量子機械学習の使用例

量子機械学習アダプタの使用方法を示します。
"""

import json
import logging
from orchestrator.quantum.nextgen.quantum_ml_adapter import QuantumMLAdapter, QuantumMLConfig

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """量子機械学習の使用例"""
    
    print("次世代量子機械学習の使用例")
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
    
    print(f"設定: {json.dumps(config.__dict__, indent=2)}")
    
    # 2. 量子機械学習アダプタの作成
    print("\n2. 量子機械学習アダプタの作成")
    print("-" * 50)
    
    adapter = QuantumMLAdapter(config)
    print("量子機械学習アダプタの作成に成功")
    
    # 3. ステータスの確認
    print("\n3. ステータスの確認")
    print("-" * 50)
    
    status = adapter.get_status()
    print(f"ステータス: {json.dumps(status, indent=2)}")
    
    # 4. 初期化
    print("\n4. 初期化")
    print("-" * 50)
    
    if adapter.initialize():
        print("量子機械学習アダプタの初期化に成功")
        
        # 初期化後のステータス確認
        status = adapter.get_status()
        print(f"初期化後のステータス: {json.dumps(status, indent=2)}")
    else:
        print("量子機械学習アダプタの初期化に失敗")
        return
    
    # 5. モデルの訓練
    print("\n5. モデルの訓練")
    print("-" * 50)
    
    # モックデータの準備
    X_train = [
        [0.1, 0.2, 0.3, 0.4],
        [0.2, 0.3, 0.4, 0.5],
        [0.3, 0.4, 0.5, 0.6],
        [0.4, 0.5, 0.6, 0.7],
        [0.5, 0.6, 0.7, 0.8],
        [0.6, 0.7, 0.8, 0.9],
        [0.7, 0.8, 0.9, 1.0],
        [0.8, 0.9, 1.0, 1.1]
    ]
    y_train = [0, 0, 0, 1, 1, 1, 1, 1]  # バイナリ分類
    
    print(f"訓練データ: {len(X_train)} サンプル")
    print(f"特徴量: {len(X_train[0])} 次元")
    print(f"クラス: {set(y_train)}")
    
    train_result = adapter.train(X_train, y_train)
    print(f"訓練結果: {json.dumps(train_result, indent=2)}")
    
    # 6. モデルの評価
    print("\n6. モデルの評価")
    print("-" * 50)
    
    # モックデータの準備
    X_test = [
        [0.15, 0.25, 0.35, 0.45],
        [0.25, 0.35, 0.45, 0.55],
        [0.45, 0.55, 0.65, 0.75],
        [0.55, 0.65, 0.75, 0.85]
    ]
    y_test = [0, 0, 1, 1]
    
    print(f"テストデータ: {len(X_test)} サンプル")
    
    evaluate_result = adapter.evaluate(X_test, y_test)
    print(f"評価結果: {json.dumps(evaluate_result, indent=2)}")
    
    # 7. モデルの予測
    print("\n7. モデルの予測")
    print("-" * 50)
    
    predict_result = adapter.predict(X_test)
    print(f"予測結果: {json.dumps(predict_result, indent=2)}")
    
    # 8. 実世界データでの使用例
    print("\n8. 実世界データでの使用例")
    print("-" * 50)
    
    # 実世界データの例（仮想データ）
    real_world_data = [
        [0.1, 0.2, 0.3, 0.4],  # サンプル1
        [0.8, 0.9, 1.0, 1.1],  # サンプル2
        [0.3, 0.4, 0.5, 0.6],  # サンプル3
        [0.6, 0.7, 0.8, 0.9]   # サンプル4
    ]
    
    print(f"実世界データ: {len(real_world_data)} サンプル")
    
    real_world_predictions = adapter.predict(real_world_data)
    print(f"実世界データの予測: {json.dumps(real_world_predictions, indent=2)}")
    
    # 9. パフォーマンス分析
    print("\n9. パフォーマンス分析")
    print("-" * 50)
    
    print(f"モデルの精度: {evaluate_result['accuracy']:.2%}")
    print(f"モデルの精度（Precision）: {evaluate_result['precision']:.2%}")
    print(f"モデルの再現率（Recall）: {evaluate_result['recall']:.2%}")
    print(f"モデルのF1スコア: {evaluate_result['f1_score']:.2%}")
    print(f"訓練の損失: {train_result['loss']:.4f}")
    print(f"訓練の反復回数: {train_result['iterations']}")
    
    # 10. 量子機械学習の利点
    print("\n10. 量子機械学習の利点")
    print("-" * 50)
    
    print("量子機械学習の主な利点:")
    print("• 高次元データの効率的な処理")
    print("• 量子並列性による高速な計算")
    print("• 量子重ね合わせによる複雑なパターンの認識")
    print("• 量子干渉によるノイズ耐性の向上")
    print("• ハイブリッドアプローチによる古典的AIとの相乗効果")
    
    print("\n量子機械学習の使用例を完了しました！")
    print("量子AI統合のさらなる深化を目指します！ :rocket:")


if __name__ == "__main__":
    main()