## 前提条件
- 対象ユーザ: 製品開発部門の開発者


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
