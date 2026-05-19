## 前提条件
- 対象ユーザ: 製品開発部門の開発者
- オーガナイゼーションは作成済みであること
- リフレッシュトークンは発行済みであること

### 環境変数

```bash
export EXASTRO_BASE_URL=https://your-exastro-instance
export EXASTRO_REFRESH_TOKEN=your_refresh_token
export EXASTRO_ORGANIZATION_ID=your_org_id
export EXASTRO_WORKSPACE_ID=your_workspace_id
```

---

## Exastro CDKを使った開発フロー

1. カートリッジ開発
   - 顧客へ提供する製品とその運用を支える運用管理ツールを自動提供する仕組みをExastroコンポーネント（カートリッジ）として開発する
   - 主コンポーネント: Ansible Playbook + パラメータシート定義（JSON）+ Conductor/Movement(JSON)
   - 追加コンポーネント: テスト用Conductor、Playbook、テストパラメータセット
   - 標準Playbook素材は `exastro-cdk search` でキーワード・タグ検索して再利用できる
2. 構文・スキーマ検証
   - `exastro-cdk verify` でマニフェストファイルの構文チェックとスキーマ検証を実施
   - 問題が検出された場合はマニフェストを修正してから次のステップへ進む
3. カートリッジ検証・テスト
   - `exastro-cdk sync` で開発したコンポーネント一式をExastroへ一括登録（差分適用）
   - `exastro-cdk test` でConductor/Movementを指定シナリオで実行し、正常終了することを確認
   - テスト実行結果・ステータスを確認し、失敗した場合はコンポーネントを修正して再実行
4. カートリッジ化
   - `exastro-cdk build` でマニフェストとITAコンポーネントをバリデーション後、Exastroのkymファイル（カートリッジ）として出力
5. 本番適用（サービス提供）
   - 本番環境のExastroでkymをインポートし、顧客固有のパラメータを入力して実行

---

## CLIコマンドインタフェース

| コマンド | 概要 | 機能 |
| :--- | :--- | :--- |
| **`exastro-cdk init`** | プロジェクト初期化 | マニフェストファイルの作成、マニフェストファイルベースの標準ディレクトリ構造の生成 |
| **`exastro-cdk sync`** | 定義と環境の同期 | REST APIを使ったリソース差分適用（create/update）、マニフェストファイルから削除されたリソースを自動削除（delete）、適用前の差分確認 |
| **`exastro-cdk verify`** | 検証 | マニフェストファイルの構文チェック及びスキーマ検証 |
| **`exastro-cdk test`** | テスト実行 | 指定したシナリオでのConductor/Movementの実行、テスト実行結果・ステータス表示 |
| **`exastro-cdk build`** | カートリッジ化 | マニフェストファイルとITAコンポーネントのバリデーション、ITA標準カートリッジ（kym）へのパッケージング |
| **`exastro-cdk search`** | 標準Playbook素材の検索 | 標準Playbook素材をキーワードやタグで検索・インポート |

---

## CLI開発サイクル

```
① manifest.yaml を記述  （必要に応じて exastro-cdk search で標準Playbookをインポート）
        ↓
② exastro-cdk init    ← Ansible Role雛形の生成 + ITA への Movement/Conductor 登録
        ↓
   [Role 開発: tasks/main.yml, defaults/main.yml を実装]
        ↓
③ exastro-cdk verify  ← マニフェストの構文チェック・スキーマ検証
        ↓
④ exastro-cdk sync    ← ロールパッケージのアップロード + 差分の同期（削除も含む）
        ↓
⑤ exastro-cdk test   ← 指定シナリオで Conductor/Movement を実行・結果確認
        ↓
⑥ exastro-cdk build  ← ITA標準カートリッジ（kym）へのパッケージング
        ↓
   本番環境へkymをインポートして適用
```

---

## 各コマンド詳細

### `init` — プロジェクト初期化

詳細仕様は [specs/init-command.md](specs/init-command.md) を参照してください。

**第1回実行:** `manifest.yaml` が存在しない場合、テンプレートを自動生成して終了。

```bash
$ exastro-cdk init
# → manifest.yaml を生成（編集してから再実行）
```

**第2回実行:** `manifest.yaml` の内容に基づいてローカルとExastro両側にリソースを展開。

```bash
$ exastro-cdk init
# ローカル: ansible/roles/<role_name>/ のディレクトリ構成を生成
# Exastro:  Movement を登録し、横一列の Conductor を自動作成
```

### `verify` — 事前検証

`manifest.yaml` の構文チェックとスキーマ検証を行います。`sync` や `build` の前に実行することで問題を早期に検出できます。

```bash
$ exastro-cdk verify
# → manifest.yaml のスキーマ検証・構文チェックを実行して結果を報告
```

### `sync` — 宣言的同期

`manifest.yaml` とExastro ITA上の実態の差分を検出し、作成・更新・削除を適用します。

```bash
$ exastro-cdk sync
```

リソースの操作順序（依存関係に従う）:

```
Movement 作成/更新
    ↓
ロールパッケージ アップロード
    ↓
Movement-ロール 紐付け（交差テーブル）
    ↓
Conductor 作成/更新
    ↓
代入値自動登録設定 更新
    ↓
マニフェストから削除されたリソースの自動削除（Pruning）
```

### `test` — テスト実行

指定したシナリオでConductor/Movementを実行し、結果・ステータスを確認します。

```bash
$ exastro-cdk test
# → Conductor/Movement を実行し、テスト結果とステータスをレポート出力
```

### `build` — カートリッジ化

検証済みのコンポーネントをITA標準カートリッジ（kymファイル）としてパッケージングします。

```bash
$ exastro-cdk build
# → マニフェストとITAコンポーネントをバリデーション後、kymファイルへパッケージング
```

### `search` — 標準Playbook素材の検索・manifest.yaml への追記

#### 前提: ワークスペースへの標準Playbookインポート

対象ワークスペースには、[exastro-suite/playbook-collection-docs](https://github.com/exastro-suite/playbook-collection-docs/tree/master/ansible_role_templates) の Ansible Playbook（ansible_role_templates）があらかじめインポートされていることを前提とします。

このPlaybookをITAへインポートすると、以下のリソースが自動生成されます。

| 生成リソース | 内容 |
| :--- | :--- |
| **Movement（Ansible Role）** | 各ロールテンプレートに対応した実行単位 |
| **Ansibleロールパッケージ** | ロールのZIPアーカイブ（ITA管理） |
| **パラメータシート** | ロールの変数に対応した入力シート |

> `manifest.yaml` は、インポート済みのMovementを組み合わせて構成を宣言するものです。現段階では自作Roleのアップロードは行わず、標準Playbookが提供するMovementを活用します。

#### コマンド概要

ワークスペース内のMovement一覧をキーワードやタグで検索し、対話形式で `manifest.yaml` に追記します。

```bash
$ exastro-cdk search <keyword>
```

#### 使用例

```bash
$ exastro-cdk search nginx

# 検索結果:
# [1] ansible_role_OS-RH_setup_nginx       - Nginxのインストール・設定
# [2] ansible_role_OS-RH_setup_nginx_vhost - Nginx バーチャルホスト設定
# [3] ansible_role_OS-RH_setup_nginx_ssl   - Nginx SSL証明書設定
#
# manifest.yaml に追記するMovementを選択してください (番号をカンマ区切りで入力, Enterでスキップ): 1,3
#
# → manifest.yaml の movements セクションへ選択したMovementを追記
```

#### manifest.yaml への反映方法

対話形式での追記のほか、検索結果を参考に `manifest.yaml` を直接編集することも可能です。

```yaml
# manifest.yaml（追記例）
movements:
  - name: ansible_role_OS-RH_setup_nginx
  - name: ansible_role_OS-RH_setup_nginx_ssl
```
