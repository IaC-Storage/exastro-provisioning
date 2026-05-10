# PACKAGING_AND_RELEASE_PHASE

## 1. フェーズ目標

これまでのフェーズで構築した機能を**流通可能な形式（カートリッジ）**にまとめ、Exastro CDKをエンドユーザーが容易に導入・利用できるプロダクトとして整備する。

PyPIへのパッケージ公開、バージョン管理ポリシーの確立、およびユーザー向けドキュメントの整備を行い、プロジェクトを**一般公開可能な状態**に引き上げる。

### 対象スコープ
| 機能 | 内容 |
| :--- | :--- |
| **PyPIパッケージング** | `pip install exastro-cdk` で導入可能にする |
| **カートリッジ形式** | Ansible Role + manifest をセットにした配布形式の定義 |
| **バージョン管理** | セマンティックバージョニングとリリースフローの確立 |
| **ドキュメント整備** | エンドユーザー向けの公式ドキュメント公開 |

---

## 2. パッケージング設計

### 2.1 PyPI公開

`pip install exastro-cdk` でインストールできる状態を目標とする。

```
$ pip install exastro-cdk
$ exastro-cdk --version
exastro-cdk 1.0.0
```

**`pyproject.toml` の整備:**
- パッケージメタデータ（author, description, classifiers）の充実。
- エントリポイント（`exastro-cdk` CLIコマンド）の定義。
- 依存ライブラリのバージョン範囲の明確化。
- Python バージョンサポートレンジの明示（≥3.10 を想定）。

### 2.2 カートリッジ形式の定義

Ansible Role と `manifest.yaml` をセットにして共有・再利用できる**カートリッジ**形式を定義する。

```
my-cartridge/
├── manifest.yaml          # Conductor/Movement の定義
├── ansible/
│   └── roles/
│       ├── os_setup/
│       └── apache_install/
└── README.md              # カートリッジの説明・使い方
```

**カートリッジの利用フロー:**

```bash
# カートリッジをダウンロードして即座に適用
$ git clone https://github.com/example/my-cartridge
$ cd my-cartridge
$ exastro-cdk sync
```

### 2.3 カートリッジのサンプルリポジトリ

公式サンプルカートリッジをGitHub上に公開し、初回利用者がすぐに試せる環境を提供する。

---

## 3. バージョン管理ポリシー

### 3.1 セマンティックバージョニング

`MAJOR.MINOR.PATCH` 形式を採用する。

| バージョン区分 | 変更内容 |
| :--- | :--- |
| **MAJOR** | 後方互換性のない変更（`manifest.yaml` スキーマの破壊的変更など） |
| **MINOR** | 後方互換性を保った新機能追加（新コマンド・新オプション追加） |
| **PATCH** | バグ修正・ドキュメント修正 |

### 3.2 リリースフロー

```
feature branch
    ↓ Pull Request & CI通過
main branch
    ↓ タグ付け (v1.x.x)
GitHub Actions (release workflow)
    ↓ PyPI publish + GitHub Release作成
```

### 3.3 `manifest.yaml` スキーマのバージョニング

スキーマ自体にもバージョンを持たせ、互換性を明示する。

```yaml
# manifest.yaml
apiVersion: exastro-cdk/v1
...
```

---

## 4. ドキュメント整備

### 4.1 公開ドキュメント構成

| ドキュメント | 内容 |
| :--- | :--- |
| **クイックスタート** | インストールから最初の `sync` 完了までのステップバイステップガイド |
| **`manifest.yaml` リファレンス** | 全フィールドの説明・型・デフォルト値・使用例 |
| **CLIリファレンス** | 全コマンド・オプションの説明 |
| **カートリッジカタログ** | 公式サンプルカートリッジの一覧と用途説明 |
| **移行ガイド** | バージョンアップ時の変更点と移行手順 |

### 4.2 ドキュメントサイト

GitHub Pages または Read the Docs でホスティングし、コードの変更と連動して自動更新する。

---

## 5. 実装アイテムリスト

### 5.1 パッケージング
- `pyproject.toml` の本番向けメタデータ整備。
- PyPI TestPyPI への試験公開・検証。
- PyPI 本番公開。
- インストール後の動作確認テストの整備。

### 5.2 カートリッジ
- カートリッジディレクトリ構成の仕様確定と文書化。
- 公式サンプルカートリッジの作成・GitHub公開。
- `exastro-cdk init --from <cartridge-url>` によるカートリッジからの初期化オプション検討。

### 5.3 バージョン管理・リリース
- セマンティックバージョニングポリシーの文書化。
- GitHub Actions リリースワークフロー（`release.yml`）の作成。
- `CHANGELOG.md` 運用ルールの確立。
- `manifest.yaml` の `apiVersion` フィールドとスキーマバージョン管理の実装。

### 5.4 ドキュメント
- クイックスタートガイドの執筆。
- `manifest.yaml` スキーマリファレンスの生成（JSON Schemaからの自動生成検討）。
- CLIリファレンスの自動生成（`--help` テキストからの生成）。
- ドキュメントサイトのホスティング設定。

---

## 6. 完了条件 (Exit Criteria)

1. `pip install exastro-cdk` でインストールし、`exastro-cdk --version` が正常に動作する。
2. 公式サンプルカートリッジを `git clone` して `exastro-cdk sync` を実行すると、Exastro ITA上に環境が構築される。
3. PyPI上にパッケージが公開されており、バージョン履歴がCHANGELOGに記録されている。
4. 公式ドキュメントサイトが公開されており、クイックスタートからCLIリファレンスまでが参照できる。
5. `main` へのマージとタグ付けをトリガーに、PyPI公開がCI/CDで自動化されている。

---

**Prerequisite:** VALIDATION_AND_TEST_PHASEの完了条件をすべて満たしていること。  
**Goal:** このフェーズの完了をもって、Exastro CDK v1.0.0 の一般公開とする。
