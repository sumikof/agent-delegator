# エージェント委譲オーケストレーションシステム

OpenHands SDKを使用した仮想開発組織のためのマルチエージェントオーケストレーションシステム。

## 概要

このシステムは、ソフトウェア開発プロジェクトで複数のAIエージェントが協力して作業できるように、設定駆動型のフレームワークを提供します。エージェントは、定義されたステージ、責任、および品質ゲートを持つワークフローに組織されます。

## 目次

- [インストール](#installation)
- [使用方法](#usage)
- [設定ファイル](#configuration-files)
- [YAMLファイルガイド（日本語）](#yaml-files-guide-japanese)
  - [1. ワークフロースキーマ](#1-ワークフロースキーマ)
  - [2. エージェントインターフェース](#2-エージェントインターフェース)
  - [3. ウェブフルスタックテンプレート](#3-ウェブフルスタックテンプレート)
  - [4. 言語ポリシー](#4-言語ポリシー)
  - [5. ファイルポリシー](#5-ファイルポリシー)
  - [YAMLファイルの共通ルール](#yamlファイルの共通ルール)
  - [CLIコマンドでYAMLを検証](#cliコマンドでyamlを検証)
  - [カスタマイズ方法](#カスタマイズ方法)
  - [トラブルシューティング](#トラブルシューティング)
  - [ベストプラクティス](#ベストプラクティス)
- [開発](#development)
- [アーキテクチャ](#architecture)
- [設計原則](#design-principles)
- [参考資料](#references)
- [バージョン](#version)

## インストール

### Python仮想環境の使用

```bash
# 仮想環境をアクティベート
source .venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

## 使用方法

### CLIコマンド

CLIはPythonモジュール構文を使用して実行できます：

```bash
python -m orchestrator.cli [COMMAND] [OPTIONS]
```

または、提供されているラッパースクリプトを使用します：

```bash
./agent-delegate [COMMAND] [OPTIONS]
```

#### 利用可能なコマンド

**1. ワークフロー設定の検証**
```bash
python -m orchestrator.cli validate <workflow-file>
python -m orchestrator.cli validate templates/web-fullstack.yaml
python -m orchestrator.cli validate my-workflow.yaml --verbose
```

**2. ワークフロー構造の表示**
```bash
python -m orchestrator.cli show <workflow-file>
python -m orchestrator.cli show templates/web-fullstack.yaml
python -m orchestrator.cli show templates/web-fullstack.yaml --format=json
```

**3. 利用可能なテンプレートのリスト**
```bash
python -m orchestrator.cli list-templates
```

**4. テンプレートの詳細を表示**
```bash
python -m orchestrator.cli info <template-name>
python -m orchestrator.cli info web-fullstack
```

**5. バージョンを表示**
```bash
python -m orchestrator.cli --version
```

### 実行例

```
$ python -m orchestrator.cli show templates/web-fullstack.yaml

ワークフロー設定: Webフルスタックプロジェクト
============================================================

プロジェクトの詳細:
  名前: Webフルスタックプロジェクト
  タイプ: web
  説明: APIバックエンドとフロントエンドを持つフルスタックWebアプリケーション

エージェントテンプレート:
  ✓ core
  ✓ quality
  ✓ web-development

ワークフローステージ (7):
  1. intake [sequential]
     → client-liaison
  2. requirements-audit [sequential]
     → requirements-auditor
  ...
```

## プロジェクト構造

```
agent-delegate/
├── orchestrator/               # メインパッケージ
│   ├── config/                # 設定の読み込みと検証
│   │   ├── loader.py         # YAMLワークフローローダー
│   │   ├── validator.py      # JSONスキーマバリデーター
│   │   └── models.py         # Pydanticデータモデル
│   ├── display/              # 出力フォーマット
│   │   └── formatter.py      # ワークフローフォーマッター
│   ├── utils/                # ユーティリティと定数
│   │   └── constants.py      # 列挙型と定数
│   └── cli.py                # CLIアプリケーション
├── schemas/                   # JSONスキーマ定義
│   ├── workflow-schema.yaml  # ワークフロー設定スキーマ
│   └── agent-interface.yaml  # エージェントインターフェーススキーマ
├── templates/                 # ビルトインワークフローテンプレート
│   └── web-fullstack.yaml    # Webフルスタックテンプレート
├── policies/                  # システムポリシー
│   ├── language-policy.yaml  # 言語使用ルール
│   └── file-policy.yaml      # ファイル操作ルール
└── tests/                     # ユニットテスト
```

## 設定ファイル

### ワークフロー設定

ワークフローは、`schemas/workflow-schema.yaml`のスキーマに従ってYAMLファイルで定義されます：

```yaml
version: "1.0"
project:
  name: "My Project"
  type: web
  description: "Project description"

agents:
  include_templates:
    - core
    - web-development

workflow:
  stages:
    - name: "planning"
      agents: ["planner"]
      execution_mode: sequential
      gate:
        required_status: OK
```

### 利用可能なテンプレート

- **web-fullstack**: フルスタックWebアプリケーション（7ステージ、14エージェント）
  - 含まれる内容：顧客連絡、要件監査、API設計、並列BE/FE実装、レビュー/QA、統合

今後のイテレーションで追加予定のテンプレート：モバイル、インフラ、データパイプライン

## YAML Files Guide (Japanese)

### 1. ワークフロースキーマ (`schemas/workflow-schema.yaml`)

**目的**: プロジェクトワークフローの構造を定義するJSONスキーマ

**主な構成要素**:
- `version`: スキーマバージョン (例: "1.0")
- `project`: プロジェクト情報 (名前、タイプ、説明、言語ポリシー)
- `agents`: エージェント設定 (テンプレート、カスタムエージェント、除外エージェント)
- `workflow`: ワークフロー定義 (ステージ、エラーハンドリング、タイムアウト)

**使用方法**:
1. 新しいワークフローを作成する際のテンプレートとして使用
2. ワークフローYAMLファイルのバリデーションに使用
3. 必須フィールドと許容値を定義

**例**:
```yaml
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

### 2. エージェントインターフェース (`schemas/agent-interface.yaml`)

**目的**: すべてのエージェントが実装する必要があるインターフェースを定義

**主な構成要素**:
- `id`: 一意の識別子 (kebab-case)
- `name`: 表示名
- `role`: 役割カテゴリ (liaison, planning, audit, etc.)
- `description`: エージェントの目的
- `capabilities`: エージェントが実行できるアクション
- `responsibilities`: 必須/禁止/許可アクション
- `boundaries`: ファイル操作の制限
- `language_policy`: 言語設定
- `escalation`: エスカレーションパス
- `timeout_ms`: タイムアウト設定
- `retry_policy`: リトライポリシー
- `inputs/outputs`: 入出力スキーマ
- `hooks`: ライフサイクルフック

**使用方法**:
1. 新しいエージェントを作成する際のテンプレート
2. エージェント間の一貫性を確保
3. エージェントの能力と制限を明確化

**例**:
```yaml
id: "backend-dev"
name: "Backend Developer"
role: "implementation"
description: "Implements backend services and APIs"
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

### 3. ウェブフルスタックテンプレート (`templates/web-fullstack.yaml`)

**目的**: ウェブアプリケーション開発のための事前定義されたワークフロー

**主な構成要素**:
- 7つのステージ: intake, requirements-audit, planning, contract, implementation, review-qa, integration
- エージェントテンプレート: core, quality, web-development
- 言語ポリシー: 顧客向けは日本語、開発は英語
- エラーハンドリング: リトライポリシー、サーキットブレーカー、フォールバック戦略

**使用方法**:
1. ウェブプロジェクトの開始テンプレートとして使用
2. 必要に応じてカスタマイズ
3. CLIコマンドで検証: `python -m orchestrator.cli validate templates/web-fullstack.yaml`

**例**:
```yaml
# ウェブプロジェクトの基本構造
version: "1.0"
project:
  name: "Web Fullstack Project"
  type: web
  description: "Full-stack web application with API backend and frontend"

agents:
  include_templates:
    - core
    - quality
    - web-development

workflow:
  stages:
    - name: "intake"
      agents: ["client-liaison"]
      execution_mode: sequential
    - name: "implementation"
      agents: ["backend-dev", "frontend-dev"]
      execution_mode: parallel
```

### 4. 言語ポリシー (`policies/language-policy.yaml`)

**目的**: エージェント間の言語使用ルールを定義

**主な構成要素**:
- `global_defaults`: 全エージェントに適用されるデフォルト設定
- `agent_overrides`: エージェントごとの言語設定
- `translation_rules`: 言語間翻訳のルール
- `content_guidelines`: 言語ごとのコンテンツガイドライン
- `validation_rules`: ポリシー遵守の検証ルール

**使用方法**:
1. エージェントの言語設定を統一
2. 顧客と開発チーム間のコミュニケーションを明確化
3. コード、ドキュメント、エラーメッセージの言語を標準化

**例**:
```yaml
global_defaults:
  customer_facing: "ja"
  internal_development: "en"
  code_comments: "en"
  commit_messages: "en"

agent_overrides:
  client-liaison:
    customer_facing: "ja"
    internal_development: "ja"
  backend-dev:
    all: "en"
```

### 5. ファイルポリシー (`policies/file-policy.yaml`)

**目的**: ファイル操作のルールと制限を定義

**主な構成要素**:
- `backup`: バックアップファイルの禁止
- `atomic_operations`: アトミックなファイル操作
- `naming_conventions`: ファイル命名規則 (kebab-case)
- `forbidden_files`: 修正禁止ファイル
- `logging`: ファイル操作のログ設定
- `workspace_structure`: 標準ディレクトリ構造
- `cleanup`: 自動クリーンアップルール
- `version_control`: Git統合設定
- `permissions`: ファイルパーミッション

**使用方法**:
1. ワークスペースの整理と標準化
2. 機密情報の保護
3. エージェントによるファイル操作の制御

**例**:
```yaml
backup:
  enabled: false
  reason: "Git history provides version control"

naming_conventions:
  files:
    case: "kebab-case"
    max_length: 100
    allowed_characters: "a-z0-9-_."

forbidden_files:
  secrets:
    patterns:
      - ".env"
      - "*.secret"
    action: "block"
```

## YAMLファイルの共通ルール

1. **インデント**: スペース2つを使用 (タブ禁止)
2. **命名規則**: kebab-case (小文字とハイフン)
3. **コメント**: `#` で始める
4. **文字コード**: UTF-8
5. **行末**: LF (WindowsのCRLF禁止)
6. **バックアップファイル**: 作成禁止 (Gitで管理)

## CLIコマンドでYAMLを検証

```bash
# ワークフローファイルを検証
python -m orchestrator.cli validate my-workflow.yaml

# テンプレートを表示
python -m orchestrator.cli show templates/web-fullstack.yaml

# 利用可能なテンプレートをリスト
python -m orchestrator.cli list-templates
```

## カスタマイズ方法

1. **テンプレートをベースに新規作成**:
   ```bash
   cp templates/web-fullstack.yaml my-project.yaml
   ```

2. **必要な部分を編集**:
   - プロジェクト名と説明
   - 言語ポリシー
   - エージェントテンプレート
   - ワークフローステージ

3. **検証**:
   ```bash
   python -m orchestrator.cli validate my-project.yaml
   ```

4. **実行**:
   ```bash
   python -m orchestrator.cli run my-project.yaml
   ```

## トラブルシューティング

**エラー**: `Invalid YAML syntax`
- 解決: インデントや構文を確認
- ツール: `yamllint` を使用

**エラー**: `Schema validation failed`
- 解決: 必須フィールドが抜けていないか確認
- ツール: `python -m orchestrator.cli validate --verbose file.yaml`

**エラー**: `Agent not found`
- 解決: エージェントIDが正しいか、テンプレートが含まれているか確認

## ベストプラクティス

1. **小さく始めて徐々に拡張**: 最小限の設定から始め、必要に応じて追加
2. **テンプレートを活用**: 既存のテンプレートをベースにカスタマイズ
3. **検証を忘れずに**: 変更後は必ず検証コマンドを実行
4. **バージョン管理**: Gitで管理し、変更履歴を残す
5. **ドキュメント**: コメントを活用して設定の意図を明確化

## 開発

### テストの実行

```bash
# 開発依存関係をインストール
pip install -r requirements-dev.txt

# テストを実行
pytest tests/ -v

# カバレッジ付きで実行
pytest tests/ --cov=orchestrator --cov-report=html
```

### コード品質

```bash
# コードをフォーマット
black orchestrator/ tests/

# リント
ruff check orchestrator/ tests/

# 型チェック
mypy orchestrator/
```

## アーキテクチャ

この実装（イテレーション1）では以下を提供します：
- ✓ YAMLファイルからの設定読み込み
- ✓ JSONスキーマ検証
- ✓ Pydanticモデル検証
- ✓ 検証と表示のためのCLIインターフェース
- ✓ テンプレートシステム

今後のイテレーションで追加予定：
- オーケストレーションエンジン（ワークフロー実行）
- OpenHands SDK統合（エージェント生成）
- 状態管理
- コンテキスト管理
- エラーハンドリング実装
- ロギングインフラストラクチャ

## 設計原則

1. **設定駆動**：すべてのワークフローをYAMLで定義
2. **型安全**：検証のためのPydanticモデル
3. **段階的**：最小限の機能から開始
4. **拡張可能**：将来の機能のための明確な拡張ポイント

## 参考資料

- 設計ドキュメント：`agent-delegation.md`
- プロジェクトガイド：`CLAUDE.md`
- スキーマ：`schemas/`
- 実装計画：`.claude/plans/linked-toasting-quiche.md`

## バージョン

現在のバージョン：0.1.0（イテレーション1）
