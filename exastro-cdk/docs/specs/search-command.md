# search コマンド仕様

## 1. Why：コマンドの目的と価値

標準Playbookライブラリ（playbook-collection-docs）に収録されたAnsible Roleを、ITA上のMovementとして検索・発見し、`manifest.yaml` へ追記する手間を最小化することが目的です。

* **Playbookの再利用促進**: 既存の標準Playbookをキーワード・タグで素早く発見することで、ゼロから実装するコストを削減します。
* **manifest.yaml への直接統合**: 検索結果をそのまま `manifest.yaml` の `movements` セクションへ対話形式で追記できます。
* **スキルハードルの低下**: ITA Web UIや playbook-collection-docs のリポジトリを手動で調べなくても、CLIから一気通貫で探せます。

---

## 2. What：仕様の詳細

### A. 前提条件

対象ワークスペースに [exastro-suite/playbook-collection-docs](https://github.com/exastro-suite/playbook-collection-docs/tree/master/ansible_role_templates) の Ansible Playbook（ansible_role_templates）があらかじめインポートされていること。

インポート済みのMovement一覧をITA APIで取得し、ローカルで検索・フィルタリングを行います。

> **TODO:** 検索インデックスをローカルにキャッシュするか、毎回ITA APIを叩くかを決定する。ワークスペースのMovement数によってはAPIが重くなる可能性がある。

### B. 検索対象フィールド

| フィールド | 説明 |
| :--- | :--- |
| **Movement名** | `ansible_role_OS-RH_setup_nginx` のようなID |
| **説明文** | Movement に付与された description |
| **タグ** | Movement に付与されたタグ（ITA上でどう管理されるか要確認） |

> **TODO:** ITA APIのMovement取得レスポンスにdescriptionやタグが含まれるか確認が必要。含まれない場合は playbook-collection-docs のメタデータ（READMEやYAMLヘッダ）をsidecarとして取り込む仕組みが必要。

### C. 対話フロー

```
$ exastro-cdk search nginx

検索結果 (3件):
  [1] ansible_role_OS-RH_setup_nginx       - Nginxのインストール・設定
  [2] ansible_role_OS-RH_setup_nginx_vhost - Nginx バーチャルホスト設定
  [3] ansible_role_OS-RH_setup_nginx_ssl   - Nginx SSL証明書設定

manifest.yaml に追記するMovementを選択してください (番号をカンマ区切りで入力, Enterでスキップ): 1,3

追記しました:
  movements:
    - name: ansible_role_OS-RH_setup_nginx
    - name: ansible_role_OS-RH_setup_nginx_ssl
```

### D. manifest.yaml への反映

選択したMovementを `manifest.yaml` の `movements` セクションへ追記します。既存の `movements` が存在する場合はリストに追加します。

```yaml
# 追記例
movements:
  - name: ansible_role_OS-RH_setup_nginx
  - name: ansible_role_OS-RH_setup_nginx_ssl
```

> **TODO:** 同じMovementが既に `movements` セクションに存在する場合の重複チェック・警告を実装するか確定する。

### E. オプション

| オプション | デフォルト | 説明 |
| :--- | :--- | :--- |
| `--tag` | なし | タグでフィルタリング |
| `--limit` | `20` | 表示件数の上限 |
| `--no-interactive` | `false` | 対話なしで検索結果一覧のみ出力（CI向け） |
| `--manifest` | `manifest.yaml` | 追記先マニフェストのパス |
| `--env-file` | なし | 接続情報を `.env` ファイルから読み込む |

---

## 3. How：実行フロー

```bash
# キーワード検索
$ exastro-cdk search nginx

# タグ絞り込み
$ exastro-cdk search --tag os-setup

# 対話なし（一覧表示のみ）
$ exastro-cdk search nginx --no-interactive
```

### 内部処理フロー

```
ITA API: ワークスペース内のMovement一覧を取得
    ↓
キーワード・タグでフィルタリング（ローカル処理）
    ↓
番号付きで結果一覧を表示
    ↓
ユーザーが追記するMovementを選択（--no-interactive の場合はここで終了）
    ↓
manifest.yaml の movements セクションへ追記
    ↓
追記内容をサマリ表示
```

---

## 4. 未決事項

| # | 項目 | 選択肢・論点 |
| :--- | :--- | :--- |
| 1 | 検索メタデータの取得元 | ITA APIのMovementレスポンスのみ vs playbook-collection-docs のREADME/YAMLヘッダをsidecarとして管理 |
| 2 | キャッシュ戦略 | Movement一覧をローカルにキャッシュして高速化するか、毎回APIを叩くか |
| 3 | タグの仕様 | ITAのMovementにタグフィールドが存在するか確認が必要 |
| 4 | 検索アルゴリズム | 前方一致・部分一致・あいまい検索のどれを採用するか |
| 5 | オフライン対応 | ITA接続なしでローカルのキャッシュだけで検索できるモードを持たせるか |
| 6 | `init` との連携 | `search` → Movement選択 → `init` を一連のフローとして統合する `scaffold` コマンドを将来的に設けるか |
