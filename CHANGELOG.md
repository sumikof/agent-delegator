# 変更履歴

このプロジェクトのすべての注目すべき変更は、このファイルに文書化されます。

フォーマットは[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)に基づいており、このプロジェクトは[セマンティックバージョニング](https://semver.org/spec/v2.0.0.html)に準拠しています。

## [未リリース]

### 追加

- **例とドキュメント**: 簡単なWebアプリワークフローの例を含む包括的な例ディレクトリを追加:
  - `examples/simple-web-app/workflow.yaml`: 完全なワークフロー設定
  - `examples/simple-web-app/requirements.txt`: サンプル要件ファイル
  - `examples/simple-web-app/expected_output/`: 期待される出力例
  - モジュール構造、CLIガイド、テンプレート、エージェント定義で`agent-delegation.md`を更新

- **Mermaid図**: ビジュアルドキュメントを追加:
  - `mermaid/module_structure.md`: モジュール構造図
  - `mermaid/workflow_execution.md`: ワークフロー実行図

- **スキーマ検証**: 包括的なスキーマ検証を追加:
  - `validate_schema.py`: ワークフロー設定の検証スクリプト
  - すべてのテンプレートと例をワークフロースキーマに対して検証

- **CI/CDパイプライン**: GitHub Actionsワークフローを追加:
  - `.github/workflows/lint_and_test.yml`: リント、テスト、検証ワークフロー
  - Blackフォーマット、Flake8リント、スキーマ検証を含む

- **ポリシー更新**: ファイルポリシーを更新:
  - CI/CDファイル制限を追加
  - 例ディレクトリのパーミッションを追加
  - セキュリティ制約を強化

### 変更

- **コードフォーマット**: コードベース全体にBlackコードフォーマットを適用
- **静的解析**: コードベース全体のFlake8の問題を修正
- **テンプレートクリーンアップ**: テンプレートから重複するYAMLドキュメントを削除
- **インポート最適化**: 未使用のインポートと依存関係をクリーンアップ

### 修正

- **スキーマコンプライアンス**: スキーマ要件に一致するようにワークフロー設定を修正
- **CLIの問題**: CLIエラーハンドリングのあいまいな変数名を修正
- **設定読み込み**: 設定ローダーの未使用変数を修正
- **モデル検証**: Pydanticモデルの未定義名の問題を修正

## [0.1.0] - 2024-01-01

### 追加

- 初期プロジェクト構造とコアモジュール
- 基本的なオーケストレーションフレームワーク
- エージェントインターフェース定義
- ワークフロースキーマ定義
- コアエージェント実装
- 設定読み込みと検証
- CLIインターフェース
- ユニットと統合テスト

[未リリース]: https://github.com/openhands/agent-delegate/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/openhands/agent-delegate/releases/tag/v0.1.0