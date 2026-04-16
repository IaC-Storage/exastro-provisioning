# Exastro Provisioning

Terraformを使用してAzure上にExastro IT Automation (EITA) の検証環境を構築するためのリポジトリです。
REST APIを用いたコンポーネント（Movement/Conductor）作成の検証を目的としています。

## 📋 構成概要

* **Cloud:** Azure
* **Instance:** Standard_B2s (2 vCPU / 8GB RAM)
* **OS:** AlmaLinux 9 (x86_64)
* **Tools:** Terraform, Docker, Docker Compose
* **Target:** Exastro ITA v2.x

## 📁 ディレクトリ構成

```text
.
├── terraform/          # Azureインフラ定義 (VM, Network, Security Group)
├── scripts/            # ITAインストール用シェルスクリプト (userdata)
├── api_test/           # API検証用コード (Python/Bash etc.)
└── README.md
```

## 🚀 セットアップ手順

### 1. 事前準備 (M1 Mac)

#### 1.1 Azure CLI と Terraform のインストール

Azure CLIとTerraformがインストールされていることを確認してください。

```bash
# Azure CLI ログイン
az login

# SSHキーの作成 (未作成の場合)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_ita
```

#### 1.2 AlmaLinux 9 の使用承諾
Terraformを実行する前に次のコマンドで AlmaLinux 9 の使用承諾（Terms） を一度だけ行っておく必要があります。  
これを行わないと、`terraform apply` 時にエラーになります。

```bash
az vm image terms accept --publisher almalinux --offer almalinux-9 --plan 9_2-gen2
```

### 2. インフラ構築

`terraform/` ディレクトリへ移動し、変数を設定してデプロイします。

```bash
cd terraform
terraform init
terraform apply
```

> **Note:** デフォルトでは `Standard_B2s` を使用し、OSディスクを100GB割り当てています。
> 停止中もディスク料金が発生するため、長期間使用しない場合は `terraform destroy` を推奨します。

### 3. Exastro ITA へのアクセス

構築完了後、出力されたパブリックIPアドレスを使用してブラウザからアクセスします。

* **URL:** `https://<Public-IP>/`
* **Initial Login:** `admin` / `password` (構築直後はコンテナ起動まで数分かかります)

## 🛠 API検証の実行

`api_test/` 内のスクリプトを使用して検証を行います。
証明書は自己署名（オレオレ証明書）を使用しているため、検証をスキップする設定を有効にしています。

```bash
# 例: Movement一覧を取得する
curl -k -u "admin:password" \
     -X GET https://<Public-IP>/api/v2/organizations/<org_id>/workspaces/<ws_id>/ita/movements/
```

## 💰 コスト削減のための運用

本環境は以下の運用を想定した見積もり（月額 約3,500円）になっています。

1.  **作業時のみ起動:** 1日4時間 × 月20日稼働。
2.  **夜間停止:** `az vm deallocate` 等でインスタンスを停止。
    * *注意: 停止中もManaged Disk (100GB) の料金（約1,800円/月）は発生します。*
3.  **完全削除:** 検証が一段落したら `terraform destroy` で全リソースを削除。

## ⚠️ 注意事項

* **セキュリティ:** `main.tf` の `source_address_prefix` は、必ずご自身の現在のグローバルIPに制限してください。
* **OSイメージ:** AlmaLinux 9 を使用しています。Azure Marketplaceでのプラン使用承諾が必要な場合があります。

---

### ライセンス
Custom / Verification Use Only