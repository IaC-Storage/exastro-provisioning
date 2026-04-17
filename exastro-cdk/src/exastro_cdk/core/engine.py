# exastro-cdk/src/exastro_cdk/core/engine.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from exastro_cdk.models.manifest import ManifestModel
from exastro_cdk.services.ita_client import ITAClient


class CDKEngine:
    """Exastro CDKコアエンジン.
    
    このクラスはCLIコマンドから呼び出され、プロジェクトの初期化やビルド処理を担当します.
    """
    def __init__(self, project_path: Path):
        """CDKEngineの初期化."""
        self.project_path = project_path
        # テンプレートディレクトリの指定
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def create_manifest(self, project_id: str, conductor_name: str) -> None:
        """マニフェストファイルを生成します."""
        template = self.env.get_template("manifest.yaml.j2")
        
        # テンプレートに渡す変数
        context = {
            "project_id": project_id,
            "conductor_name": conductor_name,
            "conductor_description": f"{conductor_name} の自動構築フロー",
            "movements": [
                {"name": "os_setup", "description": "OS基本設定"},
                {"name": "apache_install", "description": "Apacheインストール"}
            ]
        }
        
        rendered_content = template.render(context)
        
        # ローカルに保存
        manifest_path = self.project_path / "manifest.yaml"
        manifest_path.write_text(rendered_content, encoding="utf-8")

    def scaffold_local_files(self, manifest: ManifestModel) -> None:
        """マニフェストに基づいてローカルのディレクトリ構造を生成します."""
        for movement in manifest.movements:
            role_path = self.project_path / "ansible" / "roles" / movement.name
            (role_path / "tasks").mkdir(parents=True, exist_ok=True)
            (role_path / "defaults").mkdir(parents=True, exist_ok=True)
            (role_path / "tasks" / "main.yml").touch()
            (role_path / "defaults" / "main.yml").touch()

    def sync_initial_ita_structure(self, manifest: ManifestModel) -> None:
        """マニフェストの内容をITAに同期します."""
        client = ITAClient()
        for movement in manifest.movements:
            client.create_movement(movement)
        client.create_conductor(manifest.conductor)

