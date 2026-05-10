# コーディング規約・開発ルール

## 1. ブランチ戦略

`main` ブランチを唯一の長期ブランチとする（**Trunk-Based Development**）。

```
main
 ├── feature/init-command
 ├── fix/ita-client-auth
 └── chore/update-dependencies
```

| ブランチ種別 | プレフィックス | 例 |
| :--- | :--- | :--- |
| 機能追加 | `feature/` | `feature/sync-command` |
| バグ修正 | `fix/` | `fix/manifest-parse-error` |
| リファクタリング | `refactor/` | `refactor/ita-client` |
| ドキュメント | `docs/` | `docs/api-reference` |
| 設定・雑務 | `chore/` | `chore/update-ruff` |

**ルール:**
- `main` への直接pushは禁止。必ずMR（Merge Request）を経由する。
- 作業ブランチは `main` から切り、作業完了後に削除する。
- ブランチ名はケバブケース（`-` 区切り）を使用する。

---

## 2. コミットメッセージ

**[Conventional Commits](https://www.conventionalcommits.org/)** 形式を採用する。

```
<type>(<scope>): <subject>

[body]  # 任意
```

### type 一覧

| type | 用途 |
| :--- | :--- |
| `feat` | 新機能の追加 |
| `fix` | バグ修正 |
| `refactor` | 動作を変えないコード変更 |
| `test` | テストの追加・修正 |
| `docs` | ドキュメントの変更 |
| `chore` | ビルド・設定・依存関係の変更 |
| `ci` | CI/CD設定の変更 |

### scope 例（任意）

`cli`, `engine`, `ita-client`, `manifest`, `schema`

### 例

```
feat(cli): initコマンドの2段階実行を実装

manifest.yamlが存在しない場合はテンプレート生成のみ行い、
存在する場合はRoleディレクトリの展開まで実施する。
```

```
fix(ita-client): アクセストークンの期限切れ時に自動リフレッシュするよう修正
```

```
chore: ruffとpre-commitの設定を追加
```

---

## 3. レビュープロセス

```
作業ブランチで実装
    ↓
MR（Merge Request）作成
    ↓
GitLab CI 自動実行（テスト・Lint・型チェック）
    ↓  ← CI通過が必須条件
レビュアー（@nakagawa）によるコードレビュー
    ↓  ← 承認が必須条件
main へマージ（Squash merge 推奨）
```

**MR作成時のルール:**
- タイトルはコミットメッセージと同形式（`feat(scope): 説明`）
- 対応するissueがある場合は `Closes #<issue番号>` を本文に記載
- WIPの場合は `Draft:` プレフィックスをつけてCIのみ回す
- セルフレビューを済ませてからレビュー依頼する

---

## 4. Linter（ruff）

[ruff](https://docs.astral.sh/ruff/) を使用する。設定は `pyproject.toml` で一元管理する。

### `pyproject.toml` 設定

```toml
[tool.ruff]
target-version = "py311"  # TODO: Pythonバージョンが確定したら更新
line-length = 88

[tool.ruff.lint]
# 有効にするルールセット
# D: pydocstyle (ドキュメンテーションチェック)
# E: Pycodestyle (標準的なスタイル)
# W: Pycodestyle (標準的なスタイル)
# F: Pyflakes (エラー検出)
# I: Isort (import順序の自動整理)
# B: Flake8-bugbear (バグの温床になりやすいコードの検出)
# UP: Pyupgrade (古い構文のアップデート)
# N: PEP8-naming (命名規則)
# C901: 循環的複雑度（Cyclomatic Complexity）
select = ["D", "E", "W", "F", "I", "B", "UP", "N", "C901"]

# 無視するルール
# D100: モジュール自体のdocstringは必須にしない
# D104: __init__.pyのdocstringは必須にしない
# E501: 行長制限 (Ruffのformatterに任せるためlintでは無視)
ignore = ["D100", "D104", "E501"]

[tool.ruff.lint.pydocstyle]
convention = "google"  # Googleスタイルを採用
```

### pre-commit との統合

`.pre-commit-config.yaml` を用意し、コミット時に自動実行する。ruff（Lint・Format）とmypy（型チェック）を両方フックに登録することで、コミット前に品質チェックを完結させる。

```yaml
# .pre-commit-config.yaml
repos:
  # --- Ruff (Linter & Formatter) ---
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.10
    hooks:
      # Linter
      - id: ruff
        args: [--fix]
      # Formatter
      - id: ruff-format

  # --- Mypy (Type Checker) ---
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.0
    hooks:
      - id: mypy
        exclude: ^tests/
        additional_dependencies:
          - pytest
          - pytest-mock
          - pydantic
          - dotenv
```

**セットアップ手順:**

```bash
pip install pre-commit
pre-commit install   # .git/hooks/pre-commit に登録
```

---

## 5. 型チェック（mypy）

[mypy](https://mypy.readthedocs.io/) を使用する。設定は `pyproject.toml` の `[tool.mypy]` セクションで管理する。pre-commit フックにも組み込まれているため、コミット時にローカルでも自動実行される。

### 現在の設定（`pyproject.toml`）

```toml
[tool.mypy]
python_version = "3.11"
warn_unused_configs = true
warn_return_any = false
disallow_untyped_defs = true       # すべての関数に型ヒントを必須
disallow_incomplete_defs = true    # 不完全な型ヒントを禁止
check_untyped_defs = true
ignore_missing_imports = true
no_implicit_optional = true
exclude = ['^tests/']
```

### GitLab CI での実行

```yaml
# .gitlab-ci.yml（イメージ）
type-check:
  stage: verify
  script:
    - pip install mypy
    - mypy src/
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

**ローカル実行:**

```bash
mypy src/
```

---

## 6. CI全体の実行順序（GitLab CI）

MR作成時に以下の順序でジョブが実行される。**全ジョブ通過がマージの必須条件。**

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   lint       │    │  type-check  │    │    test      │
│  (ruff)      │───▶│  (mypy)      │───▶│  (pytest)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

| ジョブ | ツール | 対象 |
| :--- | :--- | :--- |
| `lint` | ruff | `src/`, `tests/` |
| `type-check` | mypy | `src/` |
| `test` | pytest | `tests/` |
