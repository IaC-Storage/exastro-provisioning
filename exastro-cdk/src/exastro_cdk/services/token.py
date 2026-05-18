import requests


def fetch_access_token(base_url: str, organization: str, refresh_token: str) -> str:
    """リフレッシュトークンを使ってアクセストークンを取得する.

    Args:
        base_url: Exastro ベースURL (例: http://192.168.10.70:80)
        organization: オーガナイゼーションID (Keycloak realm名として使用)
        refresh_token: 長期有効なリフレッシュトークン

    Returns:
        短期有効なアクセストークン文字列

    Raises:
        requests.HTTPError: トークン交換APIがエラーを返した場合
    """
    endpoint = f"{base_url}/auth/realms/{organization}/protocol/openid-connect/token"
    resp = requests.post(
        endpoint,
        data={
            "client_id": f"_{organization}-api",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]
