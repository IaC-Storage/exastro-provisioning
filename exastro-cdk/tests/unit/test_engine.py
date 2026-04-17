import pytest
from unittest.mock import patch
from exastro_cdk.core.engine import CDKEngine
from exastro_cdk.models.manifest import ManifestModel, MovementModel

@pytest.fixture
def temp_project_dir(tmp_path):
    """一時的なプロジェクトディレクトリを作成するフィクスチャ"""
    return tmp_path / "my-test-project"

@pytest.fixture
def mock_manifest():
    """テスト用のダミーManifestデータ"""
    return ManifestModel(
        project_id="test-id",
        conductor={"name": "Test Flow", "description": "Desc"},
        movements=[
            MovementModel(name="test_role_1", description="desc 1"),
            MovementModel(name="test_role_2", description="desc 2")
        ]
    )

class TestCDKEngine:
    
    def test_scaffold_local_files(self, temp_project_dir, mock_manifest):
        """ローカルのディレクトリ構造とファイルが正しく生成されるかテスト"""
        engine = CDKEngine(temp_project_dir)
        
        # 実行
        engine.scaffold_local_files(mock_manifest)
        
        # 検証: 各ロールのディレクトリが存在するか
        for movement in mock_manifest.movements:
            role_path = temp_project_dir / "ansible" / "roles" / movement.name
            assert role_path.exists()
            assert (role_path / "tasks" / "main.yml").exists()
            assert (role_path / "defaults" / "main.yml").exists()

    def test_create_manifest_from_template(self, temp_project_dir):
        """テンプレートからmanifest.yamlが正しくレンダリングされるかテスト"""
        engine = CDKEngine(temp_project_dir)
        temp_project_dir.mkdir()
        
        # 実行
        engine.create_manifest(project_id="web-v1", conductor_name="WebDeploy")
        
        manifest_file = temp_project_dir / "manifest.yaml"
        assert manifest_file.exists()
        
        content = manifest_file.read_text()
        assert 'project_id: "web-v1"' in content
        assert 'name: "WebDeploy"' in content

    @patch("exastro_cdk.core.engine.ITAClient")
    def test_sync_initial_ita_structure(self, mock_ita_class, temp_project_dir, mock_manifest):
        """ITA API呼び出しが正しい引数で行われるかテスト (Mock使用)"""
        # Mockの準備
        mock_ita_instance = mock_ita_class.return_value
        engine = CDKEngine(temp_project_dir)
        
        # 実行
        engine.sync_initial_ita_structure(mock_manifest)
        
        # 検証: Movement作成APIがロール数分呼ばれたか
        assert mock_ita_instance.create_movement.call_count == len(mock_manifest.movements)
        # 検証: Conductor作成APIが1回呼ばれたか
        assert mock_ita_instance.create_conductor.called
