自動化ジョブフローの作成には次の作業が必要だが、直感的でないためCDKでは宣言的定義から自動生成することを目指す。

---

1. Initialize: exastro-cdk init --target-usecase middleware-installation
   - 必要なディレクトリ構造と、manifest.yaml テンプレートが生成される。
2. Define: manifest.yaml に 「やりたい作業」のリストを記述。
3. Generate: exastro-cdk generate
   - manifest.yaml をもとに、MovementやConductorのJSON定義ファイルが生成される。
4. Develop: ansible/roles/ 以下に Playbook を記述。
5. Apply: exastro-cdk apply
   - Movement作成 → Roleアップロード → 紐付け → Conductor作成 が一気に走る。
   - CLI出力: "Conductor created! UI layout might be messy. Check here: [URL]"
6. Run: exastro-cdk run --op "First Deploy" --inventory target_hosts.yaml

**manifest.yamlサンプル**
```yaml
# manifest.yaml
project_id: "web-app-v1"
conductor:
  name: "WEBサーバ構築フロー"
  description: "Apacheのインストールと設定"

# 開発者が「やりたい作業」のリスト
movements:
  - name: "os_setup"
    description: "OS基本設定"
  - name: "apache_install"
    description: "Apacheインストール"
  - name: "apache_config"
    description: "設定ファイル配置"
```

**パラメータ自動抽出**
```yaml
# ansible/roles/apache_install/defaults/main.yml
# コメントアノテーション を活用することで型の検出を可能にする
# @cdk-type: integer
# @cdk-description: 待受ポート番号
http_port: 80
```

### ジョブフローの作成
1. Movement作成
2. Conductor作成 (作成したMovementをノードとして紐付け)
   - ノードの座標の自動計算は難しい可能性が高い
   - CDKでは作成するConductorのLinkをユーザへ提示、ユーザが更新してからJSONで取り込むなどの方法も検討
   - あるいはGitHubの対象リポジトリをリバースエンジニアリングするか
3. Ansible Playbook/Roleの作成
   - ディレクトリ構造をテンプレート化するためAnsible Roleに限定
   - `init`ディレクトリを作成してファイルを配置する (ansible-galaxy init も活用)
   - ユーザがRoleを作成し終わったら`sync`コマンドでアップロード
4. Movement-Playbookの紐付け
5. Parameter Sheetの作成
6. Parameter SheetとPlaybook変数の紐付け


### ジョブフローの実行
1. 作業対象ホストの登録
2. Operation作成
3. Parameter Sheetへ値を入力
4. 指定したオペレーションでConductorを実行
