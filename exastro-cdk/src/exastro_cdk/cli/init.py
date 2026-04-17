# exastro-cdk/src/exastro_cdk/cli/init.py
import typer
from typing import Optional
from pathlib import Path
from exastro_cdk.core.engine import CDKEngine

app = typer.Typer()

@app.command()
def init(
    project_path: Path = typer.Argument(Path("."), help="プロジェクトを作成するパス"),
    manifest: Optional[Path] = typer.Option(None, "--manifest", "-m", help="既存のmanifest.yamlのパス"),
):
    """
    Exastro CDK プロジェクトを初期化しITAへ基本構成を登録します.
    """
    engine = CDKEngine(project_path)
    
    # 1. Manifestの読み込みまたは生成
    manifest_data = engine.prepare_manifest(manifest)
    
    # 2. ローカルディレクトリ（Ansible Roles等）の生成
    engine.scaffold_local_files(manifest_data)
    
    # 3. ITAへの初期登録 (Movement/Conductor)
    engine.sync_initial_ita_structure(manifest_data)
    
    typer.echo(f"Successfully initialized: {project_path}")
