# tests/unit/test_movement_resource.py
from unittest.mock import MagicMock

import pytest
import requests

from exastro_cdk.models.manifest import MovementModel
from exastro_cdk.services.resources.movement import MovementResource

_BASE_URL = "http://localhost:30080/api/test-org/workspaces/test-ws/ita"


def _make_resource(mock_session: MagicMock) -> MovementResource:
    return MovementResource(session=mock_session, ita_base_url=_BASE_URL)


def _make_mock_session() -> MagicMock:
    session = MagicMock(spec=requests.Session)
    session.post.return_value.raise_for_status = MagicMock()
    return session


class TestMovementResourceCreate:
    """MovementResource.create() の単体テスト."""

    @pytest.mark.parametrize(
        ("orchestrator", "expected_menu"),
        [
            ("ansible_role", "movement_list_ansible_role"),
            ("ansible_legacy", "movement_list_ansible_legacy"),
            ("ansible_pioneer", "movement_list_ansible_pioneer"),
            ("terraform_cloud_ep", "movement_list_terraform_cloud_ep"),
        ],
    )
    def test_posts_to_correct_menu_url(
        self, orchestrator: str, expected_menu: str
    ) -> None:
        """各 orchestrator 種別に対して正しいメニュー URL に POST する."""
        mock_session = _make_mock_session()
        resource = _make_resource(mock_session)
        movement = MovementModel(name="my_role", orchestrator=orchestrator)

        resource.create(movement)

        url = mock_session.post.call_args.args[0]
        assert expected_menu in url
        assert url.startswith(_BASE_URL)
        assert url.endswith("/maintenance/all/")

    def test_posts_rendered_json_body(self) -> None:
        """JSON ボディに movement_name・discard・host_specific_format が含まれる."""
        mock_session = _make_mock_session()
        resource = _make_resource(mock_session)
        movement = MovementModel(
            name="os_setup",
            description="OS基本設定",
            orchestrator="ansible_role",
            host_specific_format="IP",
        )

        resource.create(movement)

        body = mock_session.post.call_args.kwargs["json"]
        assert isinstance(body, list)
        assert len(body) == 1
        param = body[0]["parameter"]
        assert param["movement_name"] == "os_setup"
        assert param["discard"] == "0"
        assert param["host_specific_format"] == "IP"

    def test_http_error_propagates(self) -> None:
        """ITA API がエラーを返した場合、HTTPError がそのまま伝播する."""
        mock_session = _make_mock_session()
        mock_session.post.return_value.raise_for_status.side_effect = (
            requests.HTTPError("500 Internal Server Error")
        )
        resource = _make_resource(mock_session)
        movement = MovementModel(name="role_a")

        with pytest.raises(requests.HTTPError):
            resource.create(movement)

    def test_unknown_orchestrator_raises_key_error(self) -> None:
        """未知の orchestrator 名を指定すると KeyError が発生する."""
        mock_session = _make_mock_session()
        resource = _make_resource(mock_session)
        movement = MovementModel(name="role_a", orchestrator="unknown_type")

        with pytest.raises(KeyError):
            resource.create(movement)

    def test_raise_for_status_is_called(self) -> None:
        """POST 成功後に raise_for_status() が呼ばれる."""
        mock_session = _make_mock_session()
        resource = _make_resource(mock_session)
        movement = MovementModel(name="role_b")

        resource.create(movement)

        mock_session.post.return_value.raise_for_status.assert_called_once()

    def test_description_is_passed_as_remarks(self) -> None:
        """movement.description が remarks として JSON ボディに渡される."""
        mock_session = _make_mock_session()
        resource = _make_resource(mock_session)
        movement = MovementModel(name="role_c", description="テスト説明")

        resource.create(movement)

        body = mock_session.post.call_args.kwargs["json"]
        param = body[0]["parameter"]
        assert param["remarks"] == "テスト説明"
