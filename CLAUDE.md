# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

OpenHands SDKのAgent Delegation（spawn/delegate）を用いた「仮想開発組織」オーケストレーションシステム。親エージェント（Orchestrator）がサブエージェントを制御し、顧客の依頼から要件整理〜設計〜実装〜レビュー〜テスト〜統合までを工程として分離・実行する。

## ファイル構成

```
agent-delegate/
├── agent-delegation.md          # メイン設計ドキュメント
├── schemas/
│   ├── workflow-schema.yaml     # ワークフロー設定スキーマ
│   └── agent-interface.yaml     # エージェントインターフェース定義
├── templates/
│   └── web-fullstack.yaml       # Webフルスタックテンプレート
└── policies/
    ├── language-policy.yaml     # 言語ポリシー
    └── file-policy.yaml         # ファイル操作ポリシー
```

## アーキテクチャ

### 設定駆動
- ワークフローはYAML設定ファイルで外部定義
- コード変更なしでフロー変更可能
- プロジェクトタイプ別テンプレート（Web、モバイル、インフラ、データパイプライン等）

### エージェントテンプレート
| カテゴリ | 用途 |
|----------|------|
| core | 全プロジェクト共通（orchestrator, client-liaison, planner, progress, integrator） |
| quality | 品質管理（requirements-auditor, quality-auditor, tester） |
| web-development | Webアプリ（api-designer, backend-dev, frontend-dev, reviewer-be, reviewer-fe） |
| mobile-development | モバイルアプリ |
| infrastructure | インフラ構築 |
| data-engineering | データパイプライン |
| devops | 運用自動化 |

## 重要なポリシー

### 言語ポリシー
- **顧客向け（client-liaison, progress）**: 日本語
- **開発内部**: 英語
- **コード/コミット/技術ドキュメント**: 英語

### ファイル更新ポリシー
- **バックアップファイル禁止**: `*.bak`, `*.backup`, `*.orig` 等は作成しない（Git履歴で管理）
- **アトミック操作**: 一時ファイル経由で更新
- **命名規則**: kebab-case

### 契約最優先ルール
- API定義（OpenAPI/JSONSchema）は唯一の正解
- FE/BEは契約から逸脱禁止

### 最小変更原則
- 不要なリファクタリング禁止
- 依頼された範囲のみを変更

## エージェント責任定義

各エージェントは3分類で責任を定義：
- **must_do**: 必ず実行すべき責務
- **must_not_do**: 絶対に行ってはならない行為
- **may_do**: 状況に応じて実行可能な行為

## エラーハンドリング

- **リトライ**: 指数バックオフ（max 3回）
- **サーキットブレーカー**: 5回失敗でオープン
- **フォールバック**: 人間への委譲、ワークフロー中断

## サブエージェント出力形式

```json
{
  "status": "OK | NG",
  "summary": "処理内容の要約",
  "findings": [{"severity": "INFO|WARN|ERROR", "message": "...", "ref": "..."}],
  "artifacts": [{"path": "...", "type": "code|spec|doc", "desc": "..."}],
  "next_actions": ["次に行うべき作業"],
  "trace_id": "トレースID"
}
```
