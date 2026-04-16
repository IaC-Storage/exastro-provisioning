#!/bin/bash

# ログ記録開始
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/stdout) 2>&1

echo "################################################"
echo "# Starting Exastro ITA Silent Installation"
echo "################################################"

# 1. 前提パッケージのインストールと設定 (AlmaLinux 9用)
dnf install -y git curl dnf-plugins-core
setenforce 0
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
systemctl stop firewalld
systemctl disable firewalld

# 2. Dockerのインストール (公式手順)
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

# 3. カーネルパラメータの設定 (重要)
sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" >> /etc/sysctl.conf

# 4. 公式セットアップスクリプトの取得
curl -Ssf https://ita.exastro.org/setup -o /tmp/setup.sh
chmod +x /tmp/setup.sh

# 5. サイレントインストールの実行
# 「sh /tmp/setup.sh install」に対して、対話的な回答を流し込む
# 質問順序（2026年時点のスクリプト構造に基づく）:
# - OASEデプロイ? (y)
# - GitLabデプロイ? (n)
# - パスワード自動生成? (y)
# - サービスURL? (http://<IP>:30080)  RHEL系は30080, それ以外は80
# - 管理URL? (http://<IP>:30081)     RHEL系は30081, それ以外は81
# - .env生成確認? (y)
# - 今すぐ起動? (y)

PUBLIC_IP=$(curl -s https://ifconfig.me/ip)

# 標準入力をシミュレートして実行
/tmp/setup.sh install <<EOF
y
n
y
http://${PUBLIC_IP}:30080
http://${PUBLIC_IP}:30081
y
y
EOF

echo "################################################"
echo "# Installation script submitted"
echo "################################################"
