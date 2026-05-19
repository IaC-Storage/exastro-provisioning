from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from exastro_cdk.main import app

runner = CliRunner()


def test_init_command_args():
    """CLI引数が正しくエンジンに渡されるか（エラーにならないか）の疎通テスト."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", ".", "--manifest", "non-existent.yaml"])
        # manifest が存在しない場合はデフォルト manifest を生成して正常終了する
        assert result.exit_code == 0


def test_init_stage1_creates_manifest():
    """manifest.yaml が存在しない場合、Stage1 で生成されて exit 0 になる."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "."])
        assert result.exit_code == 0
        assert Path("manifest.yaml").exists()


def test_init_with_env_file_loads_env():
    """`--env-file` オプション指定時に load_dotenv が呼ばれる."""
    with runner.isolated_filesystem():
        # テスト用 .env ファイルを作成
        Path("test.env").write_text(
            "EXASTRO_BASE_URL=http://test:80\n", encoding="utf-8"
        )

        with patch("exastro_cdk.cli.init.load_dotenv") as mock_load_dotenv:
            result = runner.invoke(app, ["init", ".", "--env-file", "test.env"])

        mock_load_dotenv.assert_called_once()
        call_kwargs = mock_load_dotenv.call_args
        # load_dotenv の第1引数が env_file パスであること
        assert "test.env" in str(call_kwargs.args[0])
        assert result.exit_code == 0


def test_init_engine_error_exits_with_code_1():
    """エンジン処理で例外が発生した場合、exit code 1 で終了する."""
    with runner.isolated_filesystem():
        with patch("exastro_cdk.cli.init.CDKEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine.run_init_process.side_effect = RuntimeError(
                "something went wrong"
            )
            mock_engine_cls.return_value = mock_engine

            result = runner.invoke(app, ["init", "."])

        assert result.exit_code == 1


def test_init_with_manifest_option_passes_path_to_engine():
    """`--manifest` オプションで指定したパスがエンジンに渡される."""
    with runner.isolated_filesystem():
        manifest_path = Path("my_manifest.yaml")
        manifest_path.write_text(
            "workspace_id: ws-1\nconductor: {}\nmovements: []\n", encoding="utf-8"
        )

        with patch("exastro_cdk.cli.init.CDKEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            runner.invoke(app, ["init", ".", "--manifest", "my_manifest.yaml"])

        call_kwargs = mock_engine.run_init_process.call_args
        passed_path = call_kwargs.kwargs.get("manifest_path") or call_kwargs.args[0]
        assert "my_manifest.yaml" in str(passed_path)


@pytest.mark.parametrize("missing_env_file", ["nonexistent.env"])
def test_init_with_nonexistent_env_file_fails(missing_env_file: str):
    """`--env-file` に存在しないファイルを指定するとエラーになる."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", ".", "--env-file", missing_env_file])
        assert result.exit_code != 0
