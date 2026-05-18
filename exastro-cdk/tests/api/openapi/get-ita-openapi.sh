#!/bin/bash
#
# Exastro ITA OpenAPI JSON 取得スクリプト
#
# 使用方法:
#   ./get-ita-openapi.sh
#
# 出力:
#   ita-openapi.yaml  - ITA API の OpenAPI 仕様 (YAML形式)
#   ita-openapi.json  - ITA API の OpenAPI 仕様 (JSON形式)
#

set -euo pipefail

CONTAINER_NAME="ita-api-organization"
CONTAINER_SPEC_PATH="/exastro/swagger/swagger.yaml"
OUTPUT_YAML="ita-openapi.yaml"
OUTPUT_JSON="ita-openapi.json"

echo "=== Exastro ITA OpenAPI 仕様書取得 ==="

# コンテナが起動しているか確認
if ! docker inspect "${CONTAINER_NAME}" > /dev/null 2>&1; then
  echo "[ERROR] コンテナ '${CONTAINER_NAME}' が見つかりません" >&2
  exit 1
fi

CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' "${CONTAINER_NAME}")
if [ "${CONTAINER_STATUS}" != "running" ]; then
  echo "[ERROR] コンテナ '${CONTAINER_NAME}' が起動していません (status: ${CONTAINER_STATUS})" >&2
  exit 1
fi

# swagger.yaml をコンテナからコピー
echo "[1/2] コンテナから OpenAPI 仕様書 (YAML) を取得中..."
docker cp "${CONTAINER_NAME}:${CONTAINER_SPEC_PATH}" "${OUTPUT_YAML}"
echo "      -> ${OUTPUT_YAML} ($(du -h "${OUTPUT_YAML}" | cut -f1))"

# YAML を JSON に変換
echo "[2/2] JSON 形式に変換中..."
python3 - <<'PYTHON'
import yaml, json, sys
from datetime import datetime, date

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

with open("ita-openapi.yaml", "r") as f:
    data = yaml.safe_load(f)

with open("ita-openapi.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, cls=DateEncoder)

print(f"      -> ita-openapi.json ({len(data.get('paths', {}))} paths)")
PYTHON

echo ""
echo "=== 完了 ==="
echo "  YAML: ${OUTPUT_YAML}"
echo "  JSON: ${OUTPUT_JSON}"
