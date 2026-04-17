from typer.testing import CliRunner
from exastro_cdk.main import app

runner = CliRunner()

def test_init_command_args():
    """CLI引数が正しくエンジンに渡されるか（エラーにならないか）の疎通テスト"""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", ".", "--manifest", "non-existent.yaml"])
        # この時点ではファイルがないのでエラーになる設計なら、その挙動を確認
        assert result.exit_code != 0
