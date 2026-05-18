"""Exastro IT Automation API テスト共通設定."""

import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

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
def created_movements() -> list:
    """テスト中に作成したMovementを (menu, name) のタプルで記録するリスト."""
    return []


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_movements(api_client, created_movements):
    """テストセッション全体の前後で、作成したMovementをクリーンアップする."""
    yield

    if not created_movements:
        return

    # menu ごとに対象Movementをまとめてフィルタ → Delete
    from itertools import groupby

    sorted_items = sorted(created_movements, key=lambda x: x[0])
    for menu, entries in groupby(sorted_items, key=lambda x: x[0]):
        names = [name for _, name in entries]
        filter_url = _ita_url("menu", menu, "filter")
        resp = api_client.post(
            filter_url + "?file=no", json={"movement_name": {"LIST": names}}
        )
        if resp.status_code != 200:
            continue

        items = resp.json().get("data") or []
        if not items:
            continue

        delete_url = _ita_url("menu", menu, "maintenance", "all")
        payload = [
            {"type": "Delete", "parameter": {"uuid": item["parameter"]["uuid"]}}
            for item in items
            if item.get("parameter", {}).get("uuid")
        ]
        if payload:
            api_client.post(delete_url, json=payload)
