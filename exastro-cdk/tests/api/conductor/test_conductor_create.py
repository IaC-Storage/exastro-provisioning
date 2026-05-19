"""Conductor 作成 / 廃止 API の学習用テスト.

=================================

Conductor の独自仕様:
  ITA の Conductor エディタは「JSON保存 / JSON読み込み」機能を持つ。
  登録時は Start・Movement・End ノードと、それらを繋ぐ edge を含む
  独自 JSON を専用エンドポイントへ POST する（maintenance/all/ ではない）。

対象 API:
  GET  /api/{org}/workspaces/{ws}/ita/menu/{menu}/info/column/
       → Conductor のフィールド名（REST キー名）一覧を取得する

  POST /api/{org}/workspaces/{ws}/ita/conductor/class/edit/
       → Conductor JSON を登録する専用エンドポイント
       → リクエストボディは conductor_single_movement_sample.json 参照（config / conductor / node-N / line-N）

  POST /api/{org}/workspaces/{ws}/ita/menu/{menu}/maintenance/all/
       → 廃止（discard=1 に Update）に使う汎用エンドポイント

{menu} に渡すメニュー名:
  conductor_class_list … Conductor クラス一覧

テストの流れ:
  1. info/column/ でフィールド名を確認する
  2. Movement の filter API で movement_id を取得する
  3. その movement_id を埋め込んだ Conductor JSON を POST して登録する
  4. レスポンスの result が "000-00000" であることを確認する（成功判定）

手動廃止テストの実行方法:
  pytest -m manual --conductor-id=<廃止したい conductor_class_id>
"""

import pytest

CONDUCTOR_MENU = "conductor_class_list"
CONDUCTOR_EDIT_PATH = "menu/conductor_class_edit/conductor/class/maintenance"

# Conductor に組み込む Movement（ITA 上に存在する Movement 名を指定してください）
MOVEMENT_MENU_FOR_LOOKUP = "movement_list_ansible_role"
MOVEMENT_NAME_FOR_TEST = "os_setup"


# ── フィクスチャ ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def movement_id_for_conductor(api_client, ita_url):
    """テスト用 Conductor に組み込む Movement の ID を ITA から取得する.

    MOVEMENT_NAME_FOR_TEST が存在しない場合はモジュール全体をスキップする。
    """
    url = ita_url("menu", MOVEMENT_MENU_FOR_LOOKUP, "filter")
    resp = api_client.post(
        url + "?file=no",
        json={"movement_name": {"LIST": [MOVEMENT_NAME_FOR_TEST]}},
    )
    resp.raise_for_status()
    items = resp.json().get("data") or []
    if not items:
        pytest.skip(
            f"Movement '{MOVEMENT_NAME_FOR_TEST}' が見つかりません。"
            "ITA に登録済みの Movement 名を MOVEMENT_NAME_FOR_TEST に設定してください。"
        )
    return items[0]["parameter"]["movement_id"]


@pytest.fixture(scope="module")
def created_conductors() -> list:
    """テスト中に作成した Conductor の conductor_class_id を記録するリスト."""
    return []


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_conductors(api_client, ita_url, created_conductors):
    """モジュール終了時に作成した Conductor を廃止（discard=1）してクリーンアップする."""
    yield

    print(f"\n[CLEANUP] created_conductors={created_conductors}")
    if not created_conductors:
        print("[CLEANUP] 作成済み Conductor なし。クリーンアップをスキップします。")
        return

    filter_url = ita_url("menu", CONDUCTOR_MENU, "filter")
    resp = api_client.post(
        filter_url + "?file=no",
        json={
            "conductor_class_id": {"LIST": created_conductors},
            "discard": {"NORMAL": "0"},
        },
    )
    if resp.status_code != 200:
        print(f"[CLEANUP] filter 失敗のためスキップ: {resp.text}")
        return

    items = resp.json().get("data") or []
    payload = [
        {
            "type": "Update",
            "parameter": {
                "conductor_class_id": item["parameter"]["conductor_class_id"],
                "discard": "1",
                "last_update_date_time": item["parameter"].get("last_update_date_time"),
            },
        }
        for item in items
        if item.get("parameter", {}).get("conductor_class_id")
    ]
    if payload:
        discard_url = ita_url("menu", CONDUCTOR_MENU, "maintenance", "all")
        discard_resp = api_client.post(discard_url, json=payload)
        print(
            f"[CLEANUP] discard → status={discard_resp.status_code}"
            f" result={discard_resp.json().get('result')}"
        )


@pytest.fixture(scope="module")
def conductor_id_from_cli(request: pytest.FixtureRequest) -> str:
    """コマンドラインオプション --conductor-id の値を返す.

    未指定の場合は pytest.skip() でテストをスキップする。
    """
    conductor_id = request.config.getoption("--conductor-id", default=None)
    if not conductor_id:
        pytest.skip(
            "--conductor-id が指定されていません（例: pytest -m manual --conductor-id=<id>）"
        )
    return conductor_id


@pytest.fixture(scope="module")
def discard_response(api_client, ita_url, conductor_id_from_cli):
    """廃止 API を1回だけ呼び出し、レスポンスをキャッシュする.

    TestConductorDiscard の各テストはこの fixture を共有し、
    同じ conductor_id への廃止リクエストを重複して送らないようにする。
    """
    conductor = _fetch_conductor_by_id(api_client, ita_url, conductor_id_from_cli)
    url = ita_url("menu", CONDUCTOR_MENU, "maintenance", "all")
    payload = _build_discard_payload(
        conductor_id_from_cli, conductor["last_update_date_time"]
    )
    resp = api_client.post(url, json=payload)
    print(
        f"\n[DISCARD] conductor_class_id={conductor_id_from_cli}"
        f" → status={resp.status_code} result={resp.json().get('result')}"
    )
    return resp


# ── Step1: info/column/ でフィールド構造を確認 ──────────────────────────────


class TestConductorColumnInfo:
    """Step1: info/column/ API の挙動を確認する.

    Conductor のフィールド名（REST キー名）はここで調べる。
    """

    def test_get_column_list_status_200(self, api_client, ita_url):
        """カラム一覧取得が 200 を返すこと."""
        url = ita_url("menu", CONDUCTOR_MENU, "info", "column")
        resp = api_client.get(url)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}\n{resp.text}"
        )

    def test_get_column_list_result_ok(self, api_client, ita_url):
        """レスポンスの result が成功コード "000-00000" であること."""
        url = ita_url("menu", CONDUCTOR_MENU, "info", "column")
        resp = api_client.get(url)
        body = resp.json()
        assert body.get("result") == "000-00000", (
            f"Unexpected result: {body.get('result')}\nfull response: {body}"
        )

    def test_get_column_list_has_data(self, api_client, ita_url):
        """Data フィールドにカラム名の辞書が入っていること."""
        url = ita_url("menu", CONDUCTOR_MENU, "info", "column")
        resp = api_client.get(url)
        columns = resp.json().get("data")
        assert isinstance(columns, dict), f"data should be a dict, got: {type(columns)}"
        assert len(columns) > 0, "column dict is empty"

    def test_get_column_list_contains_conductor_name(self, api_client, ita_url):
        """conductor_name フィールドがカラム一覧に含まれること."""
        url = ita_url("menu", CONDUCTOR_MENU, "info", "column")
        resp = api_client.get(url)
        columns = resp.json().get("data", {})
        assert "conductor_name" in columns, (
            f"'conductor_name' not found in columns.\ncolumns: {columns}"
        )

    def test_print_all_columns(self, api_client, ita_url):
        """【学習用】取得したカラム名を全件表示する.

        pytest -s で実行すると標準出力に出る。
        """
        url = ita_url("menu", CONDUCTOR_MENU, "info", "column")
        resp = api_client.get(url)
        columns = resp.json().get("data", {})
        print(f"\n=== [{CONDUCTOR_MENU}] のカラム一覧 ({len(columns)} 件) ===")
        for key, label in columns.items():
            print(f"  - {key}: {label}")


# ── Step2: conductor/class/edit/ で Conductor を新規作成 ─────────────────────


class TestConductorCreate:
    """Step2: conductor/class/edit/ API で Conductor を登録する.

    Conductor は Movement と異なり、Start・Movement・End ノードと
    それらを繋ぐ edge を含む独自 JSON を専用エンドポイントへ POST する。

    リクエストボディのトップレベルキー（conductor_single_movement_sample.json より）:
      config     … エディタのメタ情報（nodeNumber, editorVersion など）
      conductor  … Conductor 本体（conductor_name, note など）
      node-N     … 各ノード（type: start / end / movement）
      line-N     … エッジ（ノード間の接続情報）

    Movement 1 つの最小構成: Start → Movement → End
    """

    def test_create_conductor_status_200(
        self, api_client, ita_url, movement_id_for_conductor, created_conductors
    ):
        """Conductor 作成リクエストが 200 を返すこと."""
        name = "test-conductor-pytest"
        url = ita_url(CONDUCTOR_EDIT_PATH)
        payload = _build_conductor_payload(
            name, movement_id_for_conductor, MOVEMENT_NAME_FOR_TEST
        )
        resp = api_client.post(url, json=payload)
        body = resp.json()
        print(f"{url=}, {payload=}")
        if resp.status_code == 200 and body.get("result") == "000-00000":
            conductor_id = _extract_conductor_id(body)
            if conductor_id:
                created_conductors.append(conductor_id)
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}\n{resp.text}"
        )

    def test_create_conductor_result_ok(
        self, api_client, ita_url, movement_id_for_conductor, created_conductors
    ):
        """Conductor 作成の result が "000-00000"（成功）であること."""
        name = "test-conductor-pytest-result"
        url = ita_url(CONDUCTOR_EDIT_PATH)
        payload = _build_conductor_payload(
            name, movement_id_for_conductor, MOVEMENT_NAME_FOR_TEST
        )
        resp = api_client.post(url, json=payload)
        body = resp.json()
        if body.get("result") == "000-00000":
            conductor_id = _extract_conductor_id(body)
            if conductor_id:
                created_conductors.append(conductor_id)
        assert body.get("result") == "000-00000", (
            f"Unexpected result: {body.get('result')}\nfull response: {body}"
        )

    def test_create_conductor_empty_name_fails(
        self, api_client, ita_url, movement_id_for_conductor
    ):
        """conductor_name が空文字の場合はエラーになること.

        （バリデーションの挙動を学ぶテスト）
        """
        url = ita_url(CONDUCTOR_EDIT_PATH)
        payload = _build_conductor_payload(
            "", movement_id_for_conductor, MOVEMENT_NAME_FOR_TEST
        )
        resp = api_client.post(url, json=payload)
        body = resp.json()
        assert body.get("result") != "000-00000", (
            "Empty conductor_name should fail, but got success response."
        )

    def test_print_create_response(
        self, api_client, ita_url, movement_id_for_conductor
    ):
        """【学習用】登録レスポンスを全件表示する.

        pytest -s で実行するとレスポンス構造を確認できる。
        """
        name = "test-conductor-pytest-inspect"
        url = ita_url(CONDUCTOR_EDIT_PATH)
        payload = _build_conductor_payload(
            name, movement_id_for_conductor, MOVEMENT_NAME_FOR_TEST
        )
        resp = api_client.post(url, json=payload)
        print(f"\n=== Conductor 作成レスポンス (status={resp.status_code}) ===")
        import json

        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))


# ── 手動廃止テスト ──────────────────────────────────────────────────────────


@pytest.mark.manual
class TestConductorDiscard:
    """【手動実行専用】maintenance/all/ API で Conductor を廃止（discard フラグを 1 に更新）する.

    実行方法:
      pytest -m manual --conductor-id=<廃止したい conductor_class_id>

    廃止対象の conductor_class_id は filter API や ITA の画面から事前に確認してください。
    """

    def test_discard_conductor_status_200(self, discard_response):
        """廃止リクエストが 200 を返すこと."""
        assert discard_response.status_code == 200, (
            f"Expected 200, got {discard_response.status_code}\n{discard_response.text}"
        )

    def test_discard_conductor_result_ok(self, discard_response):
        """廃止の result が "000-00000"（成功）であること."""
        body = discard_response.json()
        assert body.get("result") == "000-00000", (
            f"Unexpected result: {body.get('result')}\nfull response: {body}"
        )

    def test_discard_conductor_flag_verified(
        self, api_client, ita_url, conductor_id_from_cli, discard_response
    ):
        """廃止後に filter API で取得すると discard フラグが "1" になっていること.

        discard_response に依存することで、廃止が完了した後に実行されることを保証する。
        """
        conductor = _fetch_conductor_by_id(api_client, ita_url, conductor_id_from_cli)
        discard_value = conductor.get("discard")
        print(
            f"\n[VERIFY] conductor_class_id={conductor_id_from_cli} discard={discard_value}"
        )
        assert discard_value == "1", (
            f"discard フラグが '1' になっていません。現在の値: {discard_value!r}"
        )


# ── ペイロードビルダー ────────────────────────────────────────────────────────


def _build_conductor_payload(
    conductor_name: str,
    movement_id: str,
    movement_name: str,
) -> dict:
    """Movement 1 つの最小構成 Conductor JSON を返す（conductor_single_movement_sample.json 準拠）.

    構成: Start(node-1) → Movement(node-3) → End(node-2)
    """
    return {
        "config": {
            "nodeNumber": 4,
            "terminalNumber": 7,
            "edgeNumber": 3,
            "editorVersion": "2.0.0",
        },
        "conductor": {
            "id": None,
            "conductor_name": conductor_name,
            "last_update_date_time": None,
            "note": "",
            "notice_info": {},
            "grid_snap": True,
            "movement_width": "auto",
            "movement_white_space": "wrap",
        },
        "node-1": {
            "type": "start",
            "id": "node-1",
            "terminal": {
                "terminal-1": {
                    "id": "terminal-1",
                    "type": "out",
                    "x": 7657,
                    "y": 8000,
                    "targetNode": "node-3",
                    "edge": "line-1",
                }
            },
            "x": 7475,
            "y": 7971,
            "w": 199.047,
            "h": 58,
        },
        "node-2": {
            "type": "end",
            "id": "node-2",
            "terminal": {
                "terminal-2": {
                    "id": "terminal-2",
                    "type": "in",
                    "x": 8343,
                    "y": 8000,
                    "targetNode": "node-3",
                    "edge": "line-2",
                }
            },
            "end_type": "6",
            "x": 8325.953,
            "y": 7971,
            "w": 199.047,
            "h": 58,
        },
        "node-3": {
            "type": "movement",
            "id": "node-3",
            "terminal": {
                "terminal-5": {
                    "id": "terminal-5",
                    "type": "in",
                    "x": 7867,
                    "y": 8000,
                    "targetNode": "node-1",
                    "edge": "line-1",
                },
                "terminal-6": {
                    "id": "terminal-6",
                    "type": "out",
                    "x": 8097,
                    "y": 8000,
                    "targetNode": "node-2",
                    "edge": "line-2",
                },
            },
            "movement_id": movement_id,
            "skip_flag": 0,
            "operation_id": None,
            "orchestra_id": "3",
            "movement_name": movement_name,
            "x": 7850,
            "y": 7971,
            "w": 264.297,
            "h": 58,
        },
        "line-1": {
            "type": "edge",
            "id": "line-1",
            "outNode": "node-1",
            "outTerminal": "terminal-1",
            "inNode": "node-3",
            "inTerminal": "terminal-5",
        },
        "line-2": {
            "type": "edge",
            "id": "line-2",
            "outNode": "node-3",
            "outTerminal": "terminal-6",
            "inNode": "node-2",
            "inTerminal": "terminal-2",
        },
    }


def _extract_conductor_id(response_body: dict) -> str | None:
    """登録成功レスポンスから conductor_class_id を取り出す.

    レスポンス構造: {"data": {"conductor_class_id": "..."}, "result": "000-00000", ...}
    """
    return response_body.get("data", {}).get("conductor_class_id")


def _fetch_conductor_by_id(api_client, ita_url, conductor_class_id: str) -> dict:
    """Filter API で conductor_class_id を検索し parameter dict を返す.

    見つからない場合は pytest.skip() でテストをスキップする。
    """
    url = ita_url("menu", CONDUCTOR_MENU, "filter")
    resp = api_client.post(
        url + "?file=no",
        json={"conductor_class_id": {"LIST": [conductor_class_id]}},
    )
    resp.raise_for_status()
    items = resp.json().get("data") or []
    if not items:
        pytest.skip(
            f"conductor_class_id={conductor_class_id} が見つかりません（既に削除済みか ID が誤り）"
        )
    return items[0]["parameter"]


def _build_discard_payload(conductor_class_id: str, last_update_date_time: str) -> list:
    """廃止（discard フラグを 1 に更新）用のペイロードを返す."""
    return [
        {
            "type": "Update",
            "parameter": {
                "conductor_class_id": conductor_class_id,
                "discard": "1",
                "last_update_date_time": last_update_date_time,
            },
        }
    ]
