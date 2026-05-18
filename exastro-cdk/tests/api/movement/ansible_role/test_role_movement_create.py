"""Movement(Ansible Role) 作成 / 削除 API の学習用テスト.

=================================

対象 API:
  GET  /api/{org}/workspaces/{ws}/ita/menu/{menu}/info/column/
       → Movement のフィールド名（REST キー名）一覧を取得する

  POST /api/{org}/workspaces/{ws}/ita/menu/{menu}/maintenance/all/
       → Movement を登録 / 更新 / 削除する汎用エンドポイント

{menu} に渡すメニュー名（代表例）:
  movement_list_ansible_legacy   … Ansible Legacy
  movement_list_ansible_pioneer  … Ansible Pioneer
  movement_list_ansible_role     … Ansible Role
  movement_list_terraform_cloud_ep … Terraform Cloud/EP

テストの流れ:
  1. info/column/ でフィールド名を確認する
  2. そのフィールドを使って Movement を Register（新規作成）する
  3. レスポンスの result が "000-00000" であることを確認する（成功判定）

手動廃止テストの実行方法:
  pytest -m manual --movement-id=<廃止したい movement_id>
"""

import pytest

# テスト対象のメニュー名（環境に合わせて変更してください）
MOVEMENT_MENU = "movement_list_ansible_role"


class TestMovementColumnInfo:
    """Step1: info/column/ API の挙動を確認する.

    Movement 登録に必要なフィールド名（REST キー名）はここで調べる。
    """

    def test_get_column_list_status_200(self, api_client, ita_url):
        """カラム一覧取得が 200 を返すこと."""
        url = ita_url("menu", MOVEMENT_MENU, "info", "column")
        resp = api_client.get(url)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}\n{resp.text}"
        )

    def test_get_column_list_result_ok(self, api_client, ita_url):
        """レスポンスの result が成功コード "000-00000" であること."""
        url = ita_url("menu", MOVEMENT_MENU, "info", "column")
        resp = api_client.get(url)
        body = resp.json()
        assert body.get("result") == "000-00000", (
            f"Unexpected result: {body.get('result')}\nfull response: {body}"
        )

    def test_get_column_list_has_data(self, api_client, ita_url):
        """Data フィールドにカラム名の辞書が入っていること."""
        url = ita_url("menu", MOVEMENT_MENU, "info", "column")
        resp = api_client.get(url)
        body = resp.json()
        columns = body.get("data")
        assert isinstance(columns, dict), f"data should be a dict, got: {type(columns)}"
        assert len(columns) > 0, "column dict is empty"

    def test_get_column_list_contains_movement_name(self, api_client, ita_url):
        """movement_name フィールドがカラム一覧に含まれること.

        （登録時に最低限必要なフィールドの存在確認）
        """
        url = ita_url("menu", MOVEMENT_MENU, "info", "column")
        resp = api_client.get(url)
        columns = resp.json().get("data", {})
        assert "movement_name" in columns, (
            f"'movement_name' not found in columns.\ncolumns: {columns}"
        )

    def test_print_all_columns(self, api_client, ita_url):
        """【学習用】取得したカラム名を全件表示する.

        pytest -s で実行すると標準出力に出る。
        """
        url = ita_url("menu", MOVEMENT_MENU, "info", "column")
        resp = api_client.get(url)
        columns = resp.json().get("data", {})
        print(f"\n=== [{MOVEMENT_MENU}] のカラム一覧 ({len(columns)} 件) ===")
        for key, label in columns.items():
            print(f"  - {key}: {label}")


class TestMovementCreate:
    """Step2: maintenance/all/ API で Movement を新規作成（Register）する.

    リクエストボディの構造（openapi.yaml の MAINTENANCE_PARAMETERS より）:
    [
      {
        "type": "Register",          # Register / Update / Discard / Restore / Delete
        "parameter": {
          "movement_name": "...",    # 必須: Movement 名
          "discard": "0",            # 0=有効, 1=廃止
          ...                        # その他フィールドは info/column/ で確認
        }
      }
    ]
    """

    def test_create_movement_status_200(self, api_client, ita_url, created_movements):
        """Movement 作成リクエストが 200 を返すこと."""
        name = "test-movement-role-pytest"
        url = ita_url("menu", MOVEMENT_MENU, "maintenance", "all")
        payload = _build_register_payload(name)
        resp = api_client.post(url, json=payload)
        if resp.status_code == 200 and resp.json().get("result") == "000-00000":
            created_movements.append((MOVEMENT_MENU, name))
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}\n{resp.text}"
        )

    def test_create_movement_result_ok(self, api_client, ita_url, created_movements):
        """Movement 作成の result が "000-00000"（成功）であること."""
        name = "test-movement-role-pytest-result"
        url = ita_url("menu", MOVEMENT_MENU, "maintenance", "all")
        payload = _build_register_payload(name)
        resp = api_client.post(url, json=payload)
        body = resp.json()
        if body.get("result") == "000-00000":
            created_movements.append((MOVEMENT_MENU, name))
        assert body.get("result") == "000-00000", (
            f"Unexpected result: {body.get('result')}\nfull response: {body}"
        )

    def test_create_movement_empty_name_fails(self, api_client, ita_url):
        """movement_name が空文字の場合はエラーになること.

        （バリデーションの挙動を学ぶテスト）
        """
        url = ita_url("menu", MOVEMENT_MENU, "maintenance", "all")
        payload = _build_register_payload("")  # 空文字
        resp = api_client.post(url, json=payload)
        body = resp.json()
        # 成功コード以外 = バリデーションエラーと見なす
        assert body.get("result") != "000-00000", (
            "Empty movement_name should fail, but got success response."
        )

    def test_create_movement_missing_type_fails(self, api_client, ita_url):
        """Type フィールドが無い場合はエラーになること.

        （必須フィールドの確認テスト）
        """
        url = ita_url("menu", MOVEMENT_MENU, "maintenance", "all")
        payload = [
            {"parameter": {"movement_name": "role-missing-type-test"}}
        ]  # type なし
        resp = api_client.post(url, json=payload)
        # 400 または result != "000-00000" を期待
        body = resp.json()
        assert resp.status_code != 200 or body.get("result") != "000-00000", (
            "Missing 'type' field should fail, but got success response."
        )

    def test_create_multiple_movements(self, api_client, ita_url, created_movements):
        """複数の Movement を一括登録できること.

        （MaintenanceAll の一括操作を学ぶテスト）
        """
        names = ["test-movement-role-bulk-01", "test-movement-role-bulk-02"]
        url = ita_url("menu", MOVEMENT_MENU, "maintenance", "all")
        payload = [_build_register_entry(n) for n in names]
        resp = api_client.post(url, json=payload)
        body = resp.json()
        if body.get("result") == "000-00000":
            created_movements.extend((MOVEMENT_MENU, n) for n in names)
        assert body.get("result") == "000-00000", f"Bulk register failed: {body}"


@pytest.fixture(scope="module")
def discard_response(api_client, ita_url, movement_id_from_cli):
    """廃止 API を1回だけ呼び出し、レスポンスをキャッシュする.

    TestMovementDiscard の各テストはこの fixture を共有し、
    同じ movement_id への廃止リクエストを重複して送らないようにする。
    """
    movement = _fetch_movement_by_id(api_client, ita_url, movement_id_from_cli)
    url = ita_url("menu", MOVEMENT_MENU, "maintenance", "all")
    payload = _build_discard_payload(
        movement_id_from_cli, movement["last_update_date_time"]
    )
    resp = api_client.post(url, json=payload)
    print(
        f"\n[DISCARD] movement_id={movement_id_from_cli}"
        f" → status={resp.status_code} result={resp.json().get('result')}"
    )
    return resp


@pytest.mark.manual
class TestMovementDiscard:
    """【手動実行専用】maintenance/all/ API で Movement を廃止（discard フラグを 1 に更新）する.

    実行方法:
      pytest -m manual --movement-id=<廃止したい movement_id>

    廃止対象の movement_id は filter API や ITA の画面から事前に確認してください。

    テストの流れ:
      1. filter API で movement_id を検索し last_update_date_time を取得する（discard_response fixture）
      2. maintenance/all/ に type=Update, discard=1 で送信する（discard_response fixture、1回のみ）
      3. 各テストは同じレスポンスを検証する
      4. flag_verified テストで filter API を再取得し discard フラグを確認する
    """

    def test_discard_movement_status_200(self, discard_response):
        """廃止リクエストが 200 を返すこと."""
        assert discard_response.status_code == 200, (
            f"Expected 200, got {discard_response.status_code}\n{discard_response.text}"
        )

    def test_discard_movement_result_ok(self, discard_response):
        """廃止の result が "000-00000"（成功）であること."""
        body = discard_response.json()
        assert body.get("result") == "000-00000", (
            f"Unexpected result: {body.get('result')}\nfull response: {body}"
        )

    def test_discard_movement_flag_verified(
        self, api_client, ita_url, movement_id_from_cli, discard_response
    ):
        """廃止後に filter API で取得すると discard フラグが "1" になっていること.

        （Update 後の状態を filter で検証する学習テスト）
        discard_response に依存することで、廃止が完了した後に実行されることを保証する。
        """
        movement = _fetch_movement_by_id(api_client, ita_url, movement_id_from_cli)
        discard_value = movement.get("discard")
        print(f"\n[VERIFY] movement_id={movement_id_from_cli} discard={discard_value}")
        assert discard_value == "1", (
            f"discard フラグが '1' になっていません。現在の値: {discard_value!r}"
        )


# ── ペイロードビルダー（可読性のために分離） ────────────────────────────────


def _build_register_entry(movement_name: str) -> dict:
    """1 件分の Register エントリを返す."""
    return {
        "type": "Register",
        "parameter": {
            "movement_name": movement_name,
            "discard": "0",
            "host_specific_format": "IP",  # IPアドレスをホスト特定情報として使用する例
            # Ansible Role 固有フィールド（info/column/ で確認して追加可能）:
            # "ansible_use_tpf_vars": "1",
            # "remarks": None,
        },
    }


def _build_register_payload(movement_name: str) -> list:
    """maintenance/all に渡すリスト形式のペイロードを返す."""
    return [_build_register_entry(movement_name)]


def _fetch_movement_by_id(api_client, ita_url, movement_id: str) -> dict:
    """Filter API で movement_id を検索し parameter dict を返す.

    見つからない場合は pytest.skip() でテストをスキップする。
    """
    url = ita_url("menu", MOVEMENT_MENU, "filter")
    resp = api_client.post(
        url + "?file=no", json={"movement_id": {"LIST": [movement_id]}}
    )
    resp.raise_for_status()
    items = resp.json().get("data") or []
    if not items:
        pytest.skip(
            f"movement_id={movement_id} が見つかりません（既に削除済みか ID が誤り）"
        )
    return items[0]["parameter"]


def _build_discard_payload(movement_id: str, last_update_date_time: str) -> list:
    """廃止（discard フラグを 1 に更新）用のペイロードを返す."""
    return [
        {
            "type": "Update",
            "parameter": {
                "movement_id": movement_id,
                "discard": "1",
                "last_update_date_time": last_update_date_time,
            },
        }
    ]
