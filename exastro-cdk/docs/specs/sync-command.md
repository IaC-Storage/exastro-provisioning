# sync コマンド仕様

## 1. Why：コマンドの目的と価値

`manifest.yaml` を唯一の真実（SSOT）として、ITA上のリソース状態を宣言的に一致させることが目的です。

* **冪等性の保証**: 何度実行しても結果が同じになるように差分検出・適用を行います。
* **Pruning（削除の自動化）**: マニフェストから削除されたリソースをITA上からも自動削除し、「ゴミリソース」の蓄積を防ぎます。
* **GUI操作の排除**: Web UIを経由せずにコードベースでITAの状態管理を完結させます。

---

## 2. What：仕様の詳細

### A. 対象リソース

| リソース | 操作 |
| :--- | :--- |
| **Movement** | create / update / delete |
| **ロールパッケージ（ZIPアーカイブ）** | upload / 差し替え |
| **Movement-ロール紐付け（交差テーブル）** | create / update / delete |
| **Conductor** | create / update / delete |
| **代入値自動登録設定** | create / update / delete |

### B. 適用順序（依存関係に従う）

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

削除は依存関係の逆順で行います（Conductor → Movement-ロール紐付け → Movement）。

### C. 差分検出ロジック

1. ITA APIから現在のリソース一覧を取得
2. `manifest.yaml` の定義と突き合わせ
3. 差分を `CREATE` / `UPDATE` / `DELETE` / `NO_CHANGE` に分類
4. 適用前に差分サマリを表示し、`--yes` なしの場合は確認を求める

### D. オプション

| オプション | デフォルト | 説明 |
| :--- | :--- | :--- |
| `--dry-run` | `false` | 差分を表示するのみで実際の変更は行わない |
| `--yes` / `-y` | `false` | 確認プロンプトをスキップして自動適用 |
| `--manifest` | `manifest.yaml` | 対象マニフェストのパス |
| `--env-file` | なし | 接続情報を `.env` ファイルから読み込む |
| `--prune` | `true` | Pruning（削除）を有効にするか |

> **TODO:** `--prune=false` をデフォルトにして明示的に有効化させるか、`true` にして `--no-prune` で無効化させるか、UX観点で決定が必要。誤削除リスクを考慮すると `false` がより安全。

### E. 出力フォーマット（差分サマリ例）

```
Changes to apply:
  + Movement: os_setup (CREATE)
  ~ Movement: web_install (UPDATE: role変更)
  - Movement: old_task (DELETE)
  + Conductor: main (CREATE)

Apply 3 changes? [y/N]:
```

---

## 3. How：実行フロー

```bash
# 差分確認のみ（変更なし）
$ exastro-cdk sync --dry-run

# 確認プロンプトあり（通常実行）
$ exastro-cdk sync

# CI環境等で確認なしに適用
$ exastro-cdk sync --yes
```

### 内部処理フロー

```
verify を暗黙実行（エラー時は中断）
    ↓
ITA API: 現在のリソース状態を取得
    ↓
manifest.yaml との差分計算
    ↓
差分サマリ表示 → ユーザー確認（--yes の場合はスキップ）
    ↓
依存順に CREATE / UPDATE を適用
    ↓
Pruning: DELETE を逆依存順に適用
    ↓
適用結果サマリ出力
```

> **TODO:** `sync` が暗黙的に `verify` を呼ぶか、呼ばずに独立して実行するかを決定する。呼ぶ場合は `--skip-verify` オプションを用意するか検討。

---

## 4. 未決事項

| # | 項目 | 選択肢・論点 |
| :--- | :--- | :--- |
| 1 | Pruningのデフォルト | `--prune` を `true` / `false` どちらをデフォルトにするか（誤削除リスク vs 利便性） |
| 2 | `verify` の暗黙呼び出し | `sync` 前に自動で `verify` を実行するか、ユーザーに委ねるか |
| 3 | ロールバック戦略 | 途中でAPIエラーが発生した場合のロールバック方法（部分適用の扱い） |
| 4 | ステート管理 | ITA APIをSource of Truthとして毎回フル取得するか、ローカルにステートファイルを持つか |
| 5 | 代入値自動登録 | `manifest.yaml` でどのように定義するか（スキーマ未確定） |
