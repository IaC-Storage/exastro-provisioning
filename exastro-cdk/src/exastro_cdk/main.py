# exastro-cdk/src/exastro_cdk/main.py
# CLIエントリーポイント (Typer/Click)

import typer

from exastro_cdk.cli import apply, build, init

# メインのTyperアプリ作成
app = typer.Typer(
    help="Exastro CDK: Exastro ITA の構成管理をコードで自動化するツール",
    add_completion=False,
)

# 各サブコマンドモジュールを登録
app.command(name="init", help="プロジェクトを初期化し、ITAへ基本構成を登録します")(
    init.project
)
app.add_typer(
    build.app,
    name="build-schema",
    help="Roleからパラメータシートの定義を自動抽出します",
)
app.add_typer(
    apply.app, name="apply", help="ITA側の設定を最終的な状態に同期（デプロイ）します"
)


# バージョン表示用のコールバック
def version_callback(value: bool) -> None:
    """バージョン情報を表示するコールバック."""
    if value:
        # 実際にはパッケージのバージョンを取得するロジックに置き換え
        typer.echo("Exastro CDK version: 0.1.0 (Phase.1 MVP)")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="バージョン情報を表示",
    ),
):
    """Exastro CDK - Single Source of Truth for Exastro IT Automation."""
    pass


if __name__ == "__main__":
    app()
