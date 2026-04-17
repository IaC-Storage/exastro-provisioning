# exastro-cdk/src/movement/create_movement.py
import os
import sys
import json
import requests
from dotenv import load_dotenv

WORKSPACE_ID = "sandbox"  # 対象のワークスペースID
MENU_ID = "example-menu"  # 対象のメニューID

# .envファイルから環境変数を読み込む
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

# 環境変数から値を取得
uri = os.getenv("BASE_URL")
organization_id = os.getenv("ORGANIZATION_ID")
refresh_token = os.getenv("REFRESH_TOKEN")

# API エンドポイント
endpoint = f"{uri}/api/{organization_id}/workspaces/{WORKSPACE_ID}/ita/menu/{MENU_ID}/maintenance"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"
}

# リクエストボディ, ./request_bodies/rq_body_create_movement.json から読み込む
with open("./request_bodies/rq_body_create_movement.json", "r") as f:
    request_body = json.load(f)

# APIリクエストを送信してアクセストークンを取得
response = requests.post(endpoint, json=request_body, headers=headers)

# レスポンスを確認
if response.status_code == 201:
    print("Movement created successfully.")
else:
    print("Failed to create movement. Status Code:", response.status_code)
    print("Response:", response.text)
