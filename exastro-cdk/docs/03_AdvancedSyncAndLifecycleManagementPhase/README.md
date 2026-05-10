# ADVANCED_SYNC_AND_LIFECYCLE_MANAGEMENT_PHASE

## 1. フェーズ目標

SYNCHRONIZATION_PHASEで実装した `sync`（作成・更新）を拡張し、**リソースの削除・テナント分離・差分の可視化**を実現することで、運用上の複雑さを排除して実用性を向上させる。

本フェーズの完了をもって、`manifest.yaml` がExastro ITA環境の**完全なSSOT（単一の真実）**として機能する状態を確立する。

### 対象スコープ
| 機能 | 内容 |
| :--- | :--- |
| **Pruning機能** | 定義から削除されたリソースをExastro環境から安全に削除 |
| **Workspaceの分離** | 開発者ごとのテナント分離で `sync` 時の干渉を防止 |
| **`diff` コマンド** | 定義ファイルと現在の環境状態の差分をドライラン表示 |

---

## 2. Pruning機能の設計

### 2.1 概要

`manifest.yaml` からMovementやConductorの定義を削除した後に `sync` を実行した際、Exastro ITA上の対応するリソースを**安全に削除**する機能。

### 2.2 安全削除のための設計方針

誤削除を防ぐため、以下のガードを設ける。

| ガード | 内容 |
| :--- | :--- |
| **ドライランデフォルト** | `--prune` フラグを明示しない限り削除は実行しない |
| **依存関係チェック** | 削除対象リソースが他のリソースから参照されている場合は警告・中断 |
| **確認プロンプト** | 削除実行前に対象リストを表示し、ユーザー確認を求める |

### 2.3 Pruning実行フロー

```
$ exastro-cdk sync --prune
```

1. current state（Exastro ITA上の全リソース）を取得する。
2. desired state（`manifest.yaml` 定義）と比較し、定義に存在しないリソースを特定する。
3. 削除候補リストを表示し、確認を求める。
4. 承認後、依存関係の逆順（Conductor → Movement の順）で削除APIを実行する。

---

## 3. Workspace分離設計

### 3.1 課題

複数の開発者が同一のExastro環境に対して `sync` を実行すると、互いのリソースを上書き・削除し合うリスクがある。

### 3.2 分離戦略

`manifest.yaml` にWorkspace IDを明示し、`sync` の操作スコープをそのWorkspaceに限定する。

```yaml
# manifest.yaml
workspace:
  id: dev-nakagawa     # 開発者ごとにユニークなWorkspace ID
  organization_id: my-org

conductor:
  name: os-setup-conductor
  ...
```

- Workspace IDが異なれば、`sync` / `prune` の影響範囲は完全に分離される。
- CI/CD環境では環境変数で `EXASTRO_WORKSPACE_ID` を上書きできるようにする。

---

## 4. `diff` コマンド設計

### 4.1 概要

`sync` を実行する前に、何が変更されるかを**ドライランとして可視化**するコマンド。

```
$ exastro-cdk diff
```

### 4.2 出力イメージ

```
~ Movement: os_setup
    host_group: linux_servers → linux_all

+ Movement: apache_install    (新規作成)

- Movement: old_movement      (削除予定 ※ --prune 時のみ)

Conductor: os-setup-conductor (変更なし)
```

凡例:
- `+` : 新規作成
- `~` : 変更あり
- `-` : 削除（`--prune` 指定時のみ表示）
- スペース: 変更なし

### 4.3 実装方針

- `sync` の差分算出ロジックを再利用し、APIへの書き込みを省略した読み取り専用モードとして実装する。
- 出力フォーマットは `--output json` オプションでJSON形式にも対応し、CI/CDでの機械的な処理に備える。

---

## 5. 実装アイテムリスト

### 5.1 Pruning機能
- `sync --prune` フラグの実装。
- 削除対象リソースの特定ロジック（current - desired の差分）。
- 依存関係チェック（削除前の参照確認）。
- 削除確認プロンプトおよびフォースオプション（`--yes`）の実装。
- 削除API（Movement / Conductor）のラッパー実装。

### 5.2 Workspace分離
- `manifest.yaml` の `workspace` フィールドのスキーマ追加。
- `sync` / `prune` 操作のWorkspaceスコープ制限。
- 環境変数による Workspace ID 上書き機能。

### 5.3 `diff` コマンド
- `exastro-cdk diff` コマンドのエントリポイント実装。
- 差分の人間可読フォーマット出力。
- `--output json` オプションによるJSON出力。
- `--prune` フラグとの組み合わせ（削除対象の差分も表示）。

---

## 6. 完了条件 (Exit Criteria)

1. `exastro-cdk sync --prune` を実行すると、`manifest.yaml` から削除されたリソースがExastro ITAから安全に削除される。
2. 誤削除ガード（確認プロンプト・依存関係チェック）が機能する。
3. 異なる `workspace.id` を持つ `manifest.yaml` の `sync` が互いに干渉しない。
4. `exastro-cdk diff` を実行すると、`sync` 前の変更内容がコンソールに表示される。
5. `diff` 実行後にExastro ITAの状態が変化していない（副作用なし）。

---

**Prerequisite:** SYNCHRONIZATION_PHASEの完了条件をすべて満たしていること。  
**Next Step:** バリデーション・テスト自動化の設計（VALIDATION_AND_TEST_PHASEへ）。
