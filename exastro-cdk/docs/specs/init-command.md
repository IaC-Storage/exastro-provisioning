# init コマンド仕様

## 実装状況（2026-05-19 時点）

| 機能 | 状態 | 備考 |
|---|---|---|
| 2段階実行フロー（manifest 生成 → Movement 登録） | ✅ 実装済み | `engine.py` `run_init_process()` |
| `--env-file` オプション | ✅ 実装済み | `python-dotenv` で読み込み |
| `--manifest` オプション（既存 manifest のコピー） | ✅ 実装済み | 指定パスをプロジェクトディレクトリへコピー |
| Movement の ITA 登録 | ✅ 実装済み | `MovementResource.create()` / 単体テスト済み |
| 対話型イニシャライザ | 🚧 未実装 | 現在はテンプレートからハードコード生成 |
| `.gitignore` 生成 | 🚧 未実装 | 将来対応予定 |
| Pydantic による厳密バリデーション | 🚧 未実装 | 現在は `dataclass`；型エラーは実行時まで検出されない |
| 命名規則バリデーション (`[a-z0-9_]`) | 🚧 未実装 | 将来対応予定 |
| Conductor の ITA 自動作成 | 🚧 未実装 | Task 3（`conductor.py` 実装）で対応予定 |

---

## 1. Why：コマンドの目的と価値
このコマンドの最大の目的は、ITAのGUI画面を操作しなくても自動構築の設計を開始できる状態を作ることです。

* **関心の分離 (Separation of Concerns)**: 「何を作るか（設計）」と「どう登録するか（反映）」を分離します。
* **オフラインファースト**: 開発者が移動中やセキュアなローカル環境でも、Ansible Roleの作成やワークフローの組み立てを可能にします。
* **標準化の強制**: 開発者ごとにバラバラになりがちなディレクトリ構造や命名規則を、プロジェクト開始時点で強制します。

---

## 2. What：仕様の詳細

### A. 対話型イニシャライザ (Interactive Setup)
`manifest.yaml`が存在しない場合、以下の情報をユーザーから取得します。

* **Workspace ID**: 開発対象となるExastroのワークスペースの識別子。
* **Conductor Name**: Conductorの名称。
* **Movements**: 実行したい順序に並べたMovement名のリスト（例: `os_setup, web_install`）。

### B. 生成される成果物 (Output Artifacts)
1.  **`manifest.yaml`**: 全ての構成の「単一の真実 (SSOT)」。
2.  **Ansible Role構造**: 指定されたMovement名に基づき、`ansible/roles/{name}/` 配下に `tasks/main.yml` と `defaults/main.yml` を生成します。
3.  **`.gitignore`**: `venv` や `.env`、一時ファイルを除外する設定。

### C. バリデーション・ポリシー (Strict Validation)
Pydanticを用いた厳密な型定義により、以下のルールをチェックします。

* **命名規則**: Movement名は `[a-z0-9_]` のみ（Ansible Roleの規約に準拠）。
* **構造の妥当性**: Conductor定義とMovementsリストの整合性。
* **変数のプレフィックス**: 将来的な `build-schema` を見据え、変数名にRole名を付与する準備ができているか。

---

## 3. How：実行フロー

### 第1回実行（`manifest.yaml` が存在しない場合）

対話型セットアップで情報を収集し、`manifest.yaml` テンプレートを生成して終了。

```bash
$ exastro-cdk init
# → manifest.yaml を生成（編集してから再実行）
```

### 第2回実行（`manifest.yaml` が存在する場合）

`manifest.yaml` の内容に基づき、ローカルとExastro ITA両側にリソースを展開。

```bash
$ exastro-cdk init
# ローカル: ansible/roles/<role_name>/ のディレクトリ構成を生成
# Exastro:  Movement を登録し、横一列の Conductor を自動作成
```

### `--env-file` オプション

`.env` ファイルから接続情報を読み込む場合に使用します。

```bash
$ exastro-cdk init --env-file .env
```

### 生成されるディレクトリ構造

```
project/
├── manifest.yaml
├── .gitignore
└── ansible/
    └── roles/
        └── <role_name>/
            ├── tasks/
            │   └── main.yml
            └── defaults/
                └── main.yml
```
