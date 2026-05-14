# exastro-cdk/src/exastro_cdk/services/resources/movement.py
# ITA上の Movement リソースに対するCRUD操作を担当する

import requests

from exastro_cdk.models.manifest import MovementModel


class MovementResource:
    """ITA Movement リソースの操作クラス."""

    _PATH = "/ansible-legacy-role/movements"

    def __init__(self, session: requests.Session, ita_base_url: str) -> None:
        """MovementResource の初期化.

        Args:
            session: 認証済み requests.Session
            ita_base_url: ITA ベース URL (例: https://.../api/{org_id}/workspaces/{ws_id}/ita)
        """
        self._session = session
        self._url = f"{ita_base_url}{self._PATH}"

    def create(self, movement: MovementModel) -> None:
        """Movement を ITA に登録する.

        Args:
            movement: 登録する Movement のモデル

        Raises:
            requests.HTTPError: APIがエラーレスポンスを返した場合
        """
        body = {
            "file": {
                "ansible_cfg": None,
            },
            "parameter": {
                "movement_name": movement.name,
                "host_specific_format": "IP or Hostname",
                "header_section": (
                    "- hosts: all \n"
                    '  remote_user: "{{ __loginuser__ }}"\n'
                    "  gather_facts: no"
                ),
                "orchestrator": "Ansible Legacy Role",
                "delay_timer": 0,
                "remarks": movement.description,
                "ansible_builder_options": None,
                "ansible_agent_execution_environment": None,
                "operational_parameter": None,
                "execution_environment": None,
                "winrm_connection": None,
            },
        }
        response = self._session.post(self._url, json=body)
        response.raise_for_status()
