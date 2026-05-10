# FOUNDATION_PHASE

## 1. フェーズ目標

開発者が「まずは触れる」状態を作るためのフェーズ。汎用的なツールを構築する前に、**「特定の用途のConductorを1つ完全にコードから生成する」**ことを具体的なゴールとする。

### 対象スコープ
| リソース | 内容 |
| :--- | :--- |
| **Movement** | Conductorを構成する最小実行単位の定義 |
| **Conductor** | ノード（Movement）とエッジ（実行順序）のワークフロー定義 |
| **変数/パラメータ** | 実行に必要な環境変数やパラメータの紐付け |

---

## 2. 言語戦略

### 2.1 Python MVP → Go マイグレーションパス

**まず Python でMVPを構築する。** 速度やスケーラビリティに問題が生じた場合に限り、Go によるリファクタリングを検討する。

| 段階 | 言語 | 判断基準 |
| :--- | :--- | :--- |
| **MVP（現フェーズ）** | Python | 高速プロトタイピング・Ansible/YAMLエコシステムとの親和性 |
| **移行検討** | Go | パフォーマンスボトルネックが実測で確認された場合 |

**移行コストを抑えるための設計原則:**
- Pydanticによる厳密な型定義を徹底し、データ構造を明確に保つ。
- ビジネスロジックをI/O処理から分離し、コアロジックの移植を容易にする。

---

## 3. `init` コマンド設計

`init` は **2段階の実行**を想定する。

### Step 1 (第1回 `init`): `manifest.yaml` の自動生成

プロジェクト未着手の状態で `exastro-cdk init` を実行すると、インタラクティブな対話またはテンプレートから **`manifest.yaml` を自動生成**する。

```
$ exastro-cdk init
```

- 生成物: プロジェクトルートに `manifest.yaml`
- 開発者はここで Conductor / Movement の構成を編集する
- サンプル `manifest.yaml` は GitHub 等に保存し参照可能にする

### Step 2 (第2回 `init`): ローカル開発環境の標準ディレクトリ作成

`manifest.yaml` を編集した後、再度 `exastro-cdk init` を実行すると、その内容に基づいてローカルとExastro両側にリソースを展開する。

```
$ exastro-cdk init   # manifest.yaml 編集後に実行
```

**ローカル側の処理:**
- `manifest.yaml` の `movements` リストに対応する Ansible Role ディレクトリを自動生成（`ansible-galaxy init` 相当）。
- 標準ディレクトリ構成:
  ```
  ansible/
  └── roles/
      └── <role_name>/
          ├── defaults/main.yml
          ├── tasks/main.yml
          └── ...
  ```

**Exastro側の処理:**
- `movements` リストに基づき、Movement を自動登録。
- 登録した Movement を横一列に連結した Conductor を自動作成。

---

## 4. Schema定義 (IDE連携ドラフト)

VSCode 等のIDEで `manifest.yaml` 編集時に補完・バリデーションが効くよう、**JSON Schemaのドラフト**を整備する。

### 4.1 目的
- 入力補完により、開発者が `manifest.yaml` の正しい書き方を迷わず習得できる。
- 不正な値やキーのタイポをエディタ上でリアルタイム検出できる。

### 4.2 Schema設計方針
- **形式:** JSON Schema (Draft 7 以降)
- **対応エディタ:** VSCode (`yaml-language-server` 経由)、JetBrains IDEs
- **紐付け方法:** `manifest.yaml` 冒頭に `# yaml-language-server: $schema=<path>` を記述

### 4.3 スキーマドラフト対象フィールド（初版）
```yaml
# manifest.yaml 構造イメージ
conductor:
  name: string         # Conductor名
  description: string  # 説明（任意）

movements:
  - name: string                # Movement名
    role_package_name: string   # 対応する ロールパッケージ名 (任意)
    description: string         # 説明（任意）
```

---

## 5. 実装アイテムリスト

### 5.1 CLI Core & Project Structure
- `exastro-cdk init` コマンドの2段階実行ロジックの実装。
- `manifest.yaml` テンプレートの生成機能。
- インタラクティブモード（対話形式）の実装。

### 5.2 API 通信基盤
- Exastro APIクライアントの基盤実装。
- 認証情報の安全な管理（環境変数および設定ファイル）。
- 基本的なCRUD（Create/Read/Update/Delete）操作の抽象化。

### 5.3 Conductor 固有の課題
- **依存関係の解決:** Movementが先に存在しなければConductorが作れない等のリソース生成順序の制御。
- **冪等性の初期設計:** 既存のConductorが存在する場合の振る舞い（上書き/スキップ/バージョンアップ）の定義。

### 5.4 Schema定義
- `manifest.yaml` の JSON Schema ドラフト作成。
- VSCode 用 `.vscode/settings.json` への Schema 紐付け設定。

---

## 6. 完了条件 (Exit Criteria)

1. `exastro-cdk init`（第1回）を実行すると、`manifest.yaml` が自動生成される。
2. `manifest.yaml` を編集し、`exastro-cdk init`（第2回）を実行すると、Ansible Roleの標準ディレクトリがローカルに生成される。
3. `exastro-cdk apply`（または `sync`）を実行できる。
4. **Exastro ITAの管理画面を開くと、`manifest.yaml` の定義通りのConductorとワークフロー構築が完了している。**
5. VSCode 上で `manifest.yaml` を編集する際、JSON Schema による入力補完とバリデーションが機能する。

---

**Next Step:** `manifest.yaml` の JSON Schema ドラフト作成、および API疎通確認用プロトタイプの実装。
