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
