# exastro-cdk/src/exastro_cdk/services/resources/conductor.py
# ITA上の Conductor リソースに対するCRUD操作を担当する
# TODO: ConductorModel が定義され次第、型を dict から ConductorModel に切り替える

import requests


class ConductorResource:
    """ITA Conductor リソースの操作クラス."""

    _PATH = "/conductors"

    def __init__(self, session: requests.Session, ita_base_url: str) -> None:
        """ConductorResource の初期化.

        Args:
            session: 認証済み requests.Session
            ita_base_url: ITA ベース URL (例: https://.../api/{org_id}/workspaces/{ws_id}/ita)
        """
        self._session = session
        self._url = f"{ita_base_url}{self._PATH}"

    def create(self, conductor: dict) -> None:
        """Conductor を ITA に登録する.

        Args:
            conductor: 登録する Conductor の情報 (dict)

        Raises:
            requests.HTTPError: APIがエラーレスポンスを返した場合
        """
        # TODO: conductor dict → APIリクエストボディへのマッピングを実装する
        # 参照: docs/specs/ita-api-reference.md #3-Conductor
        response = self._session.post(self._url, json=conductor)
        response.raise_for_status()
