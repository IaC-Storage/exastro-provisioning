#!/bin/bash
# 1. SELinux & Firewall 停止 (検証用)
setenforce 0
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
systemctl stop firewalld
systemctl disable firewalld

# 2. Dockerインストール
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

# 3. ITA資材の取得 (v2.x 系の最新を想定)
mkdir -p /app/exastro
cd /app/exastro
# 本来はここで git clone または curl で docker-compose.yml を取得します
# 起動確認用のダミー: docker run -d -p 443:80 nginx (疎通テスト用)
