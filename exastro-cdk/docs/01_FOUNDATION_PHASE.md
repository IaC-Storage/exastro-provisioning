# 01_FOUNDATION_PHASE.md: Exastro-CDK 開発計画

## 1. 概要
本ドキュメントは、Exastro IT Automation (ITA) のリソースをコードで管理するためのツール `exastro-cdk` の第1段階（Foundation Phase）における開発方針と検討項目をまとめたものである。

## 2. 開発戦略 (Development Strategy)

### 2.1 言語選定とマイグレーションパス
* **初期開発 (MVP):** **Python** を採用する。
    * 理由: 仕様の流動性に対応するための開発スピード重視、および既存の自動化エコシステム（Ansible等）との親和性。
* **移行計画:** 実用に耐えられないパフォーマンス（大量リソース同期時の速度、並列処理の限界）が確認された場合、**Go** への切り替えを検討する。
* **AI活用設計:** Goへの移植を容易にするため、以下のルールを遵守する。
    * `Pydantic` や型ヒント（Type Hints）を徹底し、データ構造を厳密に定義する。
    * ロジックとI/O（API通信、ファイル操作）を疎結合にし、インターフェースを抽象化する。

## 3. Phase.1 MVP目標: 「Conductorの自動生成」
汎用的なツールを構築する前に、具体的かつ価値の高いユースケースとして**「特定の用途のConductorを1つ完全にコードから生成する」**ことを目標とする。

### 3.1 対象範囲
* **Movement:** Conductorを構成する最小実行単位の定義。
* **Conductor:** ノード（Movement）とエッジ（実行順序）のワークフロー定義。
* **変数/パラメータ:** 実行に必要な環境変数やパラメータの紐付け。

## 4. 検討・実装アイテムリスト

### 4.1 CLI Core & Project Structure
* `exastro-cdk init` コマンドの実装。
* **推奨ディレクトリ構造案:**
    ```text
    exastro-project/
    ├── manifests/          # リソース定義 (YAML)
    │   ├── conductors/
    │   └── movements/
    ├── environments/       # 環境別変数定義
    └── cdk.yaml            # 接続先情報・全体設定
    ```

### 4.2 Schema定義 (YAML DSL)
* **名前ベースのリファレンス:** UUID等のID指定ではなく、名前（Name）でリソース間を紐付ける仕組み。
* **抽象化:** コンダクターのノード座標の自動計算ロジック、あるいは簡略化されたフロー記述形式の検討。

### 4.3 API 通信基盤
* Exastro APIクライアントの基盤実装。
* 認証情報の安全な管理（環境変数および設定ファイル）。
* 基本的なCRUD（Create/Read/Update/Delete）操作の抽象化。

### 4.4 Conductor 固有の課題
* **依存関係の解決:** Movementが先に存在しなければConductorが作れない等のリソース生成順序の制御。
* **冪等性の初期設計:** 既存のConductorが存在する場合の振る舞い（上書き/スキップ/バージョンアップ）の定義。

## 5. Phase.1 完了条件 (Exit Criteria)
1.  `init` コマンドにより標準的なプロジェクト構成が生成されること。
2.  YAMLで定義した特定のワークフロー（Conductor）が、コマンド一発でExastro ITA環境上に正しく構築されること。
3.  構築されたConductorが、Exastroの管理画面から正常に実行可能な状態であること。

---
**Next Step:** 具体的な `manifests` のスキーマ定義および、API疎通確認用のプロトタイプ実装。
