## 前提条件
1. オーガナイゼーションは作成済みであること
2. リフレッシュトークンは発行済みであること

## API URL

1. Workspace API
   - https://ita-docs.exastro.org/ja/2.7/reference/api/operator/platform-api.html


## 開発ロードマップ

### 1. Foundation Phase
開発者が「まずは触れる」状態を作るためのフェーズ

- CLI Coreの実装： `exastro-cdk` のベースフレームワークの構築 (`python/go` など)
- `init` コマンドの実装：プロジェクト雛形の自動生成機能 (初期化と基本的なファイル構成の生成)
  - ディレクトリ構成も含めて、プロジェクトの基本的な構造を定義
- Schema定義: YAML/JSONスキーマの初版策定

### 2. Syncronization Phase
核心となる「宣言的定義」を実現するフェーズ

- `sync` コマンド(作成・更新)の実装：宣言的定義に基づいて、IT Automationの構成を自動的に同期する機能
  - APIとの通信ロジックの実装
  - 差分検出と適用のロジックの実装

### 3. Advanced Sync & Lifecycle Management Phase
運用の複雑さを排除して実用性を向上させるフェーズ

- Pruning機能の実装: 定義ファイルから削除されたリソースをExastro環境から安全に削除するロジックの開発
- Workspace文理: 開発者ごとのテナント分離ロジックを確立し、`sync` 時の干渉を防止する機能の実装
- `diff` コマンドの実装: 定義ファイルと現在の環境状態の差分を表示するドライラン機能の開発

### 4. Validation & Test Phase
製品＋遠隔運用の品質を自動で担保するフェーズ

- `test` コマンド
- Validation Engine: 実行前にPlaybookの構文やAPIリクエストの妥当性を検査する機能の実装
- GitHub Actions連携: CI/CDパイプラインでの自動テストとバリデーションの実装


### 5. Packaging & Release Phase
成果物を流通可能な形式(カートリッジ)にまとめるフェーズ


