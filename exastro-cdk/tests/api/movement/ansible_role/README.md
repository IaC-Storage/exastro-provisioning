# Movement (Ansible Role) API テスト

`test_role_movement_create.py` に含まれる Ansible Role Movement の作成・削除 API 学習用テストです。

## 対象 API

| メソッド | パス | 用途 |
|---|---|---|
| `GET` | `/api/{org}/workspaces/{ws}/ita/menu/{menu}/info/column/` | Movement のフィールド名一覧を取得 |
| `POST` | `/api/{org}/workspaces/{ws}/ita/menu/{menu}/maintenance/all/` | Movement の登録 / 削除 |

`{menu}` には `movement_list_ansible_role` を使用しています。

## テストクラスと実行方法

### TestMovementColumnInfo — フィールド名確認

Movement 登録に必要なフィールド名（REST キー名）を `info/column/` API で確認します。

```bash
pytest tests/api/movement/ansible_role/test_role_movement_create.py::TestMovementColumnInfo
```

### TestMovementCreate — Movement 作成

`maintenance/all/` API で Movement を新規登録（`type: Register`）します。
作成した Movement はテストセッション終了後に自動削除されます。

```bash
pytest tests/api/movement/ansible_role/test_role_movement_create.py::TestMovementCreate
```

### TestMovementDiscard — Movement 廃止（手動実行専用）

`maintenance/all/` API で指定した Movement を廃止（`type: Update`, `discard: "1"`）します。
廃止にはレコードのタイムスタンプ検証が必要なため、事前に filter API で `last_update_date_time` を取得しています。

> **注意:** このテストクラスは `@pytest.mark.manual` が付いており、通常の `pytest` 実行では自動的にスキップされます。

#### 実行手順

**1. 廃止したい movement_id を確認する**

ITA の画面または filter API で movement_id を取得してください。

```bash
# filter API で Movement 一覧を取得する例
curl -s -X POST \
  "http://<ホスト名>:<ポート>/api/<org>/workspaces/<ws>/ita/menu/movement_list_ansible_role/filter/?file=no" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

**2. 廃止テストを実行する**

```bash
cd exastro-cdk
pytest -m manual --movement-id=<movement_id> \
  tests/api/movement/ansible_role/test_role_movement_create.py::TestMovementDiscard
```

#### テストの流れ

```
discard_response fixture（module スコープ、1回だけ実行）
  ├─ filter API（movement_id で検索）→ last_update_date_time を取得
  └─ maintenance/all/（type=Update, discard=1）で廃止 → レスポンスをキャッシュ

各テストは同じ discard_response を参照（廃止 API の重複呼び出しなし）
  ├─ test_discard_movement_status_200   → status_code を検証
  ├─ test_discard_movement_result_ok    → result コードを検証
  └─ test_discard_movement_flag_verified → filter API で discard フラグを確認
```

#### テスト内容

| テスト名 | 内容 |
|---|---|
| `test_discard_movement_status_200` | 廃止レスポンスが HTTP 200 であること |
| `test_discard_movement_result_ok` | レスポンスの `result` が `000-00000`（成功）であること |
| `test_discard_movement_flag_verified` | filter で再取得したとき `discard` フィールドが `"1"` になっていること |

> 廃止 API の呼び出しは `discard_response` fixture が担い、テスト間で共有されます。  
> 廃止済みレコードへの再リクエストはエラー（`499-00201`）になるため、重複実行を防ぐ設計です。
