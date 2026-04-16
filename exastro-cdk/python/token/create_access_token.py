# exastro-cdk/python/token/create_access_token.py
import os
import sys
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

# 環境変数から値を取得
uri = os.getenv("BASE_URL")
organization_id = os.getenv("ORGANIZATION_ID")
refresh_token = os.getenv("REFRESH_TOKEN")

# API エンドポイント
endpoint = f"{uri}/auth/realms/{organization_id}/protocol/openid-connect/token"

# リクエストボディ
request_body = {
    "client_id": f"_{organization_id}-api",
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}

# APIリクエストを送信してアクセストークンを取得
response = requests.post(endpoint, data=request_body)

# レスポンスを確認
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Access Token:", access_token)
else:
    print("Failed to retrieve access token. Status Code:", response.status_code)
    print("Response:", response.text)
