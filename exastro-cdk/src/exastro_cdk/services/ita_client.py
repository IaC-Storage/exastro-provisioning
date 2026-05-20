# exastro-cdk/src/exastro_cdk/services/ita_client.py
# ITA APIとの通信を担当するFacade
# 各リソースの実装は services/resources/ 配下に分離されている

import requests

from exastro_cdk.models.manifest import MovementModel
from exastro_cdk.services.resources import ConductorResource, MovementResource


class ITAClient:
    """ITA (IT Automation) APIクライアントのFacade.

    各リソース操作はリソース別クラス (MovementResource, ConductorResource) に委譲する。
    呼び出し側は本クラスのメソッドのみを使用し、内部実装の詳細を意識しない。
    """

    def __init__(
        self,
        base_url: str,
        organization_id: str,
        workspace_id: str,
        access_token: str,
    ) -> None:
        """ITAClient の初期化.

        Args:
            base_url: Exastro のベース URL (例: https://exastro.example.com)
            organization_id: オーガナイゼーション ID
            workspace_id: ワークスペース ID
            access_token: Bearer アクセストークン
        """
        session = requests.Session()
        session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )
        ita_base_url = f"{base_url}/api/{organization_id}/workspaces/{workspace_id}/ita"

        self.movement = MovementResource(session, ita_base_url)
        self.conductor = ConductorResource(session, ita_base_url)

    def create_movement(self, movement: MovementModel) -> str:
        """MovementをITAに登録し、払い出された movement_id を返す."""
        return self.movement.create(movement)

    def create_conductor(self, conductor: dict) -> None:
        """ConductorをITAに登録する."""
        self.conductor.create(conductor)
