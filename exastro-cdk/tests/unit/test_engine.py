from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import requests

from exastro_cdk.core.config import ConfigurationError, ExastroConfig, load_config
from exastro_cdk.core.engine import CDKEngine
from exastro_cdk.models.manifest import ManifestModel, MovementModel

_DUMMY_CONFIG = ExastroConfig(
    base_url="http://localhost:30080",
    organization="test-org",
    workspace="test-ws",
    refresh_token="dummy-refresh",
)


@pytest.fixture()
def temp_project_dir(tmp_path: Path) -> Path:
    """一時的なプロジェクトディレクトリ."""
    d = tmp_path / "my-test-project"
    d.mkdir()
    return d


@pytest.fixture()
def mock_manifest() -> ManifestModel:
    """テスト用 ManifestModel."""
    return ManifestModel(
        workspace_id="test-workspace",
        conductor={"name": "Test Flow", "description": "Desc"},
        movements=[
            MovementModel(name="test_role_1", description="desc 1"),
            MovementModel(name="test_role_2", description="desc 2"),
        ],
    )


class TestScaffoldLocalFiles:
    """_scaffold_local_files のテスト."""

    def test_creates_role_directories(
        self, temp_project_dir: Path, mock_manifest: ManifestModel
    ) -> None:
        """ManifestのMovement分だけAnsible Roleディレクトリが生成される."""
        engine = CDKEngine(temp_project_dir)
        engine._scaffold_local_files(mock_manifest)

        for movement in mock_manifest.movements:
            role_path = temp_project_dir / "ansible" / "roles" / movement.name
            assert (role_path / "tasks" / "main.yml").exists()
            assert (role_path / "defaults" / "main.yml").exists()

    def test_idempotent(
        self, temp_project_dir: Path, mock_manifest: ManifestModel
    ) -> None:
        """2回実行してもエラーにならない (exist_ok=True)."""
        engine = CDKEngine(temp_project_dir)
        engine._scaffold_local_files(mock_manifest)
        engine._scaffold_local_files(mock_manifest)  # 2回目もエラーなし


class TestCreateManifestFromTemplate:
    """_create_manifest / Stage1 のテスト."""

    def test_generates_manifest_yaml(self, temp_project_dir: Path) -> None:
        """初回 run_init_process で manifest.yaml が生成される."""
        engine = CDKEngine(temp_project_dir)
        engine.run_init_process()

        manifest_path = temp_project_dir / "manifest.yaml"
        assert manifest_path.exists()
        content = manifest_path.read_text(encoding="utf-8")
        assert "workspace_id" in content

    def test_stage1_does_not_call_ita(self, temp_project_dir: Path) -> None:
        """Stage1 (manifest.yaml なし) ではITA登録は行われない."""
        engine = CDKEngine(temp_project_dir)
        with patch("exastro_cdk.core.engine.load_config") as mock_load_config:
            engine.run_init_process()
            mock_load_config.assert_not_called()


class TestSyncInitialItaStructure:
    """_sync_initial_ita_structure のテスト."""

    def test_calls_create_movement_for_each_movement(
        self, temp_project_dir: Path, mock_manifest: ManifestModel
    ) -> None:
        """各MovementにつきITAClientのcreate_movementが1回ずつ呼ばれる."""
        engine = CDKEngine(temp_project_dir)
        mock_client = MagicMock()

        with (
            patch(
                "exastro_cdk.core.engine.fetch_access_token", return_value="dummy-token"
            ),
            patch("exastro_cdk.core.engine.ITAClient", return_value=mock_client),
        ):
            engine._sync_initial_ita_structure(mock_manifest, _DUMMY_CONFIG)

        assert mock_client.create_movement.call_count == 2
        calls = mock_client.create_movement.call_args_list
        assert calls[0] == call(mock_manifest.movements[0])
        assert calls[1] == call(mock_manifest.movements[1])

    def test_uses_manifest_workspace_id_for_ita_client(
        self, temp_project_dir: Path, mock_manifest: ManifestModel
    ) -> None:
        """manifest.workspace_id が config.workspace より優先してITAClientに渡される."""
        engine = CDKEngine(temp_project_dir)
        mock_client = MagicMock()

        with (
            patch("exastro_cdk.core.engine.fetch_access_token", return_value="tok"),
            patch(
                "exastro_cdk.core.engine.ITAClient", return_value=mock_client
            ) as patched_client,
        ):
            engine._sync_initial_ita_structure(mock_manifest, _DUMMY_CONFIG)

        _, kwargs = patched_client.call_args
        assert kwargs["workspace_id"] == "test-workspace"  # manifest の値

    def test_falls_back_to_config_workspace_when_manifest_workspace_is_none(
        self, temp_project_dir: Path
    ) -> None:
        """manifest.workspace_id が None の場合、config.workspace にフォールバックする."""
        manifest_no_ws = ManifestModel(
            workspace_id=None,  # type: ignore[arg-type]
            movements=[MovementModel(name="role_a")],
        )
        engine = CDKEngine(temp_project_dir)
        mock_client = MagicMock()

        with (
            patch("exastro_cdk.core.engine.fetch_access_token", return_value="tok"),
            patch(
                "exastro_cdk.core.engine.ITAClient", return_value=mock_client
            ) as patched_client,
        ):
            engine._sync_initial_ita_structure(manifest_no_ws, _DUMMY_CONFIG)

        _, kwargs = patched_client.call_args
        assert kwargs["workspace_id"] == "test-ws"  # config の値

    def test_http_error_propagates(
        self, temp_project_dir: Path, mock_manifest: ManifestModel
    ) -> None:
        """ITA APIがエラーを返した場合、HTTPError がそのまま伝播する."""
        engine = CDKEngine(temp_project_dir)
        mock_client = MagicMock()
        mock_client.create_movement.side_effect = requests.HTTPError("500 Server Error")

        with (
            patch("exastro_cdk.core.engine.fetch_access_token", return_value="tok"),
            patch("exastro_cdk.core.engine.ITAClient", return_value=mock_client),
        ):
            with pytest.raises(requests.HTTPError):
                engine._sync_initial_ita_structure(mock_manifest, _DUMMY_CONFIG)

    def test_fetch_access_token_called_with_config_values(
        self, temp_project_dir: Path, mock_manifest: ManifestModel
    ) -> None:
        """fetch_access_token が config の値で呼ばれる."""
        engine = CDKEngine(temp_project_dir)
        mock_client = MagicMock()

        with (
            patch(
                "exastro_cdk.core.engine.fetch_access_token", return_value="tok"
            ) as mock_fetch,
            patch("exastro_cdk.core.engine.ITAClient", return_value=mock_client),
        ):
            engine._sync_initial_ita_structure(mock_manifest, _DUMMY_CONFIG)

        mock_fetch.assert_called_once_with(
            _DUMMY_CONFIG.base_url,
            _DUMMY_CONFIG.organization,
            _DUMMY_CONFIG.refresh_token,
        )


class TestRunInitProcessStage2:
    """run_init_process Stage2 の統合テスト."""

    def test_stage2_calls_sync_ita(self, temp_project_dir: Path) -> None:
        """manifest.yaml が存在する場合、_sync_initial_ita_structure が呼ばれる."""
        # manifest.yaml を事前に作成 (Stage2 の前提条件)
        manifest_content = """\
workspace_id: test-ws
conductor:
  name: Test Conductor
  description: テスト
movements:
  - name: role_a
    description: Role A
    orchestrator: ansible_legacy
"""
        (temp_project_dir / "manifest.yaml").write_text(
            manifest_content, encoding="utf-8"
        )

        engine = CDKEngine(temp_project_dir)
        dummy_config = _DUMMY_CONFIG

        with (
            patch("exastro_cdk.core.engine.load_config", return_value=dummy_config),
            patch.object(engine, "_sync_initial_ita_structure") as mock_sync,
        ):
            engine.run_init_process()

        mock_sync.assert_called_once()
        manifest_arg: ManifestModel = mock_sync.call_args.args[0]
        assert manifest_arg.workspace_id == "test-ws"
        assert len(manifest_arg.movements) == 1
        assert manifest_arg.movements[0].name == "role_a"


class TestLoadConfig:
    """load_config のテスト."""

    def test_loads_all_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """環境変数がすべて揃っている場合、ExastroConfig が正しく返る."""
        monkeypatch.setenv("EXASTRO_BASE_URL", "http://test:80")
        monkeypatch.setenv("EXASTRO_ORGANIZATION", "my-org")
        monkeypatch.setenv("EXASTRO_WORKSPACE", "my-ws")
        monkeypatch.setenv("REFRESH_TOKEN", "my-token")

        config = load_config()

        assert config.base_url == "http://test:80"
        assert config.organization == "my-org"
        assert config.workspace == "my-ws"
        assert config.refresh_token == "my-token"

    @pytest.mark.parametrize(
        "missing_var",
        [
            "EXASTRO_BASE_URL",
            "EXASTRO_ORGANIZATION",
            "EXASTRO_WORKSPACE",
            "REFRESH_TOKEN",
        ],
    )
    def test_missing_env_var_raises_configuration_error(
        self, monkeypatch: pytest.MonkeyPatch, missing_var: str
    ) -> None:
        """必須環境変数が欠けていると ConfigurationError が発生する."""
        all_vars = {
            "EXASTRO_BASE_URL": "http://test:80",
            "EXASTRO_ORGANIZATION": "my-org",
            "EXASTRO_WORKSPACE": "my-ws",
            "REFRESH_TOKEN": "my-token",
        }
        for k, v in all_vars.items():
            monkeypatch.setenv(k, v)
        monkeypatch.delenv(missing_var)

        with pytest.raises(ConfigurationError, match=missing_var):
            load_config()

    def test_empty_env_var_raises_configuration_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """空文字の環境変数も未設定とみなして ConfigurationError が発生する."""
        monkeypatch.setenv("EXASTRO_BASE_URL", "")
        monkeypatch.setenv("EXASTRO_ORGANIZATION", "my-org")
        monkeypatch.setenv("EXASTRO_WORKSPACE", "my-ws")
        monkeypatch.setenv("REFRESH_TOKEN", "my-token")

        with pytest.raises(ConfigurationError, match="EXASTRO_BASE_URL"):
            load_config()
