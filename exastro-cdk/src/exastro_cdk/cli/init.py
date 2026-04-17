# exastro-cdk/src/exastro_cdk/cli/init.py
import typer
from pathlib import Path
from typing import Optional
from rich import print as rprint
from exastro_cdk.core.engine import CDKEngine

app = typer.Typer()

@app.command()
def project(
    path: Path = typer.Argument(".", help="初期化するディレクトリパス"),
    manifest: Optional[Path] = typer.Option(None, "--manifest", "-m", help="既存のmanifest.yamlを使用する場合のパス"),
):
    """
    新規プロジェクトの初期化を行います。
    """
    rprint(f"[bold blue]Initializing Exastro CDK project at:[/bold blue] {path.absolute()}")
    
    try:
        engine = CDKEngine(path)
        engine.run_init_process(manifest_path=manifest)
        
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)