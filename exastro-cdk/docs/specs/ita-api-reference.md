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

### 5.1 Conductor 作成

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

### 5.2 Conductor 一覧取得・更新・削除

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

## 6. 代入値自動登録設定

### 6.1 設定 作成・更新

> **TODO:** エンドポイント・リクエスト/レスポンスの詳細を記載してください。

---

## 参考

- [Exastro ITA 公式APIドキュメント](https://ita-docs.exastro.org/ja/2.7/reference/api/operator/platform-api.html)
