# exastro-cdk/src/exastro_cdk/core/engine.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


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

    def create_manifest(self, project_id: str, conductor_name: str):
        """マニフェストファイルを生成します."""
        template = self.env.get_get_template("manifest.yaml.j2")
        
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
