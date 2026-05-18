# Exastro ITA OpenAPI 仕様書 取得手順

## 概要

Exastro ITA v2.7 の REST API を利用するための OpenAPI 仕様書 (JSON/YAML) を取得する手順です。

## 取得方法

```bash
./get-ita-openapi.sh
```

出力ファイル:

| ファイル | 形式 | 用途 |
|---|---|---|
| `ita-openapi.yaml` | OpenAPI 3.0.3 (YAML) | コンテナから直接コピーした原本 |
| `ita-openapi.json` | OpenAPI 3.0.3 (JSON) | Swagger UI や各種ツール向け |

## なぜ `docker cp` で取得したのか

### 調査の経緯

API 仕様書の取得に `docker cp` を採用した理由は、Exastro ITA の API ゲートウェイ (platform-auth) の構造上、**HTTP 経由でOpenAPI 仕様書を取得するエンドポイントが外部に公開されていないため**です。

調査の過程で試みた方法と、それぞれが失敗した理由を以下に示します。

### 試みた方法と失敗理由

#### 1. 外部 URL 経由 (`http://<ホスト名>:80/api/.../openapi/`) → HTTP 404

Exastro の外部 URL (ポート 80) へのリクエストは `platform-auth` コンテナ内の Apache + Python WSGI アプリを経由します。
この WSGI アプリは `/api/{organization_id}/workspaces/{workspace_id}/ita/{subpath}` の形式でルーティングしますが、**`/openapi.json` というパスは `ita-api-organization` コンテナの API ルートに存在しない**ため、404 が返されました。

```bash
# 試したパス（いずれも HTTP 404）
GET http://<ホスト名>:80/api/{org_id}/ita/openapi/
GET http://<ホスト名>:80/api/{org_id}/workspaces/{ws_id}/ita/openapi/
GET http://<ホスト名>:80/api/{org_id}/workspaces/{ws_id}/ita/openapi.json
```

#### 2. コンテナ内から直接アクセス → HTTP 400 (Roles ヘッダー不足)

`ita-api-organization` コンテナ内から `localhost:8080` に直接アクセスすると、パス自体は存在する (`openapi.json` で HTTP 400) ことが分かりました。しかし、エラー内容は以下の通りでした。

```json
{"message": "リクエストヘッダーのパラメータ(Roles)が不正です", "result": "400-00001"}
```

`ita-api-organization` は `platform-auth` の WSGI アプリが認証処理後に付与する **`Roles` ヘッダー** (ユーザーのワークスペースロールを Base64 エンコードした値) を必須としています。コンテナに直接アクセスするとこのヘッダーが存在しないため、リクエストが弾かれます。

#### 3. connexion のデフォルト仕様書エンドポイント → HTTP 500

`ita-api-organization` は Python の [connexion](https://github.com/spec-first/connexion) ライブラリを使って構築されており、connexion はデフォルトで `/openapi.json` や `/ui/` に仕様書を公開します。しかし、これらのエンドポイントは HTTP 500 を返しました（connexion のバージョンやコンテナの初期化状態に起因するものと考えられます）。

### `docker cp` を選んだ理由

上記の調査を経て、`ita-api-organization` コンテナ内の `/exastro/swagger/swagger.yaml` が API 仕様の原本であることが分かりました。

- **connexion の `add_api('swagger.yaml')` の引数がこのファイルを直接参照している**
- このファイルが存在しなければ API サーバー自体が起動しない
- したがって、このファイルの内容が常に稼働中の API の仕様と一致することが保証されている

`docker cp` はコンテナのファイルシステムに直接アクセスするため、認証・ルーティングの制約を受けずに確実にファイルを取得できます。

```python
# /exastro/api.py（ita-api-organization コンテナ内）
flask_app = connexion.FlaskApp(__name__, specification_dir='./swagger/')
flask_app.add_api('swagger.yaml')  # ← このファイルが仕様の原本
```

## API の使用方法

取得した仕様書を参照しながら API を呼び出す場合、以下の認証フローが必要です。

### 1. アクセストークンの取得

```bash
ORGANIZATION_ID="<Your Organization ID>"
REFRESH_TOKEN="<Your Refresh Token>"

ACCESS_TOKEN=$(curl -s -X POST \
  "http://<ホスト名>:80/auth/realms/${ORGANIZATION_ID}/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "client_id=_${ORGANIZATION_ID}-api" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

> `REFRESH_TOKEN` は Exastro Platform の管理コンソールから取得してください。

### 2. API の呼び出し

```bash
WORKSPACE_ID="<Your Workspace ID>"

curl -s -X GET \
  "http://<ホスト名>:80/api/${ORGANIZATION_ID}/workspaces/${WORKSPACE_ID}/ita/user/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### API ベース URL

```
http://<ホスト名>:80/api/{organization_id}/workspaces/{workspace_id}/ita/
```

仕様書内のパス (`/api/{organization_id}/workspaces/{workspace_id}/ita/...`) を外部 URL のホスト部分で置き換えて使用してください。
