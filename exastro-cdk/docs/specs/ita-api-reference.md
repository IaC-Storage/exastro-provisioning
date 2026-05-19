# ITA API Reference

Exastro IT Automation (ITA) のREST APIエンドポイントをまとめたリファレンス。  
`exastro-cdk` の `ITAClient` 実装の根拠資料として使用する。

## 共通仕様

| 項目 | 内容 |
| :--- | :--- |
| **ベースURL** | `https://<EXASTRO_BASE_URL>/api/{organization_id}/workspaces/{workspace_id}/ita` |
| **認証** | `Authorization: Bearer <access_token>` ヘッダー |
| **Content-Type** | `application/json`（ファイルアップロード時は `multipart/form-data`） |

### パスパラメータ（共通）

| パラメータ | 説明 |
| :--- | :--- |
| `organization_id` | オーガナイゼーションID |
| `workspace_id` | ワークスペースID |

---

## 1. 認証

### 1.1 アクセストークン取得

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

## 2. Movement

### 2.1 Movement 作成

| 項目 | 内容 |
| :--- | :--- |
| **メソッド** | `POST` |
| **エンドポイント** | `/api/{organization_id}/workspaces/{workspace_id}/ita/ansible-legacy-role/movements` |

#### リクエストボディ

```json
{
    "file": {
        "ansible_cfg": null
    },
    "parameter": {
        "movement_name": "movement-1",
        "host_specific_format": "IP or Hostname",
        "header_section": "- hosts: all \n  remote_user: \"{{ __loginuser__ }}\"\n  gather_facts: no",
        "orchestrator": "Ansible Legacy Role",
        "ansible_builder_options": null,
        "ansible_agent_execution_environment": null,
        "operational_parameter": null,
        "execution_environment": null,
        "delay_timer": 0,
        "ansible_cfg": null,
        "remarks": "",
        "winrm_connection": null
    }
}
```

#### パラメータ詳細

| フィールド | 型 | 必須 | 説明 |
| :--- | :--- | :---: | :--- |
| `parameter.movement_name` | string | ✓ | Movement名 |
| `parameter.host_specific_format` | string | ✓ | ホスト指定形式。`"IP or Hostname"` 固定（要確認） |
| `parameter.header_section` | string | ✓ | Playbookのヘッダーセクション（YAML文字列） |
| `parameter.orchestrator` | string | ✓ | オーケストレータ種別。Ansible Legacy Roleの場合は `"Ansible Legacy Role"` |
| `parameter.delay_timer` | integer | - | 実行遅延タイマー（秒）。デフォルト `0` |
| `parameter.remarks` | string | - | 備考 |
| `parameter.ansible_builder_options` | string\|null | - | TODO: 詳細不明 |
| `parameter.ansible_agent_execution_environment` | string\|null | - | TODO: 詳細不明 |
| `parameter.operational_parameter` | string\|null | - | TODO: 詳細不明 |
| `parameter.execution_environment` | string\|null | - | TODO: 詳細不明 |
| `parameter.winrm_connection` | string\|null | - | WinRM接続設定。Windows対象時に使用 |
| `file.ansible_cfg` | string\|null | - | `ansible.cfg` ファイルの内容 |

#### レスポンス

> **TODO:** 成功時・エラー時のレスポンスサンプルを記載してください。

---

### 2.2 Movement 一覧取得

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

### 2.3 Movement 更新

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

### 2.4 Movement 削除

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

## 3. ロールパッケージ

### 3.1 ロールパッケージ アップロード

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。（`multipart/form-data` でZIPファイルを送信する想定）

---

## 4. Movement-ロール紐付け（交差テーブル）

### 4.1 紐付け 作成

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

### 4.2 紐付け 更新・削除

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

## 5. Conductor

### 5.1 Conductor 作成（登録）

| 項目 | 内容 |
| :--- | :--- |
| **メソッド** | `POST` |
| **エンドポイント** | `/api/{org}/workspaces/{ws}/ita/menu/conductor_class_edit/conductor/class/maintenance/` |

Conductor は Movement と異なり、Start・Movement・End ノードと edge を含む独自 JSON を専用エンドポイントへ POST する（汎用 `maintenance/all/` ではない）。サンプルは `tests/api/conductor/conductor_single_movement_sample.json` を参照。

#### リクエストボディ（Movement 1 つの最小構成）

```json
{
  "config": {
    "nodeNumber": 4,
    "terminalNumber": 7,
    "edgeNumber": 3,
    "editorVersion": "2.0.0"
  },
  "conductor": {
    "id": null,
    "conductor_name": "my-conductor",
    "last_update_date_time": null,
    "note": "",
    "notice_info": {},
    "grid_snap": true,
    "movement_width": "auto",
    "movement_white_space": "wrap"
  },
  "node-1": { "type": "start",    "id": "node-1", "terminal": { ... }, "x": 7475, "y": 7971, "w": 199.047, "h": 58 },
  "node-2": { "type": "end",      "id": "node-2", "terminal": { ... }, "end_type": "6", "x": 8325.953, "y": 7971, "w": 199.047, "h": 58 },
  "node-3": { "type": "movement", "id": "node-3", "movement_id": "<uuid>", "movement_name": "os_setup", "skip_flag": 0, "operation_id": null, "orchestra_id": "3", "terminal": { ... }, "x": 7850, "y": 7971, "w": 264.297, "h": 58 },
  "line-1": { "type": "edge", "id": "line-1", "outNode": "node-1", "outTerminal": "terminal-1", "inNode": "node-3", "inTerminal": "terminal-5" },
  "line-2": { "type": "edge", "id": "line-2", "outNode": "node-3", "outTerminal": "terminal-6", "inNode": "node-2", "inTerminal": "terminal-2" }
}
```

#### パラメータ詳細

| フィールド | 型 | 必須 | 説明 |
| :--- | :--- | :---: | :--- |
| `conductor.conductor_name` | string | ✓ | Conductor 名 |
| `conductor.note` | string | - | 備考 |
| `node-N.type` | string | ✓ | `start` / `end` / `movement` のいずれか |
| `node-N.movement_id` | string (UUID) | ✓（movement ノード） | 対象 Movement の ID |
| `node-N.orchestra_id` | string | ✓（movement ノード） | オーケストレータ種別 ID（Ansible Legacy Role: `"3"`） |
| `node-N.skip_flag` | integer | - | スキップフラグ（`0`=通常, `1`=スキップ） |
| `line-N.outNode` / `inNode` | string | ✓ | エッジ接続元/接続先ノード ID |

#### レスポンス（成功時）

```json
{
  "data": { "conductor_class_id": "<uuid>" },
  "message": "SUCCESS",
  "result": "000-00000",
  "ts": "2026-05-19T06:17:30.511Z"
}
```

---

### 5.2 Conductor 一覧取得・廃止

Conductor の一覧取得・廃止は汎用メニュー API を使用する。

| 操作 | メソッド | エンドポイント |
| :--- | :--- | :--- |
| カラム一覧取得 | `GET`  | `/menu/conductor_class_list/info/column/` |
| フィルタ検索   | `POST` | `/menu/conductor_class_list/filter/` |
| 廃止（discard） | `POST` | `/menu/conductor_class_list/maintenance/all/` |

廃止ペイロード例（`type: Update` で `discard: "1"` に更新）:

```json
[
  {
    "type": "Update",
    "parameter": {
      "conductor_class_id": "<uuid>",
      "discard": "1",
      "last_update_date_time": "<取得した更新日時>"
    }
  }
]
```

---

## 6. 代入値自動登録設定

### 6.1 設定 作成・更新

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

## 参考

- [Exastro ITA 公式APIドキュメント](https://ita-docs.exastro.org/ja/2.7/reference/api/operator/platform-api.html)
