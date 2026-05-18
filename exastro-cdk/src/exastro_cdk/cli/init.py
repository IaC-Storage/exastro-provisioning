# exastro-cdk/src/exastro_cdk/cli/init.py
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich import print as rprint

from exastro_cdk.core.engine import CDKEngine

app = typer.Typer()


@app.command()
def project(
    path: Annotated[Path, typer.Argument(help="初期化するディレクトリパス")] = Path(
        "."
    ),
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest", "-m", help="既存のmanifest.yamlを使用する場合のパス"
        ),
    ] = None,
    env_file: Annotated[
        Path | None,
        typer.Option(
            "--env-file",
            "-e",
            help="接続情報を記載した .env ファイルのパス",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
):
    """新規プロジェクトの初期化を行います."""
    if env_file:
        load_dotenv(env_file, override=True)
        rprint(f"[dim]Loaded env file:[/dim] {env_file}")

    rprint(
        f"[bold blue]Initializing Exastro CDK project at:[/bold blue] {path.absolute()}"
    )

    try:
        engine = CDKEngine(path)
        engine.run_init_process(manifest_path=manifest)

    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1) from e
