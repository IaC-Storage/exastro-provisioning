# CLAUDE.md — exastro-cdk

Exastro ITA の構成管理をコードで自動化する CLI ツール。`manifest.yaml` を Single Source of Truth として Movement・Conductor をコードで宣言し、ITA API へ反映する。

---

## 開発環境セットアップ

```bash
cd exastro-cdk
pip install -e ".[dev]"          # 開発用インストール
cp .env.example .env             # 接続情報を設定（EXASTRO_BASE_URL, EXASTRO_ORGANIZATION, EXASTRO_WORKSPACE, REFRESH_TOKEN）
```

---

## よく使うコマンド

```bash
# 単体テスト（外部 ITA 不要・推奨）
pytest tests/unit/ -v

# API 統合テスト（実 ITA 環境が必要）
pytest tests/api/ -v

# lint + 型チェック（pre-commit フック相当）
ruff check src/ tests/
mypy src/

# CLI の動作確認
exastro-cdk init .                      # Stage1: manifest.yaml を生成
exastro-cdk init . --env-file .env      # env-file を指定して Stage2 実行
```

---

## ディレクトリ構造

```
exastro-cdk/
├── src/exastro_cdk/
│   ├── main.py                     # CLI エントリーポイント（Typer app）
│   ├── cli/
│   │   ├── init.py                 # exastro-cdk init コマンド
│   │   ├── apply.py                # exastro-cdk apply（未実装）
│   │   └── build.py                # exastro-cdk build-schema（未実装）
│   ├── core/
│   │   ├── engine.py               # CDKEngine: init/sync の主処理
│   │   └── config.py               # ExastroConfig, load_config()
│   ├── models/
│   │   └── manifest.py             # ManifestModel, MovementModel（dataclass）
│   ├── services/
│   │   ├── ita_client.py           # ITAClient Facade
│   │   ├── token.py                # fetch_access_token()
│   │   └── resources/
│   │       ├── movement.py         # MovementResource.create()（実装済み）
│   │       └── conductor.py        # ConductorResource.create()（スタブ）
│   └── templates/
│       ├── manifest.yaml.j2        # manifest テンプレート
│       └── ita/v2.7/movement/      # Movement 登録用 Jinja2 テンプレート（orchestrator 別）
├── tests/
│   ├── unit/                       # 外部依存なし・高速（pytest tests/unit/）
│   │   ├── test_cli.py
│   │   ├── test_engine.py
│   │   └── test_movement_resource.py
│   └── api/                        # 実 ITA 環境が必要（pytest tests/api/）
│       ├── conftest.py
│       └── movement/
├── docs/
│   ├── 01_FoundationPhase/
│   │   ├── task_list.md            # 実装タスクの進捗管理
│   │   └── README.md               # フェーズ設計ドキュメント
│   └── specs/
│       ├── init-command.md         # init コマンド仕様（実装状況テーブルあり）
│       └── ita-api-reference.md    # ITA API リファレンス
└── examples/
    └── manifest.yaml               # manifest のサンプル
```

---

## アーキテクチャ

```
CLI (cli/*.py)
  └── CDKEngine (core/engine.py)     # ビジネスロジック・I/O 分離
        ├── _create_manifest()       # Jinja2 でテンプレート生成
        ├── _load_and_validate()     # YAML → ManifestModel
        ├── _scaffold_local_files()  # Ansible Role ディレクトリ生成
        └── _sync_initial_ita_structure()
              └── ITAClient (services/ita_client.py)   # Facade
                    ├── MovementResource               # ITA API への Movement 登録
                    └── ConductorResource              # ITA API への Conductor 登録（スタブ）
```

### データモデル

```python
@dataclass
class MovementModel:
    name: str
    description: str = ""
    orchestrator: str = "ansible_role"        # ansible_role / ansible_legacy / ansible_pioneer / terraform_cloud_ep
    host_specific_format: str = "IP"

@dataclass
class ManifestModel:
    workspace_id: str
    conductor: dict[str, Any] = {}
    movements: list[MovementModel] = []
```

### Movement 登録フロー

`MovementResource.create()` は orchestrator 種別に応じてメニュー URL を切り替え、`templates/ita/v2.7/movement/<orchestrator>.json.j2` をレンダリングして POST する。

```python
_ORCHESTRATOR_MENU = {
    "ansible_role":       "movement_list_ansible_role",
    "ansible_legacy":     "movement_list_ansible_legacy",
    "ansible_pioneer":    "movement_list_ansible_pioneer",
    "terraform_cloud_ep": "movement_list_terraform_cloud_ep",
}
```

---

## init コマンドの 2 段階実行

| 実行回 | 前提条件 | 処理内容 |
|---|---|---|
| 第 1 回 | manifest.yaml なし | テンプレートから manifest.yaml を生成して終了 |
| 第 2 回 | manifest.yaml あり | Role ディレクトリ生成 + ITA へ Movement 登録 |

### 環境変数（接続情報）

| 変数名 | 説明 |
|---|---|
| `EXASTRO_BASE_URL` | Exastro ベース URL（例: `http://192.168.10.70:80`） |
| `EXASTRO_ORGANIZATION` | オーガナイゼーション ID |
| `EXASTRO_WORKSPACE` | ワークスペース ID（manifest.workspace_id が優先） |
| `REFRESH_TOKEN` | OpenID Connect リフレッシュトークン |

---

## コーディング規約

- **型ヒント必須**（mypy strict、tests/ は除外）
- **Docstring**: Google スタイル（ruff D ルール）。モジュール・`__init__.py` は省略可
- **コメント**: WHY が非自明な箇所のみ。WHAT を説明するコメントは書かない
- **テスト**: 外部 ITA への接続を要するテストは `tests/api/` に分離。`tests/unit/` は mock のみ
- **モック**: `requests.Session` を `MagicMock(spec=requests.Session)` で差し替える
- **手動専用テスト**: `@pytest.mark.manual` を付与し、通常の CI では実行しない

---

## 実装状況（Task 1 完了時点）

| コンポーネント | 状態 |
|---|---|
| `exastro-cdk init`（Movement 登録まで） | ✅ 実装・テスト済み |
| `MovementResource.create()` | ✅ 実装・テスト済み |
| `ConductorResource.create()` | 🚧 スタブ（Task 3 で実装） |
| `exastro-cdk apply / sync` | 🚧 未実装（Task 4 で実装） |

詳細は [docs/01_FoundationPhase/task_list.md](docs/01_FoundationPhase/task_list.md) を参照。
