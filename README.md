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

YAMLファイルの使用方法については、[YAML_FILES_GUIDE.md](YAML_FILES_GUIDE.md)を参照してください。

このガイドには以下の内容が含まれています：
- ワークフロースキーマの構造と使用方法
- エージェントインターフェースの定義
- ウェブフルスタックテンプレートの使い方
- 言語ポリシーとファイルポリシーの設定
- YAMLファイルの共通ルール
- CLIコマンドでの検証方法
- カスタマイズ方法とベストプラクティス
- トラブルシューティング

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
