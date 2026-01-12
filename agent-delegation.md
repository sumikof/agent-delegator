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

### 2.2 ゴール（完成形）
- 顧客（あなた）の依頼から、要件整理〜設計〜実装〜レビュー〜テスト〜統合までを **工程として分離**
- 各工程は **別サブエージェント** に委譲し、必要に応じて並列実行
- 親が「状態管理」「合否判定」「差し戻し」「成果物統合」を行う

---

## 3. 全体アーキテクチャ

### 3.1 役割一覧（サブエージェント）
以下は初期スコープ（MVP）として必須の役割。必要に応じて追加・削減できる。

| ID | 役割 | 主な責務 |
|---|---|---|
| client-liaison | 顧客窓口 | 顧客要求を仕様に翻訳し、不明点/曖昧点を抽出 |
| planner | 計画設計 | 実施タスク分解、工程設計、優先度付け |
| progress | 進捗管理 | 状態遷移の確認、未完/失敗タスクの再計画提案 |
| requirements-auditor | 要件監査 | 要件の抜け/矛盾/曖昧表現の検出 |
| api-designer | API設計 | OpenAPI/JSONSchema を作成し契約を固定 |
| backend-dev | BE実装 | OpenAPI契約に従った実装（例: Spring Boot） |
| frontend-dev | FE実装 | OpenAPI契約に従った実装（例: React/TS） |
| reviewer-be | BEレビュー | 規約/品質/安全性/過剰変更の検査 |
| reviewer-fe | FEレビュー | UI品質/型/過剰変更の検査 |
| tester | テスト観点 | API契約に基づくテスト観点・疑似検証 |
| quality-auditor | 品質監査 | 方針逸脱（勝手な仕様追加など）検出 |
| integrator | 統合 | 成果物統合、最終判定、リリース候補作成 |

### 3.2 親エージェント（Orchestrator）の責務
親は「実装」や「設計」を行わず、以下に徹する。

- サブエージェント生成（spawn）
- タスク委譲（delegate）
- 返却JSONの検証
- 合否判定（Gate）
- NG時の差し戻し（修正依頼）と再実行
- 状態管理（State Machine）
- 成果物（ファイル）の配置と最終統合

---

## 4. 実行フロー（状態遷移）

### 4.1 基本フロー（MVP）
1. **Intake（受付）**: client-liaison が顧客要求を仕様化
2. **Requirements Check（要件監査）**: requirements-auditor が曖昧点を列挙
3. **Plan（計画）**: planner が工程とタスクを定義
4. **Contract（契約）**: api-designer が OpenAPI を生成（Single Source of Truth）
5. **Implementation（実装）**: backend-dev と frontend-dev を並列で実装
6. **Review & QA（品質ゲート）**: reviewer-be / reviewer-fe / tester / quality-auditor を並列で実施
7. **Integration（統合）**: integrator が成果物を統合し完了判定
8. **Progress（再計画）**: NGがあれば progress が再実行計画を提案 → 修正ループ

### 4.2 状態（例）
- NEW
- SPECIFIED
- PLANNED
- CONTRACT_READY
- IMPLEMENTED
- QA_PASSED
- INTEGRATED
- DONE
- FAILED（致命的）

---

## 5. 入出力設計（重要）

### 5.1 サブエージェント出力の統一フォーマット（必須）
全サブエージェントは、返答の冒頭または末尾に **必ず JSON** を含める。

#### 例: 共通レスポンススキーマ（提案）
```json
{
  "status": "OK | NG",
  "summary": "処理内容の簡潔な要約",
  "findings": [
    {
      "severity": "INFO | WARN | ERROR",
      "message": "指摘内容",
      "ref": "対象ファイルや行番号などの任意参照"
    }
  ],
  "artifacts": [
    {
      "path": "relative/path/to/file",
      "type": "code | spec | doc",
      "desc": "成果物の説明"
    }
  ],
  "next_actions": [
    "次に行うべき作業"
  ]
}
```
### 判定ルール

- `status = NG` の場合、必ず `findings` に `severity = ERROR` を1件以上含める  
- `artifacts.path` は必ず workspace 上の実ファイルと一致させる  
- 親エージェントは `status` と `findings.severity` のみを用いて工程の可否を自動判定する  
- `next_actions` は次に親エージェントが delegate すべき作業を自然文で記載する  

---

## 5.2 成果物の標準ディレクトリ構成
workspace/
├─ spec/           # 要件・合意仕様
├─ api/            # OpenAPI / JSONSchema
├─ backend/        # バックエンド実装
├─ frontend/       # フロントエンド実装
├─ reports/        # レビュー・テスト・監査結果
└─ integration/    # 統合成果物



すべてのサブエージェントは、このディレクトリ規約に従って成果物を保存する。

---

## 6. ルール（暴走防止）

### 6.1 契約（Contract）最優先ルール

- API 定義（OpenAPI / JSONSchema）は唯一の正解  
- FE / BE は契約から逸脱してはならない  
- 項目の追加・削除・型変更は禁止  
- 変更が必要な場合は必ず `status = NG` として差し戻す  

### 6.2 最小変更原則

- 不要なリファクタリングは禁止  
- コメントは必ず保持する  
- 既存の振る舞いを変更しない  

### 6.3 品質ゲート

- reviewer-be / reviewer-fe / tester / quality-auditor のいずれかが NG を出した場合、次工程に進めない  
- NG の指摘内容は必ず `reports/` 配下に保存する  

---

## 7. Python オーケストレーション実装方針

### 7.1 モジュール構成案

orchestrator/
├─ main.py        # エントリポイント
├─ config.py      # LLM / Tool 設定
├─ roles.py       # サブエージェント用プロンプト
├─ state.py       # 状態管理
├─ tasks.py       # delegate 用タスク定義
├─ validators.py  # JSON検証
└─ workspace.py   # ファイル操作


---

## 8. 実行フロー（MVP）

1. client-liaison が顧客要求を仕様化  
2. api-designer が OpenAPI を作成  
3. backend-dev / frontend-dev を並列で delegate  
4. reviewer-be / reviewer-fe / tester / quality-auditor を並列で delegate  
5. 全工程が OK の場合 integrator へ進む  
6. NG があれば progress により再計画し、該当工程を再実行  

---

## 9. 次に作成する成果物

- `roles.md` : 各サブエージェントのプロンプト定義  
- `response_schema.json` : 共通レスポンススキーマ  
- `state_machine.md` : 状態遷移定義  
- `orchestrator_skeleton.py` : 親エージェントの雛形実装  

---

