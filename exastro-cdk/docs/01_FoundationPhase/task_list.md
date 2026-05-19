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
- [ ] 3-a. `ConductorModel` を `models/manifest.py` に定義
- [ ] 3-b. `manifest.yaml` に `conductor` ブロックのフィールドを反映 (`ManifestModel` 更新)
- [ ] 3-c. `ConductorResource.create()` の ITA API エンドポイント・ボディマッピングを実装
- [ ] 3-d. `conductor.py` の TODO を解消（`dict` から `ConductorModel` に型切り替え）
- [ ] 3-e. Movement先作成 → Conductor作成の依存関係制御を実装

### 4. `exastro-cdk sync` でConductor作成ができる

- [ ] 4-a. `cli/apply.py` に `sync` コマンドを実装
- [ ] 4-b. `engine.py` に `run_sync_process()` を実装（Movement → Conductor の順で ITA 登録）
- [ ] 4-c. 冪等性の初期対応（既存リソースのスキップ or 上書き判定）

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
