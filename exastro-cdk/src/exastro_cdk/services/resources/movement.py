# exastro-cdk/src/exastro_cdk/services/resources/movement.py
# ITA上の Movement リソースに対するCRUD操作を担当する

import json
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

from exastro_cdk.models.manifest import MovementModel

_ORCHESTRATOR_MENU = {
    "ansible_legacy": "movement_list_ansible_legacy",
    "ansible_pioneer": "movement_list_ansible_pioneer",
    "ansible_role": "movement_list_ansible_role",
    "terraform_cloud_ep": "movement_list_terraform_cloud_ep",
}

_ORCHESTRATOR_LABEL = {
    "ansible_legacy": "Ansible Legacy",
    "ansible_pioneer": "Ansible Pioneer",
    "ansible_role": "Ansible Legacy Role",
    "terraform_cloud_ep": "Terraform Cloud/EP",
}

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates"


class MovementResource:
    """ITA Movement リソースの操作クラス."""

    def __init__(
        self,
        session: requests.Session,
        ita_base_url: str,
        ita_version: str = "v2.7",
    ) -> None:
        """MovementResource の初期化.

        Args:
            session: 認証済み requests.Session
            ita_base_url: ITA ベース URL (例: https://.../api/{org_id}/workspaces/{ws_id}/ita)
            ita_version: Exastro ITA のバージョン（テンプレートディレクトリ名に使用）
        """
        self._session = session
        self._ita_base_url = ita_base_url
        self._ita_version = ita_version
        self._jinja_env = Environment(
            loader=FileSystemLoader(_TEMPLATE_ROOT),
            keep_trailing_newline=True,
        )

    def create(self, movement: MovementModel) -> str:
        """Movement を ITA に登録し、払い出された movement_id を返す.

        Args:
            movement: 登録する Movement のモデル

        Returns:
            ITA が払い出した movement_id（UUID文字列）

        Raises:
            KeyError: movement.orchestrator が未知のオーケストレータ種別の場合、またはレスポンスに movement_id が含まれない場合
            requests.HTTPError: APIがエラーレスポンスを返した場合
        """
        orchestrator = getattr(movement, "orchestrator", "ansible_legacy")
        menu = _ORCHESTRATOR_MENU[orchestrator]
        url = f"{self._ita_base_url}/menu/{menu}/maintenance/all/"

        template_key = f"ita/{self._ita_version}/movement/{orchestrator}.json.j2"
        template = self._jinja_env.get_template(template_key)

        rendered = template.render(
            movement_name=movement.name,
            remarks=movement.description,
            orchestrator=_ORCHESTRATOR_LABEL.get(orchestrator),
            host_specific_format=movement.host_specific_format,
            delay_timer=None,
            header_section=None,
            ansible_cfg=None,
            optional_parameter=None,
            execution_environment=None,
            ansible_agent_execution_environment=None,
            ansibel_builder_options=None,
            winrm_connection=None,
        )

        body = json.loads(rendered)
        response = self._session.post(url, json=body)
        response.raise_for_status()
        data = response.json().get("data") or []
        return data[0]["parameter"]["movement_id"]
