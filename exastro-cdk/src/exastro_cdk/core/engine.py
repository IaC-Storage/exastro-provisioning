# exastro-cdk/src/exastro_cdk/core/engine.py
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader

from exastro_cdk.core.config import ExastroConfig, load_config
from exastro_cdk.models.manifest import ManifestModel, MovementModel
from exastro_cdk.services.ita_client import ITAClient
from exastro_cdk.services.token import fetch_access_token


class CDKEngine:
    """Exastro CDKコアエンジン.

    このクラスはCLIコマンドから呼び出され、プロジェクトの初期化やビルド処理を担当します.
    """

    def __init__(self, project_path: Path):
        """CDKEngineの初期化."""
        self.project_path = project_path
        # 各種テンプレートが格納されているディレクトリを指定
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def run_init_process(self, manifest_path: Path | None = None) -> None:
        """プロジェクトの初期化プロセスを実行します."""
        target_manifest = self.project_path / "manifest.yaml"

        # 1. manifest.yaml の準備
        if manifest_path and manifest_path.exists():
            # 外部マニフェストが指定された場合はコピー（または読み込み）
            import shutil

            shutil.copy(manifest_path, target_manifest)
        elif not target_manifest.exists():
            # 存在しない場合はテンプレートから作成
            # TODO: 将来的には対話型(Interactive)で workspace_id 等を受け取る
            self._create_manifest(
                workspace_id="new-workspace", conductor_name="Default Conductor"
            )

            return  # ここで終了。次のステップはユーザーが manifest.yaml を編集してから実行する想定

        # 2. ロードとバリデーション
        manifest_data = self._load_and_validate(target_manifest)

        # 3. ローカルディレクトリ(Ansible Roles)の作成
        self._scaffold_local_files(manifest_data)

        # 4. ITAへの初期登録
        config = load_config()
        self._sync_initial_ita_structure(manifest_data, config)

    def _create_manifest(self, workspace_id: str, conductor_name: str) -> None:
        """テンプレートからマニフェストファイルを生成します.

        Args:
            workspace_id: ワークスペースID
            conductor_name: Conductorの名前
        """
        template = self.env.get_template("manifest.yaml.j2")

        # テンプレートに渡す変数
        context = {
            "workspace_id": workspace_id,
            "conductor_name": conductor_name,
            "conductor_description": f"{conductor_name} の自動構築フロー",
            "movements": [
                {"name": "os_setup", "description": "OS基本設定"},
                {"name": "apache_install", "description": "Apacheインストール"},
            ],
        }

        rendered_content = template.render(context)

        # ローカルに保存
        manifest_path = self.project_path / "manifest.yaml"
        manifest_path.write_text(rendered_content, encoding="utf-8")

    def _load_and_validate(self, path: Path) -> ManifestModel:
        """マニフェストファイルを読み込み、バリデーションを行います."""
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 現状の dataclass モデルを使用してマッピング
        # 本格的なバリデーションには Pydantic への移行を推奨
        movements = [MovementModel(**m) for m in data.get("movements", [])]
        return ManifestModel(
            workspace_id=data.get("workspace_id"),
            conductor=data.get("conductor", {}),
            movements=movements,
        )

    def _sync_initial_ita_structure(
        self, manifest: ManifestModel, config: ExastroConfig
    ) -> None:
        """ManifestのMovement定義をITAに一括登録する.

        Args:
            manifest: バリデーション済みの ManifestModel
            config: 環境変数から読み込んだ ExastroConfig

        Raises:
            ConfigurationError: 必須環境変数が未設定の場合
            requests.HTTPError: ITA APIがエラーを返した場合
        """
        access_token = fetch_access_token(
            config.base_url, config.organization, config.refresh_token
        )

        # manifest.workspace_id が設定されていればITAターゲットとして優先
        workspace = manifest.workspace_id or config.workspace

        client = ITAClient(
            base_url=config.base_url,
            organization_id=config.organization,
            workspace_id=workspace,
            access_token=access_token,
        )

        registered: list[str] = []  # Task 2-b で movement_id を収集予定
        for movement in manifest.movements:
            client.create_movement(movement)
            registered.append(movement.name)

        print(f"登録完了: {len(registered)} 件のMovementをITAに登録しました。")
        for name in registered:
            print(f"  - {name}")

    def _scaffold_local_files(self, manifest: ManifestModel) -> None:
        """マニフェストに基づいてローカルのディレクトリ構造を生成します."""
        for movement in manifest.movements:
            role_path = self.project_path / "ansible" / "roles" / movement.name
            (role_path / "tasks").mkdir(parents=True, exist_ok=True)
            (role_path / "defaults").mkdir(parents=True, exist_ok=True)
            (role_path / "tasks" / "main.yml").touch()
            (role_path / "defaults" / "main.yml").touch()
