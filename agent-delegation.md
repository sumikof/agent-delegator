# OpenHands「AI開発組織」オーケストレーション設計ドキュメント（Python）

## 1. 目的

OpenHands SDK の Agent Delegation（spawn/delegate）を用いて、あなた（顧客）を中心にした「仮想開発組織」を Python でオーケストレーションする。

このドキュメントは **いきなりコードを書かずに**、まず「作るべき構成・責務・入出力・実行フロー・運用ルール」を定義し、実装の土台を固めることを目的とする。

---

## 2. 前提とゴール

### 2.1 前提

- OpenHands SDK を利用する
- 親エージェント（Orchestrator）がサブエージェントを spawn / delegate して制御する
- サブエージェント同士の直接通信は行わず、親がハブとして統合する
- サブエージェントの成果物は **必ず構造化（JSON）** して返し、親が機械的に判定できるようにする
- **設定ファイル駆動**：ワークフローは YAML/JSON で外部定義し、コード変更なしでフローを変更可能にする
- **プロジェクトタイプ汎用**：Web、モバイル、インフラ、データパイプラインなど全種別に対応可能な抽象設計

### 2.2 ゴール（完成形）

- 顧客（あなた）の依頼から、要件整理〜設計〜実装〜レビュー〜テスト〜統合までを **工程として分離**
- 各工程は **別サブエージェント** に委譲し、必要に応じて並列実行
- 親が「状態管理」「合否判定」「差し戻し」「成果物統合」を行う
- プロジェクトごとにエージェント構成とワークフローをカスタマイズ可能

---

## 3. コアコンセプト

### 3.1 エージェントアブストラクション

全エージェントは共通インターフェースを実装し、プラグイン形式で追加・削除が可能。

詳細は [schemas/agent-interface.yaml](schemas/agent-interface.yaml) を参照。

```
Agent Interface
├── Identity (id, name, role)
├── Capabilities (実行可能なアクション)
├── Responsibilities (must_do / must_not_do / may_do)
├── Boundaries (ファイルアクセス制限)
├── Language Policy (言語設定)
├── Escalation (エスカレーション先)
└── Execution Settings (timeout, retry)
```

### 3.2 ワークフローエンジン

ワークフローは YAML 設定ファイルで定義し、以下の機能を提供：

- **ステージ定義**：順次実行・並列実行の制御
- **ゲート判定**：各ステージ終了時の品質チェック
- **エラーハンドリング**：リトライ、サーキットブレーカー、フォールバック
- **タイムアウト管理**：グローバル・ステージ・エージェント単位

詳細は [schemas/workflow-schema.yaml](schemas/workflow-schema.yaml) を参照。

### 3.3 設定駆動アーキテクチャ

```
project-config.yaml          # プロジェクト固有設定
├── templates/xxx.yaml       # プロジェクトタイプ別テンプレート
├── schemas/                 # スキーマ定義
│   ├── workflow-schema.yaml
│   └── agent-interface.yaml
└── policies/                # 運用ポリシー
    ├── language-policy.yaml
    └── file-policy.yaml
```

---

## 4. エージェントテンプレートシステム

### 4.1 組み込みテンプレートカテゴリ

| カテゴリ | 含まれるエージェント | 用途 |
|----------|----------------------|------|
| **core** | orchestrator, client-liaison, planner, progress, integrator | 全プロジェクト共通 |
| **quality** | requirements-auditor, quality-auditor, tester | 品質管理 |
| **web-development** | api-designer, backend-dev, frontend-dev, reviewer-be, reviewer-fe | Web アプリ |
| **mobile-development** | mobile-architect, mobile-ios-dev, mobile-android-dev, mobile-reviewer | モバイルアプリ |
| **infrastructure** | infra-architect, terraform-dev, k8s-dev, security-auditor | インフラ構築 |
| **data-engineering** | data-architect, etl-dev, ml-engineer, data-validator | データパイプライン |
| **devops** | ci-cd-engineer, monitoring-setup, release-manager | 運用自動化 |

### 4.2 カスタムエージェントの追加

プロジェクト固有のエージェントは、ワークフロー設定の `agents.custom` セクションで定義：

```yaml
agents:
  include_templates:
    - core
    - quality
  custom:
    - id: "blockchain-dev"
      name: "Blockchain Developer"
      role: implementation
      capabilities:
        - write_solidity_contracts
        - deploy_contracts
      language_policy:
        all: "en"
```

---

## 5. ワークフロー設定

### 5.1 設定ファイル構成

ワークフロー設定ファイルは以下の構造を持つ：

```yaml
version: "1.0"

project:
  name: "プロジェクト名"
  type: web | mobile | infrastructure | data-pipeline | hybrid | custom
  language_policy:
    customer_facing: "ja"
    development: "en"

agents:
  include_templates: [core, quality, web-development]
  custom: []
  exclude: []

workflow:
  stages:
    - name: "ステージ名"
      agents: [agent-id-1, agent-id-2]
      execution_mode: sequential | parallel
      gate:
        required_status: OK
      on_failure: abort | retry | fallback
  error_handling:
    retry_policy: {...}
    circuit_breaker: {...}
```

完全なスキーマは [schemas/workflow-schema.yaml](schemas/workflow-schema.yaml) を参照。

### 5.2 プロジェクトタイプ別テンプレート

- [templates/web-fullstack.yaml](templates/web-fullstack.yaml) - Web フルスタック開発

追加予定：
- `templates/mobile-app.yaml` - モバイルアプリ開発
- `templates/infrastructure.yaml` - インフラ構築
- `templates/data-pipeline.yaml` - データパイプライン

---

## 6. 役割と責任の定義

### 6.1 責任範囲の3分類

各エージェントは以下の3つのカテゴリで責任を定義：

| 分類 | 説明 |
|------|------|
| **must_do** | 必ず実行すべき責務 |
| **must_not_do** | 絶対に行ってはならない行為 |
| **may_do** | 状況に応じて実行可能な行為 |

### 6.2 境界定義

ファイルアクセスと操作権限を明確に定義：

```yaml
boundaries:
  file_patterns:
    allowed: ["backend/**", "api/**/*.yaml"]
    forbidden: ["frontend/**", ".env*", "**/*.secret"]
  actions:
    allowed: ["read", "write", "execute_tests"]
    forbidden: ["deploy", "delete_production"]
```

### 6.3 エスカレーション

問題発生時のエスカレーション先を事前定義：

```yaml
escalation:
  on_ambiguity: requirements-auditor    # 要件が曖昧な場合
  on_blocker: progress                  # ブロッカー発生時
  on_security_concern: security-auditor # セキュリティ懸念
  on_scope_creep: client-liaison        # スコープ拡大要求
```

---

## 7. 通信とコンテキスト管理

### 7.1 言語ポリシー

詳細は [policies/language-policy.yaml](policies/language-policy.yaml) を参照。

#### 基本ルール

| カテゴリ | 言語 |
|----------|------|
| 顧客向けコミュニケーション | 日本語 |
| 開発内部コミュニケーション | 英語 |
| コードコメント | 英語 |
| 技術ドキュメント | 英語 |
| Git コミットメッセージ | 英語 |

#### エージェント別設定

| エージェント | 顧客向け | 開発内部 |
|--------------|----------|----------|
| client-liaison | 日本語 | 日本語 |
| progress | 日本語 | 英語 |
| その他開発系 | - | 英語 |

### 7.2 コンテキスト共有

エージェント間で共有するコンテキスト：

```yaml
shared_context:
  project_metadata:     # プロジェクト情報
  api_contract:         # API 契約（Single Source of Truth）
  current_state:        # 現在の状態
  completed_stages:     # 完了ステージ
  pending_issues:       # 未解決の課題
```

ストレージ形式：JSON（`workspace/.context/` 配下）

---

## 8. フィードバックループ設計方針

### 8.1 設計原則

フィードバックループは以下の原則に基づいて設計される：

1. **明確なステータス定義**: 各タスクは明確なステータスを持ち、状態遷移は決定論的に行う
2. **自動化可能性**: 品質評価とフィードバック生成は可能な限り自動化する
3. **透明性**: フィードバックプロセスは全て追跡可能で監査可能である
4. **スケーラビリティ**: 複数のレビュアーや並列フィードバックをサポートする
5. **フォールバック**: 自動化が困難な場合は人間にエスカレートできる

### 8.2 フィードバックループアーキテクチャ

```
フィードバックループの基本構造:

[タスク開始] → [エージェント実行] → [品質レビュー] → [判定]
                                      ↓
                                  [問題発見] → [フィードバック生成]
                                      ↓
                                  [修正依頼] → [エージェント再実行]
                                      ↓
                                  [再レビュー] → [承認/拒否]
```

### 8.3 ステータス遷移モデル

```
拡張ステータス遷移図:

NEW → IN_PROGRESS → IN_REVIEW → APPROVED → DONE
                     ↑       ↓
                     │       ↓
                     │   NEEDS_FIXES → IN_PROGRESS
                     │       ↓
                     │   REJECTED → (エスカレーション)
                     │
                     └─────────────────┘
```

### 8.4 コンポーネント間の相互作用

```
フィードバックループコンポーネント:

1. タスク実行エージェント: 実際の作業を実行
2. 品質監査エージェント: 成果物を評価
3. フィードバック生成エージェント: 詳細なフィードバックを作成
4. 状態管理エージェント: タスクステータスを管理
5. 通知エージェント: 関係者にステータス変更を通知
6. コンテキスト管理エージェント: 修正履歴とフィードバックを保持
```

### 8.5 品質評価基準

品質監査エージェントは以下の基準で評価を行う：

1. **コード品質**: 
   - コーディング規約の遵守
   - コードの可読性と保守性
   - ベストプラクティスの適用
   - 技術的負債の有無

2. **機能品質**:
   - 要件の完全性
   - エッジケースの処理
   - エラーハンドリング
   - パフォーマンス

3. **テスト品質**:
   - テストカバレッジ
   - テストの網羅性
   - テストの信頼性
   - テストの保守性

4. **ドキュメント品質**:
   - ドキュメントの完全性
   - ドキュメントの正確性
   - ドキュメントの最新性
   - ドキュメントの可読性

### 8.6 フィードバック生成ガイドライン

フィードバックは以下の構造で生成される：

```json
{
  "feedback_id": "unique-identifier",
  "task_id": "original-task-id",
  "status": "needs_fixes | approved | rejected",
  "severity": "low | medium | high | critical",
  "findings": [
    {
      "category": "code_quality | functional | test | documentation",
      "location": "file:line:column",
      "description": "問題の詳細説明",
      "evidence": "問題を示す証拠",
      "suggestion": "具体的な改善提案",
      "priority": "low | medium | high"
    }
  ],
  "overall_score": 0-100,
  "recommendation": "具体的なアクション",
  "deadline": "修正期限",
  "reviewer": "レビュアー情報",
  "timestamp": "フィードバック生成時刻"
}
```

### 8.7 状態管理設計

タスクステータスは以下の情報を含む：

```json
{
  "task_id": "unique-task-id",
  "current_status": "in_progress | in_review | needs_fixes | approved | rejected",
  "previous_status": "前のステータス",
  "status_changed_at": "ステータス変更時刻",
  "status_changed_by": "変更者",
  "transition_reason": "ステータス変更の理由",
  "feedback_history": [
    {
      "feedback_id": "フィードバックID",
      "timestamp": "フィードバック時刻",
      "reviewer": "レビュアー",
      "status": "フィードバックステータス"
    }
  ],
  "retry_count": 0,
  "max_retries": 3,
  "timeout_at": "タイムアウト時刻"
}
```

### 8.8 エラーハンドリングとフォールバック

フィードバックループにおけるエラーハンドリング：

1. **最大試行回数超過**: 3回の修正試行後に自動的に人間にエスカレート
2. **タイムアウト**: 設定時間内に修正が完了しない場合はエスカレート
3. **競合状態**: 同時修正要求が発生した場合はロックとキューイング
4. **デッドロック**: 循環依存が発生した場合は自動検出と解決
5. **手動介入**: いつでも人間がプロセスに介入可能

### 8.9 パフォーマンスとスケーラビリティ

フィードバックループのパフォーマンス設計：

1. **並列レビュー**: 複数のレビュアーが同時にレビュー可能
2. **バッチ処理**: 複数のフィードバックをまとめて処理
3. **キャッシング**: 過去のフィードバックをキャッシュして再利用
4. **優先度付け**: 重要度に基づいてフィードバックを優先処理
5. **リソース制限**: システムリソースの過剰使用を防止

## 9. 実行フロー（状態遷移）

### 9.1 基本フロー

```
1. Intake（受付）
   └─ client-liaison が顧客要求を仕様化

2. Requirements Check（要件監査）
   └─ requirements-auditor が曖昧点を列挙

3. Plan（計画）
   └─ planner が工程とタスクを定義

4. Contract（契約）
   └─ api-designer が OpenAPI を生成（Single Source of Truth）

5. Implementation（実装）
   └─ backend-dev と frontend-dev を並列で実装

6. Review & QA（品質ゲート）
   └─ reviewer-be / reviewer-fe / tester / quality-auditor を並列で実施

7. Integration（統合）
   └─ integrator が成果物を統合し完了判定

8. Progress（再計画）
   └─ NG があれば progress が再実行計画を提案 → 修正ループ
```

### 8.2 状態

```
NEW → SPECIFIED → PLANNED → CONTRACT_READY → IMPLEMENTED → QA_PASSED → INTEGRATED → DONE
                                                ↓                ↓
                                            FAILED ←←←←←←←←←←←←←←
```

### 8.3 並列処理機能（高度機能）

並列処理機能を使用すると、複数のエージェントを同時に実行でき、大規模プロジェクトの処理速度を大幅に向上させることができます。

```
並列処理フロー:
1. タスクキューに全てのエージェントタスクを登録
2. ロードバランサーがタスクを適切なワーカープールに割り当て
3. ワーカープールが複数のエージェントを並列で実行
4. リソースモニターがシステム状態を監視
5. 完了したタスクの結果を統合

並列実行可能なステージ:
- Implementation（バックエンドとフロントエンドの並列実装）
- Review & QA（複数のレビューとテストの並列実行）
```

並列処理の利点:
- **パフォーマンス向上**: 複数のエージェントを同時に実行できるため、総処理時間を短縮
- **リソース効率化**: システムリソースを最大限活用
- **スケーラビリティ**: 大規模プロジェクトにも対応可能
- **柔軟性**: タスクの優先度と依存関係に基づいたスマートなスケジューリング

並列処理モジュールの構成:
```
orchestrator/parallel/
├── __init__.py              # モジュール初期化
├── task_queue.py           # タスクキュー（優先度、依存関係管理）
├── worker_pool.py          # ワーカープール（エージェント実行）
├── load_balancer.py        # ロードバランサー（タスク割り当て）
├── monitor.py              # リソースモニター（システム監視）
└── orchestrator.py         # 並列処理オーケストレーター（統合）
```

並列処理の使用方法:
```bash
# 並列処理を使用してワークフローを実行
python -m orchestrator.main workflow.yaml --parallel

# CLIを使用して並列処理を実行
agent-delegate run workflow.yaml --parallel
```

---

## 9. 入出力設計

### 9.1 共通レスポンススキーマ

全サブエージェントは以下の JSON 形式で応答：

```json
{
  "status": "OK | NG",
  "summary": "処理内容の簡潔な要約",
  "findings": [
    {
      "severity": "INFO | WARN | ERROR",
      "message": "指摘内容",
      "ref": "対象ファイルや行番号",
      "suggestion": "改善提案"
    }
  ],
  "artifacts": [
    {
      "path": "relative/path/to/file",
      "type": "code | spec | doc | config | report",
      "desc": "成果物の説明",
      "checksum": "SHA256ハッシュ"
    }
  ],
  "next_actions": ["次に行うべき作業"],
  "context": {},
  "trace_id": "トレースID",
  "execution_time_ms": 1234
}
```

### 9.2 判定ルール

- `status = NG` の場合、必ず `findings` に `severity = ERROR` を1件以上含める
- `artifacts.path` は必ず workspace 上の実ファイルと一致させる
- 親エージェントは `status` と `findings.severity` のみを用いて工程の可否を自動判定

### 9.3 成果物の標準ディレクトリ構成

```
workspace/
├─ spec/           # 要件・合意仕様
├─ api/            # OpenAPI / JSONSchema
├─ backend/        # バックエンド実装
├─ frontend/       # フロントエンド実装
├─ reports/        # レビュー・テスト・監査結果
├─ integration/    # 統合成果物
├─ .context/       # エージェントコンテキスト（内部用）
└─ .logs/          # 操作ログ（内部用）
```

---

## 10. 運用ポリシー

### 10.1 ファイル更新ポリシー

詳細は [policies/file-policy.yaml](policies/file-policy.yaml) を参照。

#### バックアップファイル禁止

**バックアップファイルは作成しない。** Git 履歴がバージョン管理の役割を果たす。

禁止されるファイルパターン：
- `*.bak`, `*.backup`, `*.orig`, `*.old`
- `*.swp`, `*.swo`, `*~`
- `*.tmp`, `#*#`, `.#*`

#### アトミック操作

ファイル更新は一時ファイル経由でアトミックに実行し、部分書き込みによる破損を防止。

#### ファイル命名規則

- ファイル名：kebab-case
- 最大長：100文字
- 禁止文字：スペース、`<>:"|?*`

### 10.2 契約（Contract）最優先ルール

- API 定義（OpenAPI / JSONSchema）は唯一の正解
- FE / BE は契約から逸脱してはならない
- 項目の追加・削除・型変更は禁止
- 変更が必要な場合は必ず `status = NG` として差し戻す

### 10.3 最小変更原則

- 不要なリファクタリングは禁止
- コメントは必ず保持する
- 既存の振る舞いを変更しない
- 依頼された範囲のみを変更する

---

## 11. 信頼性とエラーハンドリング

### 11.1 リトライポリシー

```yaml
retry_policy:
  max_attempts: 3
  backoff_type: exponential
  initial_delay_ms: 1000
  max_delay_ms: 60000
  multiplier: 2.0
  jitter: true
  jitter_factor: 0.1
```

#### エラー分類

| 分類 | コード例 | デフォルトアクション |
|------|----------|----------------------|
| 一時的 | TIMEOUT, RATE_LIMITED | リトライ |
| 永続的 | INVALID_INPUT, CONTRACT_VIOLATION | エスカレーション |
| 回復可能 | PARTIAL_FAILURE | 部分リトライ |

### 11.2 サーキットブレーカー

連続失敗時に自動的に処理を停止し、システム保護：

```yaml
circuit_breaker:
  failure_threshold: 5      # 5回失敗でオープン
  success_threshold: 3      # 3回成功でクローズ
  recovery_timeout_ms: 60000
```

### 11.3 フォールバック戦略

| 条件 | アクション |
|------|------------|
| リトライ上限超過 | オーケストレーターにエスカレート |
| サーキットオープン | 人間に委譲 |
| 致命的エラー | ワークフロー中断 |

---

## 12. 並列実行ガイドライン

### 12.1 並列化可能な組み合わせ

| ステージ | エージェント | 条件 |
|----------|--------------|------|
| 実装 | backend-dev, frontend-dev | 共有リソースなし |
| レビュー | reviewer-be, reviewer-fe, tester, quality-auditor | 独立レビュー |

### 12.2 直列化が必須なケース

| 理由 | シーケンス |
|------|------------|
| 依存関係 | api-designer → backend-dev |
| データ依存 | requirements-auditor → planner |

### 12.3 リソースロック

並列実行時のファイル競合を防止：

```yaml
resource_locking:
  type: file
  scope: exclusive
  timeout_ms: 30000
```

---

## 13. ログとトレーサビリティ

### 13.1 構造化ログ

```json
{
  "timestamp": "2025-01-12T10:00:00Z",
  "level": "INFO",
  "agent_id": "backend-dev",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "API implementation completed",
  "metadata": {
    "files_modified": 5,
    "tests_passed": 42
  }
}
```

### 13.2 監査ログ

記録対象イベント：
- ファイル作成・変更・削除
- エージェント生成
- タスク委譲
- ゲート通過・失敗

保持期間：90日

---

## 14. Python オーケストレーション実装方針

### 14.1 モジュール構成

```
orchestrator/
├─ main.py           # エントリポイント
├─ config.py         # 設定ローダー
├─ workflow.py       # ワークフローエンジン
├─ agents/
│   ├─ base.py       # 基底エージェントクラス
│   ├─ registry.py   # エージェントレジストリ
│   └─ loader.py     # テンプレートローダー
├─ state.py          # 状態管理
├─ validators.py     # JSON検証
├─ error_handler.py  # エラーハンドリング
├─ context.py        # コンテキスト管理
├─ logging.py        # ログ設定
└─ workspace.py      # ファイル操作
```

### 14.2 設定ローダー

```python
class ConfigLoader:
    def load_workflow(self, path: str) -> WorkflowConfig
    def load_agents(self, templates: list[str]) -> list[AgentConfig]
    def load_policies(self) -> Policies
```

---

## 15. モジュール構成

### 15.1 実装済みモジュール構成

```
orchestrator/
├─ __init__.py
├─ main.py               # メインオーケストレーター
├─ cli.py                # CLIコマンドインターフェース
├─ config/
│   ├─ loader.py         # 設定ファイルローダー
│   └─ validator.py      # 設定バリデーター
├─ agents/
│   ├─ base.py           # 基底エージェントクラス
│   ├─ registry.py       # エージェントレジストリ
│   ├─ loader.py         # エージェントローダー
│   ├─ core/             # コアエージェント
│   │   ├─ orchestrator_agent.py
│   │   ├─ client_liaison_agent.py
│   │   ├─ planner_agent.py
│   │   ├─ progress_agent.py
│   │   └─ integrator_agent.py
│   ├─ quality/          # 品質エージェント
│   │   ├─ requirements_auditor_agent.py
│   │   ├─ quality_auditor_agent.py
│   │   └─ tester_agent.py
│   └─ web-development/  # Web開発エージェント
│       ├─ api_designer_agent.py
│       ├─ backend_dev_agent.py
│       ├─ frontend_dev_agent.py
│       ├─ reviewer_be_agent.py
│       └─ reviewer_fe_agent.py
├─ context.py            # コンテキスト管理
├─ logging.py            # ロギング設定
├─ utils/
│   ├─ file_utils.py     # ファイル操作ユーティリティ
│   ├─ validation.py     # バリデーションユーティリティ
│   └─ state_machine.py  # 状態遷移管理
└─ display/              # ディスプレイモジュール
```

### 15.2 モジュール責務

| モジュール | 責務 |
|----------|------|
| `main.py` | オーケストレーションのメインロジック |
| `cli.py` | CLIコマンドの定義と実行 |
| `config/` | 設定ファイルの読み込みと検証 |
| `agents/` | エージェントの定義と管理 |
| `context.py` | コンテキストの管理と共有 |
| `logging.py` | ロギングの設定と出力 |
| `utils/` | ユーティリティ関数 |

## 16. CLI使用ガイド

### 16.1 基本コマンド

```bash
# ワークフローの実行
python -m orchestrator.cli run --config workflow.yaml

# 設定の検証
python -m orchestrator.cli validate --config workflow.yaml

# エージェント一覧の表示
python -m orchestrator.cli list-agents

# ヘルプの表示
python -m orchestrator.cli --help
```

### 16.2 オプション

| オプション | 説明 | デフォルト |
|----------|------|----------|
| `--config` | ワークフローファイルのパス | `workflow.yaml` |
| `--workdir` | 作業ディレクトリ | `./workspace` |
| `--log-level` | ログレベル | `INFO` |
| `--dry-run` | ドライランモード | `False` |
| `--debug` | デバッグモード | `False` |

### 16.3 使用例

```bash
# 簡単なワークフローの実行
python -m orchestrator.cli run --config examples/simple-web-app/workflow.yaml

# デバッグモードで実行
python -m orchestrator.cli run --config workflow.yaml --debug --log-level DEBUG

# カスタム作業ディレクトリで実行
python -m orchestrator.cli run --config workflow.yaml --workdir ./my-workspace
```

## 17. テンプレート

### 17.1 利用可能なテンプレート

| テンプレート | パス | 用途 |
|--------------|------|------|
| Webフルスタック | `templates/web-fullstack.yaml` | Webアプリケーション開発 |
| モバイルアプリ | `templates/mobile-app.yaml` | モバイルアプリ開発 |
| インフラ構築 | `templates/infrastructure.yaml` | インフラ構築 |
| データパイプライン | `templates/data-pipeline.yaml` | データパイプライン |

### 17.2 テンプレートの使用方法

```yaml
# workflow.yaml内でテンプレートをインクルード
agents:
  include_templates:
    - core
    - quality
    - web-development
```

### 17.3 カスタムテンプレートの作成

1. `templates/` ディレクトリに新しいYAMLファイルを作成
2. 必要なエージェントとワークフローを定義
3. ワークフロー設定でインクルード

## 18. エージェント定義

### 18.1 コアエージェント

| エージェント | ID | 責務 |
|--------------|----|------|
| オーケストレーター | orchestrator | 全体のオーケストレーション |
| クライアント連絡 | client-liaison | 顧客との連絡 |
| プランナー | planner | 計画の作成 |
| 進捗管理 | progress | 進捗の管理 |
| 統合 | integrator | 成果物の統合 |

### 18.2 品質エージェント

| エージェント | ID | 責務 |
|--------------|----|------|
| 要件監査 | requirements-auditor | 要件の監査 |
| 品質監査 | quality-auditor | 品質の監査 |
| テスター | tester | テストの実施 |

### 18.3 Web開発エージェント

| エージェント | ID | 責務 |
|--------------|----|------|
| API設計 | api-designer | API設計 |
| バックエンド開発 | backend-dev | バックエンド開発 |
| フロントエンド開発 | frontend-dev | フロントエンド開発 |
| バックエンドレビュー | reviewer-be | バックエンドコードレビュー |
| フロントエンドレビュー | reviewer-fe | フロントエンドコードレビュー |

## 19. 使用例

### 19.1 簡単なWebアプリケーション

`examples/simple-web-app/` ディレクトリに簡単なWebアプリケーションの例があります。

```bash
cd examples/simple-web-app
python -m orchestrator.cli run --config workflow.yaml
```

### 19.2 カスタムワークフロー

1. 新しいワークフローファイルを作成
2. 必要なエージェントを定義
3. タスクと依存関係を設定
4. CLIで実行

## 20. Mermaid 図

### 20.1 モジュール構成図

モジュール構成の詳細な図は [mermaid/module_structure.md](mermaid/module_structure.md) を参照。

### 20.2 ワークフロー実行図

ワークフロー実行の詳細な図は [mermaid/workflow_execution.md](mermaid/workflow_execution.md) を参照。

## 21. 次に作成する成果物

### 優先度：高
- [x] `examples/` - 基本的な使用例（simple-web-app, advanced-feedback-loop）
- [x] `tests/` - 基本的な統合テスト
- [ ] `examples/` - 追加の使用例（クラウドネイティブ、大規模プロジェクト）
- [ ] `tests/` - 統合テストの拡張（エッジケース、パフォーマンス）

### 優先度：中
- [x] スキーマの検証（CI/CDに統合済み）
- [x] CI/CDパイプラインの設定（GitHub Actions）
- [ ] CI/CDパイプラインの強化（セキュリティスキャン、パフォーマンステスト）
- [ ] セキュリティポリシーとガバナンス文書の作成

### 優先度：低
- [ ] ポリシーファイルの更新（セキュリティ、リリース管理）
- [ ] コードの整形と静的解析（全コードベースに対する最終チェック）
- [ ] リリースノートの作成とバージョンアップ
- [ ] パッケージングと配布の準備（PyPI、Docker）
- [ ] 運用ドキュメントの作成（モニタリング、バックアップ）


## 22. フィードバックループ実装の次ステップ

### ドキュメントと設計仕様の完成（最優先）

#### アーキテクチャドキュメントの更新
- [ ] フィードバックループの全体設計とコンポーネント間の相互作用を詳細化
- [ ] 状態遷移図の更新と詳細説明の追加
- [ ] エラーハンドリングとフォールバック戦略の文書化

#### 状態管理設計ドキュメントの作成
- [ ] 新しいステータスの定義と遷移ルールの詳細化
- [ ] 状態遷移表とシーケンス図の作成
- [ ] 競合状態とデッドロック防止策の設計

#### API仕様書の作成
- [ ] 新しいエンドポイントとメッセージ形式の定義
- [ ] エラーコードとステータスコードの標準化
- [ ] 互換性とバージョニングポリシーの文書化

#### 使用例とチュートリアルの作成
- [ ] フィードバックループの基本的な使用例
- [ ] 高度な使用例（複数レビュアー、優先度付けなど）
- [ ] トラブルシューティングガイド

#### テスト仕様書の作成
- [ ] テストケースと検証基準の定義
- [ ] パフォーマンスベンチマークの設計
- [ ] セキュリティテストの要件定義

#### 設計レビューミーティングの準備
- [ ] 設計ドキュメントのレビュー用資料作成
- [ ] アーキテクチャ決定事項のまとめ
- [ ] リスク評価と緩和策の文書化


## 23. 実装済み機能

### ワークフローエンジン
- [x] フィードバックループワークフローエンジンの基本実装
- [x] タスクステータス管理（7ステータス）
- [x] 品質監査エージェントによる自動フィードバック生成
- [x] フィードバックループ処理（問題発見→修正依頼→再実行→再レビュー）
- [x] タスク状態追跡とフィードバック履歴管理

### CLI統合
- [x] `--feedback-loop` / `-f` オプションの追加
- [x] 詳細な実行ログとステータス追跡
- [x] JSON出力にタスク状態とフィードバック履歴を含む

### API統合
- [x] `main.py`に`use_feedback_loop`パラメータを追加
- [x] `run_workflow_with_feedback()`関数を追加
- [x] 既存の並列処理とシーケンシャル処理との互換性維持

### バグ修正
- [x] タスクIDの不一致問題を修正
- [x] フィードバック生成のエラーハンドリングを改善
- [x] タスク処理ループのタイムアウトと最大試行回数を追加

### マルチエージェント協調システム
- [x] エージェント間通信プロトコルの実装
  - [x] メッセージキューと優先度ベースのメッセージ配送
  - [x] 要求/応答パターンとエラーハンドリング
  - [x] コーディネーション要求と応答メカニズム
- [x] 協調タスク管理システムの実装
  - [x] タスク依存関係グラフとコーディネーショングループ
  - [x] リソース管理と競合検出
  - [x] タスク優先度とスケジューリング
- [x] 競合解決と優先度管理アルゴリズム
  - [x] リソース競合、優先度競合、依存関係競合の検出
  - [x] 優先度ベース、時間ベース、交渉ベースの解決戦略
  - [x] 動的優先度調整とエスカレーションメカニズム
- [x] 並列ワークフローとの統合
  - [x] 競合解決システムの自動監視と解決
  - [x] タスクグラフメトリクスとパフォーマンスモニタリング
  - [x] エージェント間コーディネーションの統合
