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
        # 1. manifestの準備 (Jinja2テンプレートからの生成など)
        engine.create_manifest(project_id=path.name, conductor_name=f"{path.name}_conductor")

        # 2. ローカルディレクトリの作成
        engine.scaffold_local_files(manifest=None)

        # 3. ITAへの初期登録
        engine.init_exastro(manifest_path=manifest)
        
        rprint("[bold green]✔ 初期化が完了しました！[/bold green]")
        rprint("次に `ansible/roles/` 内でRoleを開発し、`exastro-cdk build-schema` を実行してください。")
        
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)