# 01_FOUNDATION_PHASE.md: Exastro-CDK 開発計画

## 1. プロジェクトビジョン
Exastro-CDKは、Exastro IT Automation（以下ITA）の設定を宣言的なコードで管理し、自動化ジョブの構築プロセスを「直感的」かつ「再現可能」にすることを目的とする。

特にIaCに不慣れな開発者でも、迷わずベストプラクティスに基づいた自動化を実装できる体験を提供する。

## 2. 開発戦略 (Development Strategy)

### 2.1 言語選定とマイグレーションパス
* **言語: Python (MVP)** 
    * 高速なプロトタイピングと、Ansible/YAMLエコシステムとの親和性を優先
    * 将来的なパフォーマンス不足が懸念される場合はGoへの移行を検討するが、その際のリファクタリングコストを下げるためPydantic等を用いた厳密な型定義を行う。
* **設計思想:** 
    * **manifest.yaml** を単一の真実（SSOT）とする。
    * 複雑な分岐を持つConductorは「テスト容易性を損なうアンチパターン」と定義し、原則として**横一列（シーケンシャル）**な実行フローのみをサポートする。
    * 変数衝突を避けるため、`role名_変数名` の形式を推奨/強制する。


## 3. Phase.1 MVP目標: 「Conductorの自動生成」
汎用的なツールを構築する前に、具体的かつ価値の高いユースケースとして**「特定の用途のConductorを1つ完全にコードから生成する」**ことを目標とする。

### 3.1 対象範囲
* **Movement:** Conductorを構成する最小実行単位の定義。
* **Conductor:** ノード（Movement）とエッジ（実行順序）のワークフロー定義。
* **変数/パラメータ:** 実行に必要な環境変数やパラメータの紐付け。

## 4. 開発フロー (CDK Workflow)

### Step 1: init - アウトラインの生成

開発者が `manifest.yaml` に作業リストを記述し`exastro-cdk init` を実行する。

`manifest.yaml`はGitHub等にサンプルを保存しておく。

- **Exastro側の処理:**
  - `movements` リストに基づき、Movementを自動登録。
  - 登録したMovementを横一列に連結したConductorを自動作成。
- **ローカル側の処理:**
  - 各タスクに対応する Ansible Role ディレクトリを自動生成（`ansible-galaxy init` 相当）。

### Step 2: build-schema - 変数定義の抽出

Roleの開発が進み、`defaults/main.yml` に変数が定義された段階で実行する。

- **処理内容:** Role内の変数定義をスキャンし、パラメータシート用のメタデータ（JSON等）を生成。
- **規約:** 
  - 変数名には必ずRole名をプレフィックスとして付与する（`.ansible-lint` 等でチェックを検討）。
  - コメントアノテーション（例: `# @cdk-type: integer`）により、型や説明文をメタデータに付加する。

### Step 3: apply - Exastroとの同期

* **パラメータシート作成:** 抽出したメタデータに基づき、ITA上にパラメータシートを自動構築。
* **代入値自動登録設定:** パラメータシートと各Movementの変数を自動で紐付け。
* **Roleアップロード:** 完成したRoleをZip化し、対応するMovementへデプロイ。



## 5. 検討・実装アイテムリスト

### 5.1 CLI Core & Project Structure
* `exastro-cdk init` コマンドの実装。

### 5.2 API 通信基盤
* Exastro APIクライアントの基盤実装。
* 認証情報の安全な管理（環境変数および設定ファイル）。
* 基本的なCRUD（Create/Read/Update/Delete）操作の抽象化。

### 5.3 Conductor 固有の課題
* **依存関係の解決:** Movementが先に存在しなければConductorが作れない等のリソース生成順序の制御。
* **冪等性の初期設計:** 既存のConductorが存在する場合の振る舞い（上書き/スキップ/バージョンアップ）の定義。



## 6. Phase.1 完了条件 (Exit Criteria)

1.  `exastro-cdk init` で雛形ができる。
2.  `manifest.yaml` にConductorとMovementの構成を記述する。
3.  `exastro-cdk apply` (または `sync`) を実行。
4.  **Exastro ITAの管理画面を開くと、意図した通りのConductor作成・ワークフロー構築が完了している。**

---
**Next Step:** 具体的な `manifests` のスキーマ定義および、API疎通確認用のプロトタイプ実装。
