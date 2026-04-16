# exastro-cdk/python/workspace/create_workspace.py

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

# 固定パラメータ
endpoint = f"{uri}/api/{organization_id}/platform/workspaces"

# ユーザ可変パラメータ
workspace_id = "sandbox"
workspace_name = "sandbox"
description = "sandbox environment"  # ワークスペースの説明を指定

# 環境 最大40文字 / 使用可能文字：全角・半角文字
environments = [""]

# ワークスペース管理者のリストを指定, ユーザー名から取得する必要あり
workspace_administrators = [
    {
        "id": "0165db47-0b43-412f-bb20-366ba79c3655"
    }
]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"
}

request_body = {
  "id": workspace_id,
  "name": workspace_name,
  "informations": {
    "description": description,
    # "environments": environments,
    "workspace_administrators": workspace_administrators
  }
}

# APIリクエストを送信してワークスペースを作成
response = requests.post(endpoint, json=request_body, headers=headers)

# レスポンスを確認
if response.status_code == 201:
    print("Workspace created successfully.")
else:
    print("Failed to create workspace. Status Code:", response.status_code)
    print("Response:", response.text)
