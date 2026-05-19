# test コマンド仕様

## 1. Why：コマンドの目的と価値

`sync` でITAに登録したConductor/Movementが実際に期待通り動作するかを、本番環境に適用する前に検証することが目的です。

* **結合テストの自動化**: Conductor/Movementの実行をCLIから起動し、完了まで待機・結果を取得することで、Web UIを開かずにテストサイクルを回せます。
* **シナリオ駆動**: `manifest.yaml` にテスト用シナリオ（実行対象・入力パラメータ・期待ステータス）を定義し、再現性のあるテストを実現します。
* **CI連携**: `sync` → `test` をパイプラインに組み込み、マージ前に動作確認を自動化します。

---

## 2. What：仕様の詳細

### A. テストシナリオの定義

`manifest.yaml` の `tests` セクションにシナリオを記述します。

```yaml
# manifest.yaml（テストシナリオ例）
tests:
  - name: os_setup_smoke
    target:
      type: conductor          # conductor | movement
      name: main
    parameters:
      - sheet: os_setup_params
        host: test-host-01
        values:
          os_setup_ntp_server: "ntp.example.com"
    expect:
      status: completed        # completed | warning | error
      timeout_sec: 300
```

> **TODO:** `parameters` のスキーマ（シート名・ホスト・変数の渡し方）はITA APIの代入値設定に依存する。確定が必要。

### B. 実行フロー

1. テストシナリオに従いパラメータをITAへ設定
2. Conductor / Movementを実行
3. ポーリングで完了を待機
4. 実行結果（ステータス・ログURL）を取得・表示
5. `expect.status` と照合し、不一致なら exit code `1`

### C. 出力フォーマット例

```
Running scenario: os_setup_smoke
  Target: Conductor "main"
  Host: test-host-01
  ⏳ Waiting... (30s)
  ⏳ Waiting... (60s)
  ✔ Status: completed
  Log: https://your-exastro/ui/conductor/job/12345

Result: PASSED (1/1)
```

### D. オプション

| オプション | デフォルト | 説明 |
| :--- | :--- | :--- |
| `--scenario` | 全シナリオ | 実行するシナリオ名を指定（カンマ区切りで複数指定可） |
| `--timeout` | シナリオ定義値 | 完了待機タイムアウト（秒）をグローバルに上書き |
| `--manifest` | `manifest.yaml` | 対象マニフェストのパス |
| `--env-file` | なし | 接続情報を `.env` ファイルから読み込む |
| `--no-cleanup` | `false` | テスト後にITA上のパラメータ設定を削除しない |

> **TODO:** テスト実行後にITAへ設定したパラメータ（代入値）を自動クリーンアップするか、`--no-cleanup` で任意にするかを決定する。クリーンアップしない場合、次回テストへの影響を考慮する必要がある。

---

## 3. How：実行フロー

```bash
# 全シナリオ実行
$ exastro-cdk test

# 特定シナリオのみ実行
$ exastro-cdk test --scenario os_setup_smoke

# タイムアウトを上書き
$ exastro-cdk test --timeout 600
```

### 内部処理フロー

```
manifest.yaml の tests セクションを読み込む
    ↓
対象シナリオのフィルタリング（--scenario 指定時）
    ↓
シナリオごとに:
    ITA API: パラメータを代入値設定へ投入
        ↓
    ITA API: Conductor / Movement を実行開始
        ↓
    ポーリング: 完了 or タイムアウトまで待機
        ↓
    ITA API: 実行結果・ステータスを取得
        ↓
    expect.status と照合
        ↓
    （クリーンアップ: パラメータ設定を削除）
    ↓
全シナリオの結果サマリ出力
    ↓
1件以上失敗 → exit code 1
```

---

## 4. 未決事項

| # | 項目 | 選択肢・論点 |
| :--- | :--- | :--- |
| 1 | テストシナリオの定義場所 | `manifest.yaml` 内の `tests` セクション vs 別ファイル（例: `tests/scenarios.yaml`）|
| 2 | パラメータ投入方法 | ITA APIの代入値設定をどのエンドポイントで行うか（`ita-api-reference.md` と連動） |
| 3 | テスト専用ホスト | テスト実行用のホストをどう管理するか（`manifest.yaml` に記載 vs 環境変数） |
| 4 | クリーンアップ戦略 | テスト後に投入したパラメータ・作成したジョブ履歴をどこまで削除するか |
| 5 | 並列実行 | 複数シナリオを並列実行するか、直列実行のみにするか |
| 6 | ログ取得 | Conductor/Movementの実行ログをファイルへ保存するオプションを持たせるか |
