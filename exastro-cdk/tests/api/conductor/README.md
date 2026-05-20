# Conductor API テスト

`test_conductor_create.py` に含まれる Conductor の作成・フィルタ・廃止 API 学習用テストです。

## 前提条件

- `tests/.env` に ITA 接続情報が設定されていること（`EXASTRO_BASE_URL` / `EXASTRO_ORGANIZATION` / `EXASTRO_WORKSPACE` / `REFRESH_TOKEN`）
- ITA 上に **`os_setup`** という名前の Ansible Role Movement が登録済みであること

## 対象 API

| メソッド | パス | 用途 |
|---|---|---|
| `GET` | `/api/{org}/workspaces/{ws}/ita/menu/conductor_class_list/info/column/` | Conductor のフィールド名一覧を取得 |
| `POST` | `/api/{org}/workspaces/{ws}/ita/menu/conductor_class_edit/conductor/class/maintenance/` | Conductor JSON を登録する専用エンドポイント |
| `POST` | `/api/{org}/workspaces/{ws}/ita/menu/conductor_class_list/filter/` | Conductor 一覧を検索 |
| `POST` | `/api/{org}/workspaces/{ws}/ita/menu/conductor_class_list/maintenance/all/` | Conductor を廃止（discard=1 に Update） |
| `POST` | `/api/{org}/workspaces/{ws}/ita/menu/movement_list_ansible_role/filter/` | Movement 一覧を検索（orchestra_id 確認用） |

## テストクラスと実行方法

### TestConductorColumnInfo — フィールド名確認

Conductor 登録に必要なフィールド名（REST キー名）を `info/column/` API で確認します。

```bash
pytest tests/api/conductor/test_conductor_create.py::TestConductorColumnInfo -v -s
```

### TestConductorCreate — Conductor 作成（1 Movement）

`conductor/class/maintenance/` エンドポイントに Start → Movement → End 構成の JSON を POST します。
作成した Conductor はモジュール終了後に自動廃止されます。

```bash
pytest tests/api/conductor/test_conductor_create.py::TestConductorCreate -v -s
```

### TestConductorFilter — filter API 動作確認

`filter/` API で Conductor 一覧を取得し、レスポンス構造を確認します。
3-d の `ConductorResource.create()` で既存 Conductor を検索する際に使います。

```bash
pytest tests/api/conductor/test_conductor_create.py::TestConductorFilter -v -s
```

### TestOrchestraIdInMovementFilter — orchestra_id の動的取得確認

movement filter レスポンスの `parameter` に `orchestra_id` が含まれるかを確認します。
3-d で Conductor ノードに `orchestra_id` を動的にセットできるかどうかの判断材料になります。

```bash
pytest tests/api/conductor/test_conductor_create.py::TestOrchestraIdInMovementFilter -v -s
```

### TestConductorMultiMovement — Conductor 作成（2 Movement 直列）

Start → Movement[0] → Movement[1] → End の 2 Movement チェーン構成を登録します。
3-d のノード採番ロジック（`_build_multi_movement_conductor_payload`）を実機で検証します。

```bash
pytest tests/api/conductor/test_conductor_create.py::TestConductorMultiMovement -v -s
```

### TestConductorDiscard — Conductor 廃止（手動実行専用）

`maintenance/all/` API で指定した Conductor を廃止します。

> **注意:** このテストクラスは `@pytest.mark.manual` が付いており、通常の `pytest` 実行では自動的にスキップされます。

#### 実行手順

**1. 廃止したい conductor_class_id を確認する**

```bash
# filter API で Conductor 一覧を取得する例
curl -s -X POST \
  "http://<ホスト>:<ポート>/api/<org>/workspaces/<ws>/ita/menu/conductor_class_list/filter/?file=no" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

**2. 廃止テストを実行する**

```bash
cd exastro-cdk
pytest -m manual --conductor-id=<conductor_class_id> \
  tests/api/conductor/test_conductor_create.py::TestConductorDiscard
```

## まとめて実行

```bash
cd exastro-cdk

# 通常テスト（manual 除く）
pytest tests/api/conductor/ -v -s

# 特定クラスのみ
pytest tests/api/conductor/test_conductor_create.py::TestConductorFilter -v -s
```
