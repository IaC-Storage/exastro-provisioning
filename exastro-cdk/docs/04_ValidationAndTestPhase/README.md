# VALIDATION_AND_TEST_PHASE

## 1. フェーズ目標

製品品質と遠隔運用の信頼性を**自動的に担保**するフェーズ。`sync` や `apply` の実行前にPlaybookの構文やAPIリクエストの妥当性を検査するValidation Engineを実装し、CI/CDパイプラインによる継続的な品質保証を確立する。

### 対象スコープ
| 機能 | 内容 |
| :--- | :--- |
| **`test` コマンド** | Exastro CDKプロジェクトの自動テスト実行 |
| **Validation Engine** | `sync` 前のPlaybook構文・APIリクエスト妥当性検査 |
| **GitHub Actions連携** | CI/CDパイプラインでの自動テストとバリデーション |

---

## 2. `test` コマンド設計

### 2.1 概要

Exastro CDKプロジェクト全体のテストを実行するコマンド。ユニットテストから結合テストまでを一括で実行し、結果を報告する。

```
$ exastro-cdk test
```

### 2.2 テスト階層

| テスト種別 | 内容 | ツール |
| :--- | :--- | :--- |
| **ユニットテスト** | 各モジュール（Parser, Client, Engine）の単体テスト | pytest |
| **スキーマバリデーション** | `manifest.yaml` のJSON Schema準拠チェック | jsonschema |
| **Ansible Lint** | Roleの構文・ベストプラクティス検査 | ansible-lint |
| **結合テスト** | モックAPIサーバーを使ったend-to-endの `sync` フロー検証 | pytest + responses |

### 2.3 テスト実行オプション

```
$ exastro-cdk test                  # 全テスト実行
$ exastro-cdk test --unit           # ユニットテストのみ
$ exastro-cdk test --lint           # Lintのみ
$ exastro-cdk test --validate       # スキーマバリデーションのみ
```

---

## 3. Validation Engine設計

### 3.1 概要

`sync` / `apply` コマンドの**実行前フック**として動作し、問題を早期に検出して無効なAPIリクエストの発行を防ぐ。

```
$ exastro-cdk sync
→ [Validation] manifest.yaml のスキーマチェック ... OK
→ [Validation] Ansible Role 構文チェック ... OK
→ [Validation] API接続確認 ... OK
→ [Sync] 差分の適用を開始します...
```

### 3.2 バリデーション項目

| チェック項目 | 内容 | 失敗時の動作 |
| :--- | :--- | :--- |
| **スキーマ検証** | `manifest.yaml` がJSON Schema定義に準拠しているか | エラー終了 |
| **参照整合性** | `movements` に定義されたRoleがローカルに存在するか | エラー終了 |
| **変数名規約** | `role名_変数名` プレフィックス規約に準拠しているか | 警告（続行可） |
| **API疎通確認** | Exastro ITAへのヘルスチェックリクエストが通るか | エラー終了 |
| **Playbookシンタックス** | `ansible-playbook --syntax-check` 相当の検査 | 警告（続行可） |

### 3.3 バリデーションのスキップ

CI等の特定環境ではバリデーションをスキップできるオプションを提供する。

```
$ exastro-cdk sync --skip-validation
```

---

## 4. GitHub Actions連携設計

### 4.1 CI/CDパイプライン概要

`manifest.yaml` や Ansible Roleの変更をトリガーに、自動でバリデーションとテストを実行するワークフローを提供する。

```yaml
# .github/workflows/exastro-cdk-ci.yml （イメージ）
on:
  push:
    paths:
      - 'manifest.yaml'
      - 'ansible/roles/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install exastro-cdk
        run: pip install exastro-cdk
      - name: Run validation
        run: exastro-cdk test
```

### 4.2 提供するワークフローテンプレート

`exastro-cdk init` 実行時に `.github/workflows/` へのCI設定テンプレートを生成するオプションを追加する。

| テンプレート | トリガー | 内容 |
| :--- | :--- | :--- |
| `ci.yml` | Pull Request | バリデーション・テスト・`diff` 結果のPRコメント投稿 |
| `cd.yml` | `main` ブランチへのマージ | `exastro-cdk sync` の自動実行 |

---

## 5. 実装アイテムリスト

### 5.1 `test` コマンド
- `exastro-cdk test` コマンドのエントリポイント実装。
- pytest 実行ランナーの統合。
- テストフィルタリングオプション（`--unit` / `--lint` / `--validate`）の実装。
- テスト結果のサマリ出力（pass/fail/skip件数）。

### 5.2 Validation Engine
- バリデーションエンジンの基盤実装（`sync` / `apply` への前処理フック）。
- JSON Schemaによる `manifest.yaml` 検証ロジック。
- Ansible Lint統合（`ansible-lint` のPythonラッパー呼び出し）。
- ITA APIヘルスチェックロジック。
- 参照整合性チェック（Role存在確認）。
- `--skip-validation` オプションの実装。

### 5.3 GitHub Actions連携
- CIワークフローテンプレート（`ci.yml`）の作成。
- CDワークフローテンプレート（`cd.yml`）の作成。
- `init` コマンドへのテンプレート生成オプション（`--with-github-actions`）追加。
- PRへの `diff` 結果自動コメント機能（GitHub Actions + `exastro-cdk diff --output json`）。

---

## 6. 完了条件 (Exit Criteria)

1. `exastro-cdk test` を実行すると、ユニットテスト・スキーマ検証・Lintが一括で実行される。
2. `exastro-cdk sync` 実行前にValidation Engineが自動的に動作し、問題を事前検出できる。
3. バリデーション違反があった場合、`sync` が中断され原因が明示される。
4. Pull RequestのタイミングでCIが自動実行され、`diff` 結果がPRにコメントされる。
5. `main` ブランチへのマージをトリガーに `sync` が自動実行される。

---

**Prerequisite:** ADVANCED_SYNC_AND_LIFECYCLE_MANAGEMENT_PHASEの完了条件をすべて満たしていること。  
**Next Step:** 成果物のパッケージング・リリース（PACKAGING_AND_RELEASE_PHASEへ）。
