from typer.testing import CliRunner

from exastro_cdk.main import app

runner = CliRunner()


def test_init_command_args():
    """CLI引数が正しくエンジンに渡されるか（エラーにならないか）の疎通テスト."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", ".", "--manifest", "non-existent.yaml"])
        # manifest が存在しない場合はデフォルト manifest を生成して正常終了する
        assert result.exit_code == 0
