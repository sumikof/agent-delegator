# YAML Files Setup Guide (Japanese) - Step by Step

このガイドでは、エージェント委譲オーケストレーションシステムで使用されるYAMLファイルの設定方法をステップバイステップで説明します。

## 目次

- [1. 事前準備](#1-事前準備)
- [2. ワークフロースキーマの設定 (`schemas/workflow-schema.yaml`)](#2-ワークフロースキーマの設定-schemasworkflow-schemayaml)
- [3. エージェントインターフェースの設定 (`schemas/agent-interface.yaml`)](#3-エージェントインターフェースの設定-schemasagent-interfaceyaml)
- [4. ウェブフルスタックテンプレートの設定 (`templates/web-fullstack.yaml`)](#4-ウェブフルスタックテンプレートの設定-templatesweb-fullstackyaml)
- [5. 言語ポリシーの設定 (`policies/language-policy.yaml`)](#5-言語ポリシーの設定-policieslanguage-policyyaml)
- [6. ファイルポリシーの設定 (`policies/file-policy.yaml`)](#6-ファイルポリシーの設定-policiesfile-policyyaml)
- [7. カスタムYAMLファイルの作成](#7-カスタムyamlファイルの作成)
- [8. 検証とテスト](#8-検証とテスト)
- [9. トラブルシューティング](#9-トラブルシューティング)
- [10. ベストプラクティス](#10-ベストプラクティス)

## 1. 事前準備

### 必要なツール
- YAMLエディタ (VS Code, Sublime Textなど)
- Python 3.8+
- OpenHands SDK

### ディレクトリ構造
```bash
project-root/
├── schemas/              # スキーマ定義
├── templates/            # テンプレート
├── policies/             # ポリシーファイル
└── custom/               # カスタムYAMLファイル
```

### 共通ルール
1. **インデント**: スペース2つを使用 (タブ禁止)
2. **命名規則**: kebab-case (小文字とハイフン)
3. **コメント**: `#` で始める
4. **文字コード**: UTF-8
5. **行末**: LF (WindowsのCRLF禁止)

## 2. ワークフロースキーマの設定 (`schemas/workflow-schema.yaml`)

### ステップ1: 基本構造の理解
ワークフロースキーマはJSON Schema形式で、プロジェクトワークフローの構造を定義します。

### ステップ2: 必須フィールドの設定
```yaml
# schemas/workflow-schema.yaml
version: "1.0"
project:
  name: "My Web App"
  type: web
  description: "Customer portal application"
  language_policy:
    customer_facing: "ja"
    development: "en"

agents:
  include_templates:
    - core
    - quality
    - web-development

workflow:
  stages:
    - name: "requirements"
      agents: ["client-liaison"]
      execution_mode: sequential
      gate:
        required_status: OK
```

### ステップ3: 高度な設定
- エラーハンドリングの追加
- カスタムエージェントの定義
- タイムアウト設定

### ステップ4: 検証
```bash
python -m orchestrator.cli validate schemas/workflow-schema.yaml
```

## 3. エージェントインターフェースの設定 (`schemas/agent-interface.yaml`)

### ステップ1: 基本情報の設定
```yaml
# schemas/agent-interface.yaml
id: "backend-dev"
name: "Backend Developer"
role: "implementation"
description: "Implements backend services and APIs"
```

### ステップ2: 能力と責任の定義
```yaml
capabilities:
  - "write_code"
  - "run_tests"
  - "fix_bugs"

responsibilities:
  must_do:
    - "Follow API contract strictly"
    - "Write unit tests"
  must_not_do:
    - "Modify frontend code"
    - "Change database schema without approval"
```

### ステップ3: 言語ポリシーとタイムアウト
```yaml
language_policy:
  all: "en"

timeout_ms: 3600000
retry_policy:
  max_attempts: 3
  backoff_type: "exponential"
```

### ステップ4: 検証
```bash
python -m orchestrator.cli validate schemas/agent-interface.yaml
```

## 4. ウェブフルスタックテンプレートの設定 (`templates/web-fullstack.yaml`)

### ステップ1: テンプレートのコピー
```bash
cp templates/web-fullstack.yaml custom/my-web-project.yaml
```

### ステップ2: 基本情報の編集
```yaml
# custom/my-web-project.yaml
version: "1.0"
project:
  name: "My Web Project"
  type: web
  description: "Full-stack web application with API backend and frontend"
```

### ステップ3: エージェント設定
```yaml
agents:
  include_templates:
    - core
    - quality
    - web-development
```

### ステップ4: ワークフローステージの定義
```yaml
workflow:
  stages:
    - name: "intake"
      agents: ["client-liaison"]
      execution_mode: sequential
    - name: "implementation"
      agents: ["backend-dev", "frontend-dev"]
      execution_mode: parallel
```

### ステップ5: 検証
```bash
python -m orchestrator.cli validate custom/my-web-project.yaml
```

## 5. 言語ポリシーの設定 (`policies/language-policy.yaml`)

### ステップ1: グローバルデフォルトの設定
```yaml
# policies/language-policy.yaml
global_defaults:
  customer_facing: "ja"
  internal_development: "en"
  code_comments: "en"
  commit_messages: "en"
```

### ステップ2: エージェントごとのオーバーライド
```yaml
agent_overrides:
  client-liaison:
    customer_facing: "ja"
    internal_development: "ja"
  backend-dev:
    all: "en"
```

### ステップ3: 検証
```bash
python -m orchestrator.cli validate policies/language-policy.yaml
```

## 6. ファイルポリシーの設定 (`policies/file-policy.yaml`)

### ステップ1: バックアップ設定
```yaml
# policies/file-policy.yaml
backup:
  enabled: false
  reason: "Git history provides version control"
```

### ステップ2: 命名規則
```yaml
naming_conventions:
  files:
    case: "kebab-case"
    max_length: 100
    allowed_characters: "a-z0-9-_."
```

### ステップ3: 禁止ファイルの設定
```yaml
forbidden_files:
  secrets:
    patterns:
      - ".env"
      - "*.secret"
    action: "block"
```

### ステップ4: 検証
```bash
python -m orchestrator.cli validate policies/file-policy.yaml
```

## 7. カスタムYAMLファイルの作成

### ステップ1: テンプレートの選択
```bash
# 利用可能なテンプレートをリスト
python -m orchestrator.cli list-templates

# テンプレートを表示
python -m orchestrator.cli show templates/web-fullstack.yaml
```

### ステップ2: 新規ファイルの作成
```bash
cp templates/web-fullstack.yaml custom/my-custom-project.yaml
```

### ステップ3: 必要な部分を編集
1. プロジェクト名と説明
2. 言語ポリシー
3. エージェントテンプレート
4. ワークフローステージ

### ステップ4: 検証
```bash
python -m orchestrator.cli validate custom/my-custom-project.yaml
```

## 8. 検証とテスト

### CLIコマンド
```bash
# ワークフローファイルを検証
python -m orchestrator.cli validate my-workflow.yaml

# テンプレートを表示
python -m orchestrator.cli show templates/web-fullstack.yaml

# 利用可能なテンプレートをリスト
python -m orchestrator.cli list-templates

# 詳細検証
python -m orchestrator.cli validate --verbose my-workflow.yaml
```

### 自動テスト
```bash
# ユニットテストの実行
python -m pytest tests/unit/

# 統合テストの実行
python -m pytest tests/integration/
```

## 9. トラブルシューティング

### 一般的なエラーと解決方法

**エラー**: `Invalid YAML syntax`
- 解決: インデントや構文を確認
- ツール: `yamllint` を使用

**エラー**: `Schema validation failed`
- 解決: 必須フィールドが抜けていないか確認
- ツール: `python -m orchestrator.cli validate --verbose file.yaml`

**エラー**: `Agent not found`
- 解決: エージェントIDが正しいか、テンプレートが含まれているか確認

**エラー**: `File operation forbidden`
- 解決: ファイルポリシーを確認し、必要な権限を追加

## 10. ベストプラクティス

### ファイル管理
1. **小さく始めて徐々に拡張**: 最小限の設定から始め、必要に応じて追加
2. **テンプレートを活用**: 既存のテンプレートをベースにカスタマイズ
3. **検証を忘れずに**: 変更後は必ず検証コマンドを実行
4. **バージョン管理**: Gitで管理し、変更履歴を残す
5. **ドキュメント**: コメントを活用して設定の意図を明確化

### ワークフロー設計
1. **段階的な開発**: 単純なワークフローから始め、複雑さを徐々に追加
2. **エラーハンドリング**: 適切なエラーハンドリングとフォールバックを設定
3. **パフォーマンス**: タイムアウトとリトライポリシーを適切に設定
4. **セキュリティ**: 機密情報の保護とファイル操作の制限

### チームコラボレーション
1. **標準化**: チーム内で共通のテンプレートとポリシーを使用
2. **ドキュメント**: 設定の意図と変更履歴を文書化
3. **レビュー**: チームメンバーによるレビューとフィードバック
4. **トレーニング**: 新しいチームメンバーへのトレーニングと知識共有