# FOUNDATION_PHASE タスクリスト

## 現状サマリー

| コンポーネント | 状態 | 備考 |
|---|---|---|
| `exastro-cdk init` | 実装完了 | Movement 登録まで動作確認済み（単体テスト追加済み） |
| `movement.py` | 実装済み | `MovementResource.create()` 動作可能・単体テスト追加済み |
| `conductor.py` | スタブのみ | URL/ボディマッピング未実装、`ConductorModel`未定義 |
| `apply.py` (sync) | 空 | `app = typer.Typer()` のみ |

---

## タスクリスト

### 1. `exastro-cdk init` の完成 (仮実装 → 本実装)

- [x] 1-a. ITA初期登録を `engine.py` の `run_init_process` Step4 に実装（完了: PR #2）
- [x] 1-b. `ita_client.py` の `ITAClient` との接続確認・整合（完了: 単体テストで確認 PR #5）

### 2. `movement.py` の実装完成

- [x] 2-a. 学習用テスト (`tests/api/movement/`) をベースに `MovementResource` の動作検証（完了: `tests/unit/test_movement_resource.py` 追加 PR #5）
- [ ] 2-b. `movement_id` の返却対応（Conductor側で参照するため）

### 3. `conductor.py` の実装

- [ ] 3-a. 学習用テスト (`tests/api/conductor/`) を作成し、Conductor登録の動作検証環境を整備
- [ ] 3-b. `ConductorModel` を `models/manifest.py` に定義
- [ ] 3-c. `manifest.yaml` に `conductor` ブロックのフィールドを反映 (`ManifestModel` 更新)
- [ ] 3-d. `ConductorResource.create()` の ITA API エンドポイント・ボディマッピングを実装
- [ ] 3-e. `conductor.py` の TODO を解消（`dict` から `ConductorModel` に型切り替え）
- [ ] 3-f. Movement先作成 → Conductor作成の依存関係制御を実装

### 4. `exastro-cdk sync` でConductor作成ができる

- [ ] 4-a. `cli/apply.py` に `sync` コマンドを実装
- [ ] 4-b. `engine.py` に `run_sync_process()` を実装（Movement → Conductor の順で ITA 登録）
- [ ] 4-c. 冪等性の初期対応（既存リソースのスキップ or 上書き判定）

---

## 設計メモ

### Conductor の N Movement 対応方針

`manifest.yaml` は「1 Conductor + N Movements」構造を前提としている。
実装方針は **全 Movement を直列チェーンで繋いだ 1 Conductor を生成する**。

```
Start → Movement[0] → Movement[1] → ... → Movement[N-1] → End
```

ノード/エッジは Movement リストから動的生成する：

- `node-1`: start（out: terminal-1）
- `node-3` 〜 `node-(N+2)`: movement ノード（各 in/out terminal をインデックスから採番）
- `node-2`: end（in: terminal-2）
- `line-1` 〜 `line-(N+1)`: 隣接ノードを順番に接続
- X 座標はインデックス × オフセット（約 300px）で計算

`ConductorResource.create()` は単一 Movement ではなく `list[dict]` を受け取る設計に変更する。

**事前確認事項**: `orchestra_id` は Movement ごとに異なる可能性がある（Ansible Legacy Role=`"3"` など）。
`movement_list_*/filter` のレスポンスに含まれるか確認しておくと 3-d の実装がスムーズになる。

**着手順序**: 依存関係上、2-b（`movement_id` の返却対応）から始めるのが最短経路。

---

## 依存関係

```
3-a ConductorModel定義
    ↓
3-b ManifestModel更新  ←  2-b movement_id返却
    ↓
3-c ConductorResource実装
    ↓
3-e 依存関係制御
    ↓
4-b engine.run_sync_process()
    ↓
4-a cli/apply.py sync コマンド
```
