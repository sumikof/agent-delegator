# Agent-Delegate Orchestration System

Multi-agent orchestration system using OpenHands SDK for virtual development organizations.

## Overview

This system provides a configuration-driven framework for orchestrating multiple AI agents to work together on software development projects. Agents are organized into workflows with defined stages, responsibilities, and quality gates.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration Files](#configuration-files)
- [YAML Files Guide (Japanese)](#yaml-files-guide-japanese)
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
- [Development](#development)
- [Architecture](#architecture)
- [Design Principles](#design-principles)
- [References](#references)
- [Version](#version)

## Installation

### Using Python Virtual Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Commands

The CLI can be run using Python module syntax:

```bash
python -m orchestrator.cli [COMMAND] [OPTIONS]
```

Or use the provided wrapper script:

```bash
./agent-delegate [COMMAND] [OPTIONS]
```

#### Available Commands

**1. Validate a workflow configuration**
```bash
python -m orchestrator.cli validate <workflow-file>
python -m orchestrator.cli validate templates/web-fullstack.yaml
python -m orchestrator.cli validate my-workflow.yaml --verbose
```

**2. Display workflow structure**
```bash
python -m orchestrator.cli show <workflow-file>
python -m orchestrator.cli show templates/web-fullstack.yaml
python -m orchestrator.cli show templates/web-fullstack.yaml --format=json
```

**3. List available templates**
```bash
python -m orchestrator.cli list-templates
```

**4. Show template details**
```bash
python -m orchestrator.cli info <template-name>
python -m orchestrator.cli info web-fullstack
```

**5. Show version**
```bash
python -m orchestrator.cli --version
```

### Example Output

```
$ python -m orchestrator.cli show templates/web-fullstack.yaml

Workflow Configuration: Web Fullstack Project
============================================================

Project Details:
  Name: Web Fullstack Project
  Type: web
  Description: Full-stack web application with API backend and frontend

Agent Templates:
  ✓ core
  ✓ quality
  ✓ web-development

Workflow Stages (7):
  1. intake [sequential]
     → client-liaison
  2. requirements-audit [sequential]
     → requirements-auditor
  ...
```

## Project Structure

```
agent-delegate/
├── orchestrator/               # Main package
│   ├── config/                # Configuration loading & validation
│   │   ├── loader.py         # YAML workflow loader
│   │   ├── validator.py      # JSON Schema validator
│   │   └── models.py         # Pydantic data models
│   ├── display/              # Output formatting
│   │   └── formatter.py      # Workflow formatter
│   ├── utils/                # Utilities & constants
│   │   └── constants.py      # Enums & constants
│   └── cli.py                # CLI application
├── schemas/                   # JSON Schema definitions
│   ├── workflow-schema.yaml  # Workflow configuration schema
│   └── agent-interface.yaml  # Agent interface schema
├── templates/                 # Built-in workflow templates
│   └── web-fullstack.yaml    # Web fullstack template
├── policies/                  # System policies
│   ├── language-policy.yaml  # Language usage rules
│   └── file-policy.yaml      # File operation rules
└── tests/                     # Unit tests
```

## Configuration Files

### Workflow Configuration

Workflows are defined in YAML files following the schema in `schemas/workflow-schema.yaml`:

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

### Available Templates

- **web-fullstack**: Full-stack web application (7 stages, 14 agents)
  - Includes: customer liaison, requirements audit, API design, parallel BE/FE implementation, review/QA, integration

More templates (mobile, infrastructure, data-pipeline) will be added in future iterations.

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

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=orchestrator --cov-report=html
```

### Code Quality

```bash
# Format code
black orchestrator/ tests/

# Lint
ruff check orchestrator/ tests/

# Type checking
mypy orchestrator/
```

## Architecture

This implementation (Iteration 1) provides:
- ✓ Configuration loading from YAML files
- ✓ JSON Schema validation
- ✓ Pydantic model validation
- ✓ CLI interface for validation and display
- ✓ Template system

Future iterations will add:
- Orchestration engine (workflow execution)
- OpenHands SDK integration (agent spawning)
- State management
- Context management
- Error handling implementation
- Logging infrastructure

## Design Principles

1. **Configuration-Driven**: All workflows defined in YAML
2. **Type-Safe**: Pydantic models for validation
3. **Incremental**: Minimal viable features first
4. **Extensible**: Clear extension points for future features

## References

- Design Document: `agent-delegation.md`
- Project Guide: `CLAUDE.md`
- Schemas: `schemas/`
- Implementation Plan: `.claude/plans/linked-toasting-quiche.md`

## Version

Current version: 0.1.0 (Iteration 1)
