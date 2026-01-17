# ワークフロー実行図

```mermaid
graph LR
    A[開始] --> B[受付]
    B --> C[要件チェック]
    C --> D[計画]
    D --> E[契約]
    E --> F[実装]
    F --> G[レビュー＆QA]
    G --> H[統合]
    H --> I[完了]
    
    G -->|NG| J[進捗再計画]
    J --> F
    
    subgraph "コアエージェント"
    B1[client-liaison] --> B
    C1[requirements-auditor] --> C
    D1[planner] --> D
    E1[api-designer] --> E
    H1[integrator] --> H
    end
    
    subgraph "開発エージェント"
    F1[backend-dev] --> F
    F2[frontend-dev] --> F
    end
    
    subgraph "品質エージェント"
    G1[reviewer-be] --> G
    G2[reviewer-fe] --> G
    G3[tester] --> G
    G4[quality-auditor] --> G
    end
    
    subgraph "進捗管理"
    J1[progress] --> J
    end
```

## ワークフロー実行の説明

この図は、ワークフロー実行プロセスを示しています：

1. **受付**：クライアント連絡が顧客から要件を収集
2. **要件チェック**：要件監査が要件を検証し、あいまいさをチェック
3. **計画**：プランナーが開発計画とタスクの分解を作成
4. **契約**：APIデザイナーがAPI仕様（Single Source of Truth）を作成
5. **実装**：バックエンドとフロントエンドの開発者が並列で作業
6. **レビュー＆QA**：複数の品質エージェントが実装をレビューおよびテスト
7. **統合**：インテグレーターがすべてのコンポーネントを組み合わせて最終検証を実行
8. **進捗再計画**：ステージが失敗した場合（NG）、進捗エージェントが再計画提案を作成

ワークフローは、適切な場所で順次および並列実行の両方をサポートし、自動エラーハンドリングとフォールバックメカニズムを備えています。