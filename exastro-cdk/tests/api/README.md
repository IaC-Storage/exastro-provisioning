# Exastro ITA API テスト

Exastro IT Automation の REST API を対象とした学習用テスト群です。

## ディレクトリ構成

```
tests/api/
├── conftest.py          # 共通フィクスチャ・CLI オプション定義
├── pytest.ini           # pytest 設定（マーカー定義を含む）
├── movement/
│   ├── ansible_legacy/  # Ansible Legacy Movement テスト
│   └── ansible_role/    # Ansible Role Movement テスト
└── openapi/             # OpenAPI 仕様書取得スクリプト
```

## 事前準備

### 環境変数の設定

`tests/.env` に以下を記載してください。

```env
EXASTRO_BASE_URL=http://<ホスト名>:<ポート>
EXASTRO_ORGANIZATION=<オーガニゼーション ID>
EXASTRO_WORKSPACE=<ワークスペース ID>
REFRESH_TOKEN=<リフレッシュトークン>
```

リフレッシュトークンは Exastro Platform 管理コンソールから取得してください。

## テストの実行

### 通常実行（手動テストを除く全テスト）

```bash
cd exastro-cdk
pytest tests/api/
```

### 特定ファイルのみ実行

```bash
pytest tests/api/movement/ansible_role/test_role_movement_create.py
```

### 手動実行専用テスト（`@pytest.mark.manual`）

`@pytest.mark.manual` が付いたテストは通常実行では自動的にスキップされます。
実行するには `-m manual` を明示的に指定してください。

```bash
pytest -m manual --movement-id=<movement_id> tests/api/movement/ansible_role/
```

## CLI オプション

`conftest.py` で定義されているカスタムオプションです。

| オプション | 説明 | 対象テスト |
|---|---|---|
| `--movement-id=<id>` | 廃止対象の movement_id を指定する | `@pytest.mark.manual` の廃止テスト |

## マーカー一覧

`pytest.ini` で定義されているマーカーです。

| マーカー | 説明 | デフォルト動作 |
|---|---|---|
| `manual` | 手動実行専用テスト | 通常実行では除外（`-m manual` で実行） |

## フィクスチャ一覧（conftest.py）

| フィクスチャ名 | スコープ | 説明 |
|---|---|---|
| `api_client` | session | 認証済み `requests.Session` |
| `ita_url` | session | ITA API の URL ビルダー関数 |
| `movement_id_from_cli` | session | `--movement-id` オプションの値。未指定時はスキップ |
| `created_movements` | session | テスト中に作成した Movement を記録するリスト |
| `cleanup_test_movements` | session | テスト終了後に作成した Movement を自動削除 |
