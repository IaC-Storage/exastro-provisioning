"""Exastro IT Automation API テスト共通設定."""

import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv


def pytest_addoption(parser: pytest.Parser) -> None:
    """コマンドラインオプションを追加する."""
    parser.addoption(
        "--movement-id",
        action="store",
        default=None,
        help="削除対象の movement_id（手動削除テスト用）",
    )
    parser.addoption(
        "--conductor-id",
        action="store",
        default=None,
        help="廃止対象の conductor_class_id（手動廃止テスト用）",
    )


load_dotenv(Path(__file__).parent.parent / ".env")

# ── 接続設定（環境変数 or デフォルト値で上書き可能） ──────────────────────
BASE_URL = os.getenv("EXASTRO_BASE_URL", "http://localhost:30080")
ORGANIZATION = os.getenv("EXASTRO_ORGANIZATION", "your-org-id")
WORKSPACE = os.getenv("EXASTRO_WORKSPACE", "your-workspace-id")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN", "")


# ── ヘルパー ──────────────────────────────────────────────────────────────
def _fetch_access_token() -> str:
    """REFRESH_TOKEN を使って新しいアクセストークンを取得する."""
    endpoint = f"{BASE_URL}/auth/realms/{ORGANIZATION}/protocol/openid-connect/token"
    resp = requests.post(
        endpoint,
        data={
            "client_id": f"_{ORGANIZATION}-api",
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _ita_url(*path_parts: str) -> str:
    """ITA API の URL を組み立てる."""
    base = f"{BASE_URL}/api/{ORGANIZATION}/workspaces/{WORKSPACE}/ita"
    suffix = "/".join(str(p).strip("/") for p in path_parts)
    return f"{base}/{suffix}/"


# ── フィクスチャ ──────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def api_client():
    """認証済み requests.Session（セッション全体で使い回す）."""
    access_token = _fetch_access_token()
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
    )
    return session


@pytest.fixture(scope="session")
def ita_url():
    """URL ビルダーを fixture として提供する."""
    return _ita_url


@pytest.fixture(scope="session")
def movement_id_from_cli(request: pytest.FixtureRequest) -> str:
    """コマンドラインオプション --movement-id の値を返す.

    未指定の場合は pytest.skip() でテストをスキップする。
    """
    movement_id = request.config.getoption("--movement-id")
    if not movement_id:
        pytest.skip(
            "--movement-id が指定されていません（例: pytest -m manual --movement-id=<id>）"
        )
    return movement_id


@pytest.fixture(scope="session")
def created_movements() -> list:
    """テスト中に作成したMovementを (menu, name) のタプルで記録するリスト."""
    return []


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_movements(api_client, created_movements):
    """テストセッション全体の前後で、作成したMovementをクリーンアップする."""
    yield

    print(f"\n[CLEANUP] created_movements={created_movements}")
    if not created_movements:
        print("[CLEANUP] 作成済み Movement なし。クリーンアップをスキップします。")
        return

    # menu ごとに対象Movementをまとめてフィルタ → 廃止（discard=1）
    from itertools import groupby

    sorted_items = sorted(created_movements, key=lambda x: x[0])
    for menu, entries in groupby(sorted_items, key=lambda x: x[0]):
        names = [name for _, name in entries]
        print(f"\n[CLEANUP] menu={menu} 対象名={names}")

        filter_url = _ita_url("menu", menu, "filter")
        filter_body = {
            "movement_name": {"LIST": names},
            "discard": {"NORMAL": "0"},  # 有効レコードのみ（廃止済みは除外）
        }
        print(f"[CLEANUP] filter_url={filter_url} body={filter_body}")
        resp = api_client.post(filter_url + "?file=no", json=filter_body)
        print(
            f"[CLEANUP] filter → status={resp.status_code} result={resp.json().get('result')}"
        )
        if resp.status_code != 200:
            print(f"[CLEANUP] filter 失敗のためスキップ: {resp.text}")
            continue

        items = resp.json().get("data") or []
        print(f"[CLEANUP] filter でヒットした件数: {len(items)}")
        if not items:
            print(
                "[CLEANUP] 対象 Movement が見つかりません（既に廃止済みか名前が不一致）。"
            )
            continue

        payload = [
            {
                "type": "Update",
                "parameter": {
                    "movement_id": item["parameter"]["movement_id"],
                    "discard": "1",
                    "last_update_date_time": item["parameter"].get(
                        "last_update_date_time"
                    ),
                },
            }
            for item in items
            if item.get("parameter", {}).get("movement_id")
        ]
        print(f"[CLEANUP] 廃止ペイロード ({len(payload)} 件): {payload}")

        discard_url = _ita_url("menu", menu, "maintenance", "all")
        if payload:
            discard_resp = api_client.post(discard_url, json=payload)
            print(
                f"[CLEANUP] discard → status={discard_resp.status_code}"
                f" result={discard_resp.json().get('result')}"
                f" body={discard_resp.text}"
            )
