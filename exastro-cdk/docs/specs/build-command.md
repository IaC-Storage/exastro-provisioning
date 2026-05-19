# build コマンド仕様

## 1. Why：コマンドの目的と価値

テスト済みのカートリッジコンポーネントをITA標準のエクスポート形式（kymファイル）にパッケージングし、本番環境へのデリバリーを可能にすることが目的です。

* **再現性のある成果物**: `manifest.yaml` とAnsible Roleから決定論的にkymを生成し、環境依存の手動操作を排除します。
* **バリデーションゲート**: パッケージング前に最終バリデーションを実施し、不完全なカートリッジのリリースを防ぎます。
* **セルフサービスデリバリー**: 製品開発部門がSI工数なしで顧客へカートリッジを提供できる状態を作ります。

---

## 2. What：仕様の詳細

### A. kymファイルとは

ITA（Exastro IT Automation）が標準サポートするインポート/エクスポート形式のZIPアーカイブ。  
内部にConductor・Movement・ロールパッケージ・代入値設定・パラメータシートなどのリソース定義が含まれます。

> **TODO:** kymファイルの内部構造（ディレクトリレイアウト・各ファイルのフォーマット）をITA仕様から確認・記載する。

### B. パッケージング対象

| リソース | ソース |
| :--- | :--- |
| **Conductor定義** | ITA APIから取得 or `manifest.yaml` から生成 |
| **Movement定義** | ITA APIから取得 or `manifest.yaml` から生成 |
| **ロールパッケージ** | `ansible/roles/<name>/` をZIPアーカイブ化 |
| **パラメータシート定義** | `manifest.yaml` の変数定義から生成 |
| **代入値自動登録設定** | `manifest.yaml` から生成 |

> **TODO:** リソース取得元として「ITA APIから取得」と「manifest.yamlから生成」のどちらを正とするか確定が必要。ITA上の実態とのずれが生じうる。

### C. ビルド前バリデーション

`build` は以下を事前チェックします。

1. `verify` と同等のスキーマ検証
2. ITA上のリソースと `manifest.yaml` の整合性確認（`sync` 済みか）
3. 変数プレフィックス（`{role名}_{変数名}`）の全数チェック
4. Ansible Role構造の整合性（`tasks/main.yml`・`defaults/main.yml` の存在）

> **TODO:** `build` 実行前に `sync` 済みであることを強制するか、未sync状態でもビルド可能にするかを決定する。

### D. 出力

```
dist/
└── <conductor_name>-<version>.kym
```

バージョン番号の決定方法は未決定。

> **TODO:** バージョニング戦略を確定する（`manifest.yaml` への `version` フィールド追加 vs gitタグ vs 自動採番）。

### E. オプション

| オプション | デフォルト | 説明 |
| :--- | :--- | :--- |
| `--output` / `-o` | `dist/` | 出力先ディレクトリ |
| `--version` | 未定 | kymファイルのバージョンを明示指定 |
| `--manifest` | `manifest.yaml` | 対象マニフェストのパス |
| `--skip-verify` | `false` | ビルド前バリデーションをスキップ |

---

## 3. How：実行フロー

```bash
# 基本実行
$ exastro-cdk build

# 出力先を指定
$ exastro-cdk build --output ./release/

# バージョンを指定
$ exastro-cdk build --version 1.2.0
```

### 内部処理フロー

```
verify 実行（スキーマ・整合性チェック）
    ↓
ITA APIから現在のリソース定義を取得（sync済みチェック）
    ↓
ansible/roles/ 以下をZIPアーカイブ化
    ↓
kymファイル内部構造へ各リソースを配置
    ↓
ZIPパッケージング → dist/<name>-<version>.kym を出力
    ↓
ビルドサマリ表示（出力ファイルパス・含まれるリソース一覧）
```

---

## 4. 未決事項

| # | 項目 | 選択肢・論点 |
| :--- | :--- | :--- |
| 1 | kymファイル内部構造 | ITA仕様の確認が必要。`ita-api-reference.md` にエクスポートAPIが未記載 |
| 2 | リソース取得元 | ITA APIから取得 vs `manifest.yaml` からの生成（整合性の担保方法） |
| 3 | バージョニング | `manifest.yaml` への `version` フィールド追加・gitタグ・自動採番のどれか |
| 4 | sync前提の強制 | `build` 前に `sync` 済みであることを必須とするか任意にするか |
| 5 | パラメータシート生成 | 変数定義からパラメータシートのスキーマをどう生成するか（ITA固有フォーマット） |
| 6 | テスト用コンポーネントの除外 | `tests` セクションのシナリオやテスト用Conductorをkymから除外するか |
