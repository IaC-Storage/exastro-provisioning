# Exastro Provisioning

Exastro IT Automation (EITA) の検証環境を自動構築するためのプロジェクトです。

*   **api-verification-environment**: Azure上にAlmaLinux 9 + Docker構成でEITA v2を構築します。REST APIを用いたMovementやConductorの操作検証を目的としています。

## 🛠 使用技術スタック

*   **Infrastructure:** Azure
*   **IaC:** Terraform
*   **OS:** AlmaLinux 9
*   **Automation:** Exastro IT Automation (v2.x)
*   **Container:** Docker, Docker Compose

## 🚀 はじめに

各プロジェクトのディレクトリ内に詳細な `README.md` が用意されています。構築や検証を行う際は、それぞれのディレクトリへ移動して手順を確認してください。

例: Exastro ITAの検証環境を構築する場合
```bash
cd exastro-provisioning/api-verification-environment
# READMEの手順に従って実行
```

## ⚠️ 注意事項

*   本リポジトリに含まれるコードは検証用です。本番環境で使用する場合は、セキュリティ設定（IP制限、パスワード管理、証明書など）を適切に見直してください。
*   クラウドのリソースをデプロイする場合、実行時間に応じた課金が発生します。不要になったリソースは速やかに削除することを推奨します。

---

### ライセンス
Custom / Verification Use Only